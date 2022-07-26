"""
General Operations Functions
----------------------------

Contains general functions (including CRUD functions)
"""
from contextlib import closing
from typing import Union, Iterable
import sqlite3

# Database filename
DATABASE = r"database.db"


def execute_db(query: str, parameters=None, fetchone=False) -> Union[list[tuple], tuple, None]:
    """ Execute sql query with parameters """

    # Ensure that query statement ends properly
    assert query.strip().endswith(";"), 'Must end SQL query with ";"'

    # Use with statement to ensure proper closing of file
    with closing(sqlite3.connect(DATABASE)) as connection:
        with connection:

            # Cursor for executing queries
            cursor = connection.cursor()

            # Execute parameterised queries
            retrieved = cursor.execute(query, parameters)

            if fetchone:
                data = retrieved.fetchone()
            else:
                data = retrieved.fetchall()

            # Return fetched data (if any)
            return data

    # Code should never reach here, raise error just in case
    raise RuntimeError("Unknown critical error!")


def retrieve_db(table: str, columns: Iterable=None, or_and: int=0, limit: int=0, offset: int=0, fetchone=False, **attributes) -> Union[list[tuple], tuple, None]:
    """
    Retrieve rows from table

    Args:
        table (str): Table to be retrieved.
        columns (:obj:`Iterable`, optional): Columns to be projected.
        or_and (:obj:`int`, optional): 0 for OR, 1 for AND.
        limit (:obj:`int`, optional): Limits the number of rows retrieved
        offset (:obj:`int`, optional): Offset of index to start retrieving from
        fetchone (:obj:`bool`, optional): Fetches one row only if set to True
        **attributes: Attributes to be selected.

    Returns:
        list[tuple] | tuple | None: Data retrieved
    """

    # Default values of statements
    projection = "*"   # Project all columns
    selection = ""     # No selection options
    limit_offset = ""  # No limit

    if columns:  # If columns were specified

        # Construct projection statement
        projection = ",".join(columns)

    if attributes:  # If attributes were specified

        # Selection statements
        selection = []

        # Loop through attributes and add parameterised statements
        for attribute in attributes:
            selection.append(f"{attribute} = ?")

        # Join statements with "OR"/"AND" if more than one
        selection = " WHERE " + (" OR ", " AND ")[or_and].join(selection)

    if limit:  # If limits were specified

        # Limits and offsets should be positive
        assert limit >= 0, "Limit should be a int more than 0"
        assert offset >= 0, "Offset should be a int more than 0"

        limit_offset = f" LIMIT {int(limit)} OFFSET {int(offset)}"

    # Create query
    query = f"""SELECT {projection} FROM {table} {selection} {limit_offset};"""

    # Fetch and return results of the query
    return execute_db(query, tuple(attributes.values()), fetchone)


def insert_row(table: str, values: Iterable, columns: Iterable[str]=None) -> None:
    """ Inserts new row with values into, columns of table """

    # Values shouldn't be empty
    if not values:
        raise ValueError("Must specify at least one value to be inserted")

    # Generate question marks used for parameterised query
    question_marks = ",".join("?"*len(values))

    # Format column names (default nothing)
    column_names = f"({','.join(columns)})" if columns else ""

    # Format query statement
    query = f"""INSERT INTO {table} {column_names} VALUES ({question_marks});"""

    # Execute parameterised SQL query 
    execute_db(query, values)


def delete_rows(table: str, or_and: int=0, **attributes) -> None:
    """ Deletes rows from table """

    # At least one attribute needs to be specified
    if not attributes:
        raise TypeError("Must specify at least one attribute")

    # Selection statements
    selection = []

    # Loop through attributes and add parameterised statements
    for attribute in attributes:
        selection.append(f"{attribute} = ?")

    selection = (" OR ", " AND ")[or_and].join(selection)

    # Format query statement
    query = f"""DELETE FROM {table} WHERE {selection};"""

    # Execute parameterised query
    execute_db(query, tuple(attributes.values()))


def update_rows(table: str, columns: Iterable[str], values: Iterable, or_and: int=0, **attributes) -> None:
    """ Updates rows of table """

    # At least one column should be updated
    if not columns:
        raise ValueError("Must specify at least column to be updated")

    # Each column needs a corresponding value
    elif len(columns) != len(values):
        raise ValueError("Columns and values must be of same length")

    # At least one attribute needs to be specified
    elif not attributes:
        raise TypeError("Must specify at least one attribute")

    # Format columns
    temp = []  # Temp 
    for column in columns:
        temp.append(f"{column} = ?")
    columns_str = ",".join(temp)

    # Selection statements
    selection = []
    # Loop through attributes and add parameterised statements
    for attribute in attributes:
        selection.append(f"{attribute} = ?")
    selection = (" OR ", " AND ")[or_and].join(selection)

    query = f"""UPDATE {table} SET {columns_str} WHERE {selection};"""

    params = tuple(values) + tuple(attributes.values())

    execute_db(query, params)
