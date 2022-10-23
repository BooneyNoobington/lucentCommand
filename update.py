# Manipulating existing data in a rdbms.

# Attach a n to m relation. E.g. an analysis to a sample.
def attachNtoM(caller, masterTable, detailTable):

    import sql_interop as si  # Database Manipulation.
    import mariadb  # Mostly for

    # List all the info from first dataset.


