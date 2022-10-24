# Helper functions for order processing.


# ---- OS related --------------------------------------------------------------

# Get operating system.
lubw.get_os <- function(){
  sysinf <- Sys.info()
  if (!is.null(sysinf)){
    os <- sysinf['sysname']
    if (os == 'Darwin')
      os <- "osx"
  } else { ## mystery machine
    os <- .Platform$OS.type
    if (grepl("^darwin", R.version$os))
      os <- "osx"
    if (grepl("linux-gnu", R.version$os))
      os <- "linux"
  }
  tolower(os)
}


# Install packages and add them to the library.
ready_packages <- function(
      packages.vec
    , repo = "https://cran.us.r-project.org"
    , lib.bool = TRUE  # Load packages.
    , verbose.bool = FALSE
    , proxy.str = ""
    , always_install.bool = FALSE
)
{
  
  # Set proxy.
  Sys.setenv(https_proxy = proxy.str)
  
  # Identify packages which are not yet installed.
  new.packages <- packages.vec[!(packages.vec %in% installed.packages()[,"Package"])]
  
  # If there are uninstalled packages install them.
  if (always_install.bool){  # Do not check if packages are already installed.
    print("Force install these packages:")
    print(packages.vec)
    install.packages(new.packages, repos = repo)
  } else {
    # Install only if there are packages that aren't available.
    print("Installing these packages:")
    print(new.packages)
    if(length(new.packages)) install.packages(new.packages, repos = repo)
  }
  
  # Now load all required packages.
  if (lib.bool){
    for (current.package in packages.vec){
      library(current.package, character.only = TRUE)
    }
  }
  
}
