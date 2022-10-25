#!/bin/env Rscript

source("./R/helpers.r")
ready_packages(c("yaml"))

# Load configuration file.
# No need to recurse if the database information is not in an included file.
# TODO: Enforce this by style checking conf files.
config <- yaml::read_yaml(file = "./conf/config.yaml")

source("./R/sql_interop.r")

sql_connection <- database_connection(config)

query <- create_query_string(
    "./sql/TEST.SQL"
  , list(
        "{reciever1}" = "kotzboy"
      , "{reciever2}" = "Testi"
      , "{reciever3}" = "Testo"
    )
)

print(query)
