# Compile a list of options to present to the user.
def getOptions(sqlConnection, tableOrView, where = "", viewPrefix = "attach"):

    import sql_interop as si  # Talk to the database.
    import mariadb  # Handle sql related errors.

    # Compile a list of dictianories which represent the options.
    try:
        options = si.fetchData(
            sqlConnection, f"SELECT * FROM `{viewPrefix}_{tableOrView}` {where};"
        )
    # If the view doesn't exist, interpret argument as simple table.
    except mariadb.ProgrammingError:
        options = si.fetchData(sqlConnection, f"SELECT * FROM `{tableOrView}` {where};")
    # Catch other stuff that might go wrong.
    except Exception as e:
        print(f"Error retrieving options for picker, {e}.")
        return {}  # Return an empty list. Anything that calls getOptions will have to deal with.

    return options
