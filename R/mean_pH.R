#!/bin/env Rscript

# Grab command line arguments.
args = commandArgs(trailingOnly = TRUE)

# See if the conditions for the correct execution of this script are met.
source("./R/conditions.R")
ensure_conditions(mean_pH.R)

# Connect to the data base.
# Argument is lucent config which is read by read_yaml and returned as a list.
sql_connection <- database_connection(yaml::read_yaml(file = "./conf/config.yaml"))


# Collect all the data.

# What sample, procedure and measurand is this about?
spm <- fetch_data(
    sql_connection  # Established above.
  , paste(
        "SELECT id_sample, id_procedure, id_measurand FROM `result` WHERE id_result = "
      , args[1]  # This is the results id.
      , sep = ""
    )
)

# What's the input?
# This is highly variable depending on the needs of the script.
# It doesn't always just load the raw values with the same sample, procedure and measurand.
pH.data <- fetch_data(
    sql_connection  # Established above.
  , create_query_string(
        "./R/mean_pH.SQL"  # Raw statement.
        # Replace with actual ids for sample and procedure.
      , list(
            "{sample.id}" = spm$id_sample
          , "{procedure.id}" = spm$id_procedure
          , "{measurand.id}" = spm$id_measurand
        )
    )
)

# Calculate the result.
result.value <- pH.mean(pH.data$value)

# Pute the value into the database.
statement.string <- paste(
    "UPDATE `result` SET value = ", result.value, "WHERE id_sample = ", spm$id_sample
  , "AND id_procedure = ", spm$id_procedure
  , "AND id_measurand = ", spm$id_measurand
)

execute_statement(sql_connection, statement.string)
