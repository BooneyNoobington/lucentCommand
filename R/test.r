#!/bin/env Rscript

library(yaml)

setwd("/opt/lucent")

# Load configuration file.
# No need to recurse if the database information is not in an included file.
# TODO: Enforce this by style checking conf files.
config <- yaml::read_yaml(file = "./conf/config.yaml")

source("./R/sql_interop.r")

sql_connection <- database_connection(config)

query <- create_query_string("./sql/GET_PERSON.SQL", list(reciever = "Markus"))

print(query)
