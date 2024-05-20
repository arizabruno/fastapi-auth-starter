from app.auth.password import get_password_hash
from app.data_access.db_connection import Database
import pandas as pd



def execute_query(query, params=None, fetch="all", commit=False):
    """
    Executes a given SQL query with optional parameters and manages the database connection.
    Returns the results as a list of dictionaries after transforming them into a pandas DataFrame,
    with column names corresponding to the SQL table columns.

    Parameters:
    - query (str): The SQL query to execute.
    - params (tuple|dict|None): Optional parameters to pass with the query. Default is None.
                                If provided, it should be a tuple or dict of parameters you wish to bind to the query.
    - fetch (str): Determines how the results are fetched post-query execution. Default is "all".
                   Acceptable values are:
                   - "all": Fetches all rows of a query result, returns a list of dictionaries.
                   - "one": Fetches the first row of a query result, returns a list containing a single dictionary.
    - commit (bool): Specifies whether to commit the transaction. Default is False.
                     If True, the changes made by the query will be committed to the database.

    Returns:
    - On successful execution and fetch="all" or fetch="one", returns a list of dictionaries representing the fetched rows.
    - On successful execution with commit=True, returns True.
    - If an exception occurs during query execution, prints the error and returns None.
    """
    connection = Database.get_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute(query, params)
            if fetch == "one" and commit:
                connection.commit()
                rows = [cursor.fetchone()]
                print(rows)
                if not rows or rows[0] is None:  # Check if no data was fetched or fetchone() found no rows
                    return []  # Return an empty list
                col_names = [desc[0] for desc in cursor.description]
                df = pd.DataFrame(rows, columns=col_names)
                return df.to_dict('records')
            if commit:
                connection.commit()
                return True
            if fetch in ("all", "one"):
                rows = cursor.fetchall() if fetch == "all" else [cursor.fetchone()]
                if not rows or rows[0] is None:  # Check if no data was fetched or fetchone() found no rows
                    return []  # Return an empty list
                col_names = [desc[0] for desc in cursor.description]
                df = pd.DataFrame(rows, columns=col_names)
                return df.to_dict('records')  # Convert DataFrame to list of dicts
    except Exception as e:
        print(f"An error occurred: {e}")
        return None
    finally:
        Database.return_connection(connection)



def create_user(email: str, username: str, password: str):
    """
    Adds a new user to the database with a hashed password.

    Args:
        username (str): The user's username.
        password (str): The user's plain text password, which will be hashed before storage.
        email (str): The user's email address.

    Returns:
        Union[dict, None]: The newly created user's data, or None if an error occurred.
    """
    hashed_password = get_password_hash(password)
    query = """
    INSERT INTO users (email, username, hashed_password) VALUES (%s, %s, %s)
    """
    params = (email, username, hashed_password)
    return execute_query(query, params=params, commit=True)


def read_all_users():
    """
    Fetches all users from the users table without exposing sensitive information like hashed passwords.

    Returns:
    - The result of the `execute_query` function, which is a list of dictionaries where each dictionary represents a user without their hashed password.
    """
    query = "SELECT user_id, email, username, roles FROM users"
    return execute_query(query, fetch="all")


def read_user_by_id(user_id: int):
    """
    Fetches a single user from the users table by their ID.

    Parameters:
    - user_id (int): The ID of the user to fetch.

    Returns:
    - A list containing a single dictionary representing the user, or an empty list if no user was found. Sensitive information like hashed passwords is not included.
    """
    query = "SELECT user_id, email, username, roles FROM users WHERE user_id = %s"
    params = (user_id,)
    return execute_query(query, params=params, fetch="one")[0]




def update_user_info(user_id: int, new_email: str = None, new_username: str = None, new_password: str = None):
    """
    Updates the information of an existing user in the users table based on their ID.

    Parameters:
    - user_id (int): The ID of the user to update.
    - new_email (str, optional): The new email address to update.
    - new_username (str, optional): The new username to update.
    - new_passowrd (str, optional): The new password to update.

    Returns:
    - The result of the `execute_query` function, which could be True if the operation was successful and the transaction was committed, or None if an error occurred.
    """
    updates = []
    params = []

    if new_email:
        updates.append("email = %s")
        params.append(new_email)
    if new_username:
        updates.append("username = %s")
        params.append(new_username)
    if new_password:
        new_hashed_password = get_password_hash(new_password)
        updates.append("hashed_password = %s")
        params.append(new_hashed_password)

    if not updates:
        return None  # No updates to make

    params.append(user_id)  # For the WHERE clause
    query = "UPDATE users SET " + ", ".join(updates) + " WHERE user_id = %s"

    return execute_query(query, params=params, commit=True)


def delete_user(user_id: int):
    """
    Deletes a user from the users table using their ID.

    Parameters:
    - user_id (int): The ID of the user to be deleted.

    Returns:
    - The result of the `execute_query` function, which could be True if the operation was successful and the transaction was committed, or None if an error occurred.
    """
    query = "DELETE FROM users WHERE user_id = %s"
    params = (user_id,)
    return execute_query(query, params=params, commit=True)


def read_user_by_username(username: str):
    """
    Fetches a single user from the users table by their username.

    Parameters:
    - username (str): The username of the user to fetch.

    Returns:
    - A list containing a single dictionary representing the user, or an empty list if no user was found. Sensitive information like hashed passwords is not included.
    """
    query = "SELECT user_id, email, username, hashed_password, roles FROM users WHERE username = %s"
    params = (username,)
    return execute_query(query, params=params, fetch="one")[0]

def read_user_by_email(email: str):
    """
    Fetches a single user from the users table by their email.

    Parameters:
    - email (str): The email of the user to fetch.

    Returns:
    - A list containing a single dictionary representing the user, or an empty list if no user was found. Sensitive information like hashed passwords is not included.
    """
    query = "SELECT user_id, email, username, hashed_password, roles FROM users WHERE email = %s"
    params = (email,)
    return execute_query(query, params=params, fetch="one")[0]
