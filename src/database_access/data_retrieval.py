import pyodbc
from dotenv import load_dotenv
import os

' ###### establishing connection #################'

def establish_database_connection():
    cloud_usage = True
    if cloud_usage:
        try:
            ' ######### load environment variables, get azure sql-db admin credentials #####'
            load_dotenv(dotenv_path="../../.env")
            azure_db_admin =  os.getenv("SQL_DB_ADMIN")
            azure_db_admin_pwd = os.getenv("SQL_DB_ADMIN_PWD")
            ' ###################### connection parameters ####################'
            server = r'bird-paradise-db-server.database.windows.net'
            database = 'bird_paradise_sqldatabase' # "birds_paradise_SQL_dev" # 'ProjektarbeitPP'
            username = azure_db_admin
            password = azure_db_admin_pwd
            driver = '{ODBC Driver 17 for SQL Server}'

            ' ############### open connection ###########################'
            connection_string = f"""
                    DRIVER={driver};
                    SERVER={server};
                    DATABASE={database};
                    UID={username};
                    PWD={password};
                    Encrypt=yes;
                    TrustServerCertificate=no;""" #                     TrustServerCertificate=no;
            connection = pyodbc.connect(connection_string)
            print("Connection succesfully established")
        except pyodbc.Error as e:
            print("Connection error: ", e)
        return connection
    else:
        try:
            ' ###################### connection parameters ####################'
            server = r'DESKTOP-5S013HL\SQL2022EXPRESS'
            database = 'ProjektarbeitPP'
            driver = '{ODBC Driver 17 for SQL Server}'

            ' ############### open connection ###########################'
            connection_string = f"""
                    DRIVER={driver};SERVER={server};DATABASE={database};Trusted_Connection=yes"""
            connection = pyodbc.connect(connection_string)
            print("Connection succesfully established")
        except pyodbc.Error as e:
            print("Connection error: ", e)
        return connection


' ################### function to exec queries/procedures ################'
def make_query(input_query, connection, procedure = False, params=None):
    try:
        # set cursor
        cursor = connection.cursor()
        # call procedure with params (or no params) or execute raw query
        if procedure:
            if params:
                cursor.execute(input_query, *params)
            else:
                cursor.execute(input_query)
        else: 
            cursor.execute(input_query)

        # if query is reading, cursor.description is not None
        if cursor.description:
            # extract column names of retrieved results
            column_names = [column[0] for column in cursor.description]
            # extract all rows of retrieved results
            rows = cursor.fetchall()
            # convert rows to list of dictionaries
            results = [dict(zip(column_names, row)) for row in rows]
            return results
        # if query is writing, cursor.description is None
        else:
            # query is writing. Check, if OUTPUT-Statement returns results
            try:
                rows = cursor.fetchall()
                if rows:
                    column_names = [column[0] for column in cursor.description]
                    results = [dict(zip(column_names, row)) for row in rows]
                    connection.commit()
                    return results
            except:
                # no fetchable result set. Just commit and return success message
                connection.commit()
                return {"status": "success", "message": "Query executed, no data returned."}
    except Exception as e:
        print(f"Error during execution of sql-query:\n{e}")
        return None