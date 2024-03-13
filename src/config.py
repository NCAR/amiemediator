import os
from pathlib import Path
from configparser import ConfigParser

class ConfigError(Exception):
    pass

class ConfigLoader:
    """Front-end to ConfigParser

    This class uses ConfigParser to load "ini" files and inject secrets
    from files and or environment variables into the configuration.

    To make use of "secrets injection", a configuration file should use
    variable interpolation: for example, if a ``[localsite]`` section, needs
    to define variable ``password``, it can define it using the syntax
    ``password = %(localsite_password)s``, then rely on ConfigLoader to
    define ``localsite_password``. It does that as follows:

    ConfigLoader first determines the names of all sections in the
    configuration file, and all variables defined in each section.

    It then looks in the directory named in the ``SECRETS_DIR`` environment
    variable for files that begin with "<section>_", where <section> is a
    section name. For each matching file name, it defines a secret variable
    with the filename as the name and the file contents as the value.

    It then searches the environment for variables that have names starting
    with "<ucsection>_", where <ucsection> is a section name converted to
    upper case. For each matching environment variable, it defines a secret
    variable with the lower case environment variable name as a name and the
    environment variable value as the value.

    Config Loader then uses ConfigParser to load the configuration using the
    secret variables as additional defaults, with the expectation that
    the configuation uses variable interpolation to define the values of
    secrets. ConfigParser will also filter the resulting configuration so
    that secrets do not appear in sections that do not use them.
    """

    def loadConfig(configfile) -> dict:
        parser = ConfigParser(default_section="NoSuCh",interpolation=None)
        parser.read(configfile)
        sections = parser.sections()
#        print("DEBUG config sections="+str(sections))
        prefixes = [s+"_" for s in sections]
#        print("DEBUG config prefixes="+str(prefixes))
        section2vars = {}
        for section in sections:
            vars = set()
            for var in parser[section]:
                vars.add(var)
            section2vars[section] = vars
        default_vars = [] if 'DEFAULT' not in section2vars else section2vars['DEFAULT']

        defaults_dict = ConfigLoader._load_files_dict('SECRETS_DIR',prefixes)
        env_dict = ConfigLoader._load_env_dict(prefixes)
        defaults_dict.update(env_dict)

        config = {}

        parser = ConfigParser(defaults=defaults_dict)
        parser.read(configfile)
        for section in parser.sections():
            config[section] = {}
            explicit_vars = section2vars[section]
            for var in parser[section]:
                if var in explicit_vars or var in default_vars:
                    config[section][var] = parser[section][var]
        return config

    def _load_files_dict(key, prefixes):
        secrets_dir = os.environ.get(key,None)
        if secrets_dir is None:
            return {}
        elif not os.path.isdir(secrets_dir):
            return {}
        files = [f for f in os.listdir(secrets_dir) \
                 if os.path.isfile(os.path.join(secrets_dir, f))]
        secrets_dict = {};
        failures = []
        for filename in files:
            for p in prefixes:
                if filename.startswith(p):
                    path = os.path.join(secrets_dir, filename)
                    try:
                        file = open(path,'r')
                        value = file.read()
                        secrets_dict[filename] = value.strip()
                    except Exception as e:
                        failures.add(filename + ": " + str(e))
                    finally:
                        file.close()
                    break
        if failures:
            msg = "Unable to load secrets from {secrets_dir}:\n" + \
                "\n".join(failure)
            raise ConfigError(msg)

        return secrets_dict

    def _load_env_dict(prefixes):
        ucprefixes = [p.upper() for p in prefixes]
        env_dict = {}
        for envvar in os.environ:
            for p in ucprefixes:
                if envvar.startswith(p):
                    env_dict[envvar.lower()] = os.environ[envvar]
                    break
        return env_dict
