# Database related functionality.

# Connect to a sqlite database file.
def databaseConnection(sqliteFile):

  # Import required package.
  import sqlite3

  # Initialize empty connection.
  conn = None

  # Try and fill it with the actual game data.
  try:
    conn = sqlite3.connect(sqliteFile)
  except Error as e:
    print(e)
  
  # Return the connection.
  return conn


# Function to determine primary key of table.
def getPrimaryKey(sqlConnection, table):

    import helpers as h

    # Get the id field value for the passed.
    tableInfo = fetchData(
          sqlConnection
        , "PRAGMA table_info(" + table + ");"
    )

    # What is the name of the primary key?
    try:
        primaryKey = h.selectDictianory(tableInfo, "pk", 1)["name"]
    except Exception as e:
        print("Could not determine the primary key for table: " + table)
        print(e)
        return 1   # End function with error 1.


    return primaryKey


 
# Build a query string from an sql file.
def buildQueryString(SQLFile, replacements = {}):
  with open(SQLFile, "r") as openedSQLFile:
    queryList = openedSQLFile.readlines()
  
  queryString = "".join(queryList)

  # Put in actual values for placeholders.
  queryString = queryString.format(**replacements)

  return queryString



# Helper function to get query results as dictianory not list.
def dict_factory(cursor, row):
  d = {}
  for idx, col in enumerate(cursor.description):
    d[col[0]] = row[idx]
  return d  
  

# Fetch data from query.
def fetchData(sqliteConnection, queryString, verbose = False):

  import sqlite3

  # Initialize a cursor.
  # Get results of query as dictianory.
  sqliteConnection.row_factory = dict_factory
  cursor = sqliteConnection.cursor()
  # Apply sql command.

  if verbose: print(queryString)

  try:
    cursor.execute(queryString)
    resultDic = cursor.fetchall()
  except sqlite3.OperationalError:
    print("This query seems to be faulty:")
    print(queryString)
    # Return an empty result set.
    return {}
  except Exception as e:
    print(e)
    return {}

  # Return list as dictianory.
  return resultDic
  

# Update a database field or fields.
def executeStatement(sqliteConnection, statementString, verbose = False):

  import sqlite3  # TODO: Can this safely be assumed unneccesary?

  if verbose:
    print("Executing the following statement: \n")
    print(statementString)
  # Initialize the cursor
  cursor = sqliteConnection.cursor()
  # Execture an sql statement.
  try:
    cursor.execute(statementString)
  except sqlite3.IntegrityError as ie:
    print("There seems to be a data integrity error with this statement:")
    print(statementString)
    print(ie)
  except Exception as e:
    print("There seems to be a problem with this statement:")
    print(statementString)
    print(e)
  # Commit the changes.
  sqliteConnection.commit()  


# Generic insert into database.
def genericInsert(sqlConnection, tableName, fieldList, valueList, verbose = False):

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
        # The statement itself.
        executeStatement(
            sqlConnection
          , buildQueryString(
                "./sql/GENERIC_INSERT.SQL"
              , {
                    "tableName": tableName
                   , "fieldList": ", ".join(fieldList)
                   , "valueList": "\'" + "\', \'".join(valueList) + "\'"
                }
            )
        )
        # Also return primary key and its value (if existing).
        try:
            primaryKeyField = getPrimaryKey(sqlConnection, tableName)
            primaryKeyValue = valueList[fieldList.index(primaryKeyField)]
            return primaryKeyField, primaryKeyValue
        except Exception as e:
          print("Returning primary key field and value failed.")
          print(e)
          return "", -1

    except Exception as e:
        print(
            "While trying to perform an import to: "
              + tableName + " and this error occured"
        )
        print(e)
        return "", -1
