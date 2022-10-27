#!/bin/env Rscript

# Other code needed to complete this function.
source("./R/helpers.r")  # Functions to solve two to three liners.
source("./R/sql_interop.r")  # Talk to the data base.
ready_packages(c("yaml"))


# Calculate mean of arbitrary inputs.
args = commandArgs(trailingOnly = TRUE)

# Interpret the arguments.
result.id <- args[1]

# Sanity check, does the file exist?
if (! file.exists("./R/mean_pH.SQL")){
    print("Error, query file not found.")
    quit("no")  # Abort execution, don't save workspace.
}


# Connect to the data base.
sql_connection <- database_connection(yaml::read_yaml(file = "./conf/config.yaml"))


# Collect all the data.

# What sample, procedure and measurand is this about?
spm <- fetch_data(
    sql_connection  # Established above.
  , paste(
        "SELECT id_sample, id_procedure, id_measurand FROM `result` WHERE id_result = "
      , result.id
      , sep = ""
    )
)

# What's the input?
pH.data <- fetch_data(
    sql_connection  # Established above.
  , create_query_string(
        "./R/mean_pH.SQL"  # Raw statement.
        # Replace with actual ids for sample and procedure.
      , list("{sample.id}" = spm$id_sample, "{procedure.id}" = spm$id_procedure)
    )
)


# Function to calculate a mean of several pHs.
pH.mean <- function(pH.vec){

    # Transform log to concentration.
	concentration <- exp(-(pH.vec)/(log(exp(1))))

	# Compute mean. Ingore "not numbers".
	concentration.mean <- mean(concentration, na.rm = TRUE )

	# Re-transform to logarithm.
	concentration.mean.log <- -log(concentration.mean)

	return(concentration.mean.log)
}


# Calculate the result.
result.value <- pH.mean(pH.data$value)

# Pute the value into the database.
statement.string <- paste(
    "UPDATE `result` SET value = ", result.value, "WHERE id_sample = ", spm$id_sample
  , "AND id_procedure = ", spm$id_procedure
  , "AND id_measurand = ", spm$id_measurand
)

execute_statement(sql_connection, statement.string)
