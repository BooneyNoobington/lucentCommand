def getOptions(sqlConnection, tableOrView, where = "", viewPrefix = "attach"):

    import sql_interop as si
    import mariadb

    try:
        options = si.fetchData(
            sqlConnection, f"SELECT * FROM {viewPrefix}_{tableOrView} {where};"
        )
    # If the view doesn't exist, interpret argument as simple table.
    except mariadb.ProgrammingError:
        options = si.fetchData(sqlConnection, f"SELECT * FROM {tableOrView} {where};")
    except Exception as e:
        print(f"Error retrieving options for picker, {e}.")

    return options
