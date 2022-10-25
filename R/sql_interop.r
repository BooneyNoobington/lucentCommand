# Connection has to include the correct keywords.
database_connection <- function(config){

    source("./R/helpers.r")  # Functions for smaller problems.
    ready_packages(c("RMariaDB", "DBI"))  # Connect to a MariaDB.

    sql_connection <- RMariaDB::dbConnect(
        MariaDB()  # Driver definition.
      , dbname = config$database$schema
      , host = config$database$host
      , user = config$database$user
      , unix.socket = config$database$socket
    )

    # Give the connection back.
    return(sql_connection)

}




# Transform a saved query into an executable string.
create_query_string <- function(file.path, replacements.list){

    source("./R/helpers.r")  # Functions for smaller problems.
    ready_packages(c("readr"))

    # First open the file as is.
    query.raw <- readr::read_file(file.path)

    # Then remove all newlines. They might cause problems when executing the query.
    query.string <- gsub("\\n", " ", query.raw)

    # Also remove all occurences in the replacements.list.
    for (r in names(replacements.list)){
        query.string <- gsub(r, replacements.list[[r]], query.string, perl = TRUE)
    }

    return(query.string)

}



# Fetch data from a MariaDB.
fetch_data <- function(sql_connection, query_file, query_string = ""){

    # Decide wether to use a query string or a file.
    if (query_string != ""){
        query = query_string
    }

    # Execute query.
    results <- RMariaDB::dbSendQuery(sql_connection, query)
    results.readable <- RMariaDB::dbFetch(results)

    # Send back the results to calling function.
    return(results.readable)

}
