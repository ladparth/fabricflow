import pytest
from fabricflow.copy.utils import extract_schema_table


@pytest.mark.parametrize(
    "sql, expected",
    [
        ("SELECT * FROM mydb.mytable", ("mydb", "mytable")),
        ("SELECT * FROM mytable", (None, "mytable")),
        (
            "SELECT * FROM non_existing_db.non_existing_table",
            ("non_existing_db", "non_existing_table"),
        ),
        (
            "SELECT [BusinessEntityID], [PersonType], [NameStyle], [Title], [FirstName], [MiddleName], [LastName], [Suffix], [EmailPromotion], [AdditionalContactInfo], [Demographics], [rowguid], [ModifiedDate] FROM [Person].[Person]",
            ("Person", "Person"),
        ),
    ],
)
def test_extract_schema_table(sql, expected):
    assert extract_schema_table(sql) == expected
