import logging
import sqlite3


class DatabaseHelper:
    def __init__(self, path_to_db="data/database.db"):
        self.path_to_db = path_to_db

    @property
    def connection(self):
        return sqlite3.connect(self.path_to_db)

    def execute(self, sql: str, parameters: tuple = None, fetchone=False,
                fetchall=False, commit=False):
        if not parameters:
            parameters = tuple()
        connection = self.connection
        connection.set_trace_callback(db_logs)
        cursor = connection.cursor()
        try:
            cursor.execute(sql, parameters)
        except Exception as err:
            connection.close()
            return err

        data = None

        if commit:
            connection.commit()

        if fetchone:
            data = cursor.fetchone()

        if fetchall:
            data = cursor.fetchall()

        connection.close()
        return data

    def create_table_users(self):
        sql = """
        CREATE TABLE IF NOT EXISTS Users (
        id int NOT NULL,
        Username varchar(255),
        chat_from varchar(255),
        msg_id_chat_from int,
        access_hash int,
        status int,
        PRIMARY KEY (id)
        );
        """
        return self.execute(sql, commit=True)

    def add_user(self, user_id: int, username: str, chat_from: str,
                 msg_id_chat_from: int, access_hash: int, status: bool = False):
        sql = ("INSERT INTO Users(id, Username, chat_from, msg_id_chat_from, access_hash, status) "
               "VALUES (?, ?, ?, ?, ?, ?)")
        parameters = (user_id, username, chat_from, msg_id_chat_from, access_hash, status)
        return self.execute(sql, parameters=parameters, commit=True)

    def update_user(self, user_id: int, username: str, chat_from: str,
                    msg_id_chat_from: int, access_hash: int, status: bool = False):
        sql = ("UPDATE Users SET (Username, chat_from, msg_id_chat_from, access_hash, status) = "
               "(?, ?, ?, ?, ?) WHERE id = ?")
        parameters = (username, chat_from, msg_id_chat_from, access_hash, status, user_id)
        return self.execute(sql, parameters=parameters, commit=True)

    def update_user_status_db(self, user_id: int, new_status: bool):
        sql = f"UPDATE Users SET status = ? WHERE id = ?"
        parameters = (int(new_status), user_id)
        return self.execute(sql, parameters=parameters, commit=True)

    def null_all_users(self):
        sql = f"UPDATE Users SET status = 0"
        return self.execute(sql, commit=True)

    def select_all_users(self):
        sql = "SELECT * FROM Users"
        return self.execute(sql, fetchall=True)

    def select_user(self, **kwargs):
        sql = "SELECT * FROM Users WHERE "
        sql, parameters = self.format_args(sql, kwargs)
        return self.execute(sql, parameters, fetchone=True)

    def count_users(self):
        return self.execute("SELECT COUNT (*) FROM Users;", fetchone=True)

    def delete_users(self):
        sql = "DELETE FROM Users"
        return self.execute(sql, commit=True)

    def create_table_admins(self):
        sql = """
                CREATE TABLE IF NOT EXISTS Admins (
                admin_id int NOT NULL,
                message_id int,
                PRIMARY KEY (admin_id)
                );
                """
        return self.execute(sql, commit=True)

    def add_admin(self, admin_id, message_id):
        sql = "INSERT INTO Admins(admin_id, message_id) VALUES (?, ?)"
        parameters = (admin_id, message_id)
        return self.execute(sql, parameters=parameters, commit=True)

    def update_message_id_of_admin(self, admin_id: int, new_message_id: int):
        sql = f"UPDATE Admins SET message_id = ? WHERE admin_id = ?"
        parameters = (new_message_id, admin_id)
        return self.execute(sql, parameters=parameters, commit=True)

    def get_admin(self, admin_id):
        sql = "SELECT * FROM Admins WHERE admin_id = ?"
        parameters = (admin_id, )
        return self.execute(sql, parameters, fetchone=True)

    @staticmethod
    def format_args(sql, parameters: dict):
        sql += " AND ".join([
            f"{item} = ?" for item in parameters
        ])
        return sql, tuple(parameters.values())


def db_logs(statement):
    logging.info(f"""
Executing: {statement}
""")
