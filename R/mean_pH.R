#!/bin/env Rscript

# Other code needed to complete this function.
source("./R/helpers.r")  # Functions to solve two to three liners.
source("./R/sql_interop.r")  # Talk to the data base.
ready_packages(c("yaml"))


# Calculate mean of arbitrary inputs.
args = commandArgs(trailingOnly = TRUE)

# Interpret the arguments.
sample.id <- args[1]
procedure.id <- args[2]

# Sanity check, does the file exist?
if (! file.exists("./R/mean_pH.SQL")){
    print("Error, query file not found.")
    quit("no")  # Abort execution, don't save workspace.
}


# Connect to the data base.
sql_connection <- database_connection(yaml::read_yaml(file = "./conf/config.yaml"))


# Collect all the data.
pH.data <- fetch_data(
    sql_connection  # Established above.
  , create_query_string(
        "./R/mean_pH.SQL"  # Raw statement.
        # Replace with actual ids for sample and procedure.
      , list("{sample.id}" = sample.id, "{procedure.id}" = procedure.id)
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
statement.string <- concat(
    "UPDATE `result` SET value = ", result.value, "WHERE id_sample = "
  , sample.id, " AND id_measurand = ", measurand.id
)

