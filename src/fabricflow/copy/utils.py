from sqlglot.expressions import Table
from sqlglot.expressions import Expression
import sqlglot
import logging
from logging import Logger

logger: Logger = logging.getLogger(__name__)


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
        parsed: Expression = sqlglot.parse_one(sql, read="tsql")

        table: Table | None = next(parsed.find_all(Table), None)

        if table is None:
            logger.warning("No primary table expression found in SQL: '%s'", sql)
            return None, None

        schema: str | None = table.db
        table_name: str | None = table.name

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
        logger.critical(
            "An unexpected error occurred during schema/table extraction for SQL: '%s'. Error: %s",
            sql,
            e,
        )
        return None, None


def extract_copy_activity_info(activity_results) -> list[dict] | None:
    logger.debug("Extracting copy activity info from results")

    extracted_data: list[dict] = []

    activities: list[dict] = (
        activity_results.get("value", activity_results)
        if isinstance(activity_results, dict)
        else activity_results
    )

    logger.debug("Processing %d activities", len(activities))

    for idx, activity in enumerate(activities):
        logger.debug("Processing activity %d: %s", idx, activity)
        info: dict[str, str | dict | None] = {
            "copy_status": activity.get("status", None),
            "copy_activity_run_start": activity.get("activityRunStart", None),
            "copy_activity_run_end": activity.get("activityRunEnd", None),
            "copy_activity_duration": activity.get("durationInMs", None),
            "copy_activity_output": activity.get("output", None),
        }

        sql_query: str | None = (
            activity.get("input", {}).get("source", {}).get("sqlReaderQuery", None)
        )

        if sql_query:
            info["copy_activity_sql_query"] = sql_query

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
