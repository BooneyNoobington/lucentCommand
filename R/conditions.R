# Function to be called at the beginning of all scripts.
ensure_conditions <- function(cond_list){
    # Source all the files needed.
    for (s in cond_list$sources) source(s)

    # Ready all packages. The function should be ready since the sources.
    for (p in cond_list$required_packages) ready_packages(p)

    # Check for required files.
    for (f in cond_list$files) if(! file.exists(f)) stop(paste("Error: file", f, "not found."))

    # Check other conditions.
    for (c in cond_list$conditions){
        if(! c$cond) stop(paste("Warning, condition\"", as.character(c$name), "\"not met."))
    }
}



# Conditions for script to calculate mean pH.
mean_pH.R <- list(
    # A bunch of helper files.
    sources = c("./R/helpers.R", "./R/sql_interop.R", "./R/functions.R")
     # Read the system configuration.
  , required_packages = c("yaml")
    # SQL file to get raw values.
  , files = c("./R/mean_pH.SQL", "./conf/config.yaml")
    # Needs exactly one argument.
  , conditions = list(
        list(name = "Needs exactly one argument.", cond = length(args) == 1)
      , list(name = "Dummy", cond = 1 == 1)
    )
)
