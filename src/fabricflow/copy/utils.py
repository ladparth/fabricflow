import sqlglot
import logging

logger = logging.getLogger(__name__)


def extract_schema_table(sql: str) -> tuple[str | None, str | None]:
    """
    Extracts the schema and table name from a given SQL query using sqlglot.

    Args:
        sql: The SQL query string.

    Returns:
        A tuple containing (schema_name, table_name).
        Returns (None, None) if parsing fails or no table is found.
    """
    logger.debug("Attempting to extract schema and table from SQL: '%s'", sql)
    try:
        # Parse the SQL query using sqlglot with T-SQL dialect.
        parsed = sqlglot.parse_one(sql, read="tsql")

        # Find the first Table expression in the parsed SQL.
        table = next(parsed.find_all(sqlglot.expressions.Table), None)

        if table is None:
            logger.warning("No primary table expression found in SQL: '%s'", sql)
            return None, None

        # Extract schema and table name using the .db and .name properties.
        schema = table.db
        table_name = table.name

        # The .db property can return an empty string if no schema is specified.
        if schema == "":
            schema = None

        logger.info(
            "Successfully extracted schema: '%s', table: '%s' from SQL.",
            schema,
            table_name,
        )
        return schema, table_name

    except sqlglot.errors.ParseError as e:
        logger.error("Failed to parse SQL query: '%s'. Error: %s", sql, e)
        return None, None
    except Exception as e:
        # Catch any other unexpected errors during processing
        logger.critical(
            "An unexpected error occurred during schema/table extraction for SQL: '%s'. Error: %s",
            sql,
            e,
        )
        return None, None


def extract_copy_activity_info(activity_results):
    logger.debug("Extracting copy activity info from results")
    extracted_data = []
    activities = (
        activity_results.get("value", activity_results)
        if isinstance(activity_results, dict)
        else activity_results
    )
    logger.debug("Processing %d activities", len(activities))
    for idx, activity in enumerate(activities):
        logger.debug("Processing activity %d: %s", idx, activity)
        info = {
            "copy_status": activity.get("status"),
            "copy_activity_run_start": activity.get("activityRunStart"),
            "copy_activity_run_end": activity.get("activityRunEnd"),
            "copy_activity_duration": activity.get("durationInMs"),
            "copy_activity_output": activity.get("output"),
        }

        sql_query = activity.get("input", {}).get("source", {}).get("sqlReaderQuery")
        info["copy_activity_sql_query"] = sql_query

        if sql_query:
            logger.debug(
                "Extracting schema and table for SQL query in activity %d", idx
            )
            info["source_schema"], info["source_table_name"] = extract_schema_table(
                sql_query
            )
        else:
            logger.info("No SQL query found in activity %d", idx)

        extracted_data.append(info)
    logger.info("Extracted info for %d activities", len(extracted_data))
    return extracted_data
