# config-vars
A python package to make working with configuration variables easier. Configuration variables are usually set using environment variables, which unnecessarily crowds your .zshrc file. You will also eventually forget what these variables' uses actually are. Configvars stores project-specific variables in your virtual environment's 'site-packages' folder and offers an easy-to-use API for loading these in your python modules/scripts.

# Storing variables
From the command line:
```
~  % python3 -m configvars
storage name: flask.website
Enter the variables you want to store. An empty string will save the variables and exit.
>>> MAIL_USER = "user@example.com"
>>> MAIL_PASSWORD = "my_pass"
>>> SECRET_KEY = "fff9cf72a8a9855ef8ba"
>>>
```

# Using the variables you have stored
After an `import configvars`, the following pieces of code accomplish the same result.

### Load the variables for 'flask.website', store them in 'my_vars' and access them like attributes
```
my_vars = configvars.load("flask.website")

class Config:
    MAIL_USER = my_vars.MAIL_USER
    MAIL_PASSWORD = my_vars.MAIL_PASSWORD
    SECRET_KEY = my_vars.SECRET_KEY
```

### Ask configvars to 'hold' the variables for 'flask.website' and access them directly from the package.
```
configvars.hold("flask.website")

class Config:
    MAIL_USER = configvars.MAIL_USER
    MAIL_PASSWORD = configvars.MAIL_PASSWORD
    SECRET_KEY = configvars.SECRET_KEY
```

### Decorate 'Config' with `configvars.load` to load all available variables (note that the 'vars_' argument is necessary to use 'load' as a class decorator).
```
@configvars.load("flask.website", vars_="all")
class Config:
    """My configuration class."""
```
