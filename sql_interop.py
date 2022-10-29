# Database related functionality.

# Initialize logging.
import logging
sqlLogger = logging.getLogger(__file__)

# Connect to a sqlite database file.
def databaseConnection(config):

    # Module Imports
    import mariadb
    import sys

    # Connect to MariaDB Platform
    try:
        sqlConnection = mariadb.connect(
            host = config["database"]["host"]
          , user = config["database"]["user"]
          , unix_socket = config["database"]["socket"]
          , database = config["database"]["schema"]
        )
    except mariadb.Error as e:
        print(f"Error connecting to MariaDB Platform: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Error connecting to MariaDB Platform: {e}")
        sys.exit(1)

    # Report the successful connection to the database to the log file.
    sqlLogger.info("Database connection established.")

    return sqlConnection


# Function to determine primary key of table.
def getPrimaryKey(sqlConnection, table):
    # Get the id field value for the passed.
    tableInfo = fetchData(
          sqlConnection
        , f"SHOW KEYS FROM `{table}` WHERE Key_name = 'PRIMARY'"
    )

    # What is the name of the primary key?
    try:
        primaryKey = tableInfo[0]["Column_name"]
    except Exception as e:
        print(f"Could not determine the primary key for {table}, {e}")
        return 1   # End function with error 1.

    return primaryKey


# Get all columns which can't be null except primary key.
def getAllMandatory(sqlConnection, table):

    import sql_interop as si  # For querying the database.

    # Execute statement / query.
    # TODO: This entire function is more or less redundant. But the query
    # below behaves strangely. Can't WHERE to Null = NO or 0 or False …
    allNonNull = si.fetchData(sqlConnection, f"SHOW COLUMNs FROM `{table}`")

    # Also get primary key.
    try:
        primaryKey = getPrimaryKey(sqlConnection, table)
    except Exception as e:
        print(f"Couldn't determine primary key for {table}, {e}")
        return -1

    # Try to extract a list.
    try:
        mandatories = [d["Field"] for d in allNonNull if d["Null"] == "NO"]
    except Exception as e:
        print(f"Couldn't exract mandatory fields from {table}, {e}")


    # Remove primary key from mandatories.
    mandatories.pop(mandatories.index(primaryKey))

    # End of regular execution.
    return mandatories



# Get the id of a dataset identified by
# unique pairs of fields / keys and values.
def getId(sqlConnection, table, stringIdentifiers):

    # Retrieve the column name of the primary key in "table".
    primaryKey = getPrimaryKey(sqlConnection, table)

    # Build where clause:
    wheres = [
        x + " = \'" + stringIdentifiers[x] + "\'" for x in stringIdentifiers
    ]
    whereClause = " AND ".join(wheres)

    # Find the id of the required dataset in the detail table.
    idDetail = si.fetchData(
        sqlConnection
      , "SELECT " + primaryKey
            + " FROM " + table
            + " WHERE " + whereClause
    )

    if len(idDetail) == 1:
        return idDetail[0][primaryKey]
    else:
        raise ValueError(
            "Expected one result row but got " + str(len(idDetail))
        )


 
# Build a query string from an sql file.
def buildQueryString(SQLFile, replacements = {}):
  with open(SQLFile, "r") as openedSQLFile:
    queryList = openedSQLFile.readlines()
  
  queryString = "".join(queryList)

  # Put in actual values for placeholders.
  queryString = queryString.format(**replacements)

  return queryString



# Fetch data from query.
def fetchData(sqlConnection, queryString, verbose = False):

    import mariadb  # TODO: Necessary if sqlConnection exists?

    # Initialize a cursor.
    # Get results of query as dictianory.
    cursor = sqlConnection.cursor(dictionary = True)

    if verbose: print(queryString)

    try:
        cursor.execute(queryString)
        resultDic = cursor.fetchall()
    except mariadb.ProgrammingError:
        raise mariadb.ProgrammingError
    except Exception as e:
        print(f"Fetching data failed. Got this error: {e}")
        print(f"Query was: {queryString}")
        return [{}]

    # Return list as dictianory.
    return resultDic



# Update a database field or fields.
def executeStatement(sqlConnection, statementString, verbose = False):

    import mariadb  # TODO: Can this safely be assumed unneccesary?

    if verbose:
        print("Executing the following statement: \n")
        print(sqlConnection)

    # Initialize the cursor
    cursor = sqlConnection.cursor()

    # Execture an sql statement.
    try:
        cursor.execute(statementString)

    # Log the execution of this statement.
        sqlLogger.info(
            "The following statement has been executed: %s"
          , statementString.replace("\n", " ")
        )

    except mariadb.IntegrityError as ie:
      print(
          "There seems to be a data integrity error with this statement:" +
          f"{statementString} \n{ie}"
      )
    except Exception as e:
      print(
          "There seems to be a problem with this statement:" +
          f"{statementString} \n{e}"
      )

    # Commit the changes.
    sqlConnection.commit()



# Generic insert into database.
def genericInsert(sqlConnection, tableName, fieldList, valueList, verbose = False):

    import hashlib  # For checksum calculation of the values.

    # Stringify the value list. In a generic case data types aren't known.
    valueList = [str(e) for e in valueList]

    if verbose: print("Inserting Keys:")
    if verbose: print(fieldList)
    if verbose: print("With values:")
    if verbose: print(((valueList)))

    if len(fieldList) != len(valueList):
        raise ValueError("List of fields and list of values don't have the same length")
        print(fieldList)
        print(valueList)
        return -1

    # Insert into procedure table.
    try:

        # Put the statement string together.
        statementString = buildQueryString(
            "./sql/GENERIC_INSERT.SQL"
          , {
                "tableName": tableName
              , "fieldList": ", ".join(fieldList)
              , "valueList": "\'" + "\', \'".join(valueList) + "\'"
            }
        )

        # The statement itself.
        executeStatement(sqlConnection, statementString)

        # Also return primary key and its value (if existing).
        try:
            primaryKeyField = getPrimaryKey(sqlConnection, tableName)
            primaryKeyValue = valueList[fieldList.index(primaryKeyField)]

            return primaryKeyField, primaryKeyValue

        except Exception as e:
            print("Returning primary key field and value failed.")
            print(e)
            return "", -1

        finally:

            # Sort the value list. It will be digested to a sha256 hash
            # as a string. So it needs to be in a distinct order.
            # Later when checking the database the resulting list also
            # has to be sorted to get the exact same hash back.
            valueList.sort()

            # Log the occurence of this insert query.

            sqlLogger.info(
                "Hash check: %s·%s·%s·%s"
              , tableName, primaryKeyField, primaryKeyValue
              , hashlib.sha256(
                  "".join(valueList).encode('utf-8')
                ).hexdigest()
            )

    except Exception as e:
        print(
            "While trying to perform an import to: "
              + tableName + " and this error occured"
        )
        print(e)
        return "", -1



# Function to return a table as list of dictianories for building options.
