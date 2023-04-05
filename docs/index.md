# Welcome to your documentation site!
configlayer enables you to easily read, compose and manage your application configuration.

## How it works
You load your configuration from various sources, including **environment variables, dot files, json, yaml, toml, ini files or the AWS Systems Manager Parameter Store** into `Layer`s. These are `dict` compatible custom classes that provide two additional core features:
1. Layers can be combined with `a / b`, where mappings in a will take precedence over mappings in b. The left layer takes precendence over the right layer. A KeyError will occur if no Layer contains that key. 
2. You can call Layers, giving you the handy `layer(key: str, cast=None, default=undefined)` interface. See examples below.

## Installation
Most data sources can be imported with no dependencies outside the python standard library. Some data sources require additional dependencies you can optionally install with the bracket `[]` notation. 
```
# support environment variables, dotfiles, ini-files and JSON
pip install configlayer

# and support YAML
pip install configlayer[yaml]

# and support TOML in Python < 3.11; part of stdlib for >=3.11
pip install configlayer[toml]

# and support AWS SSM
pip install configlayer[ssm]

# and support multiple, e. g. AWS SSM and YAML
pip install configlayer[ssm,yaml]
```

### Examples
```python
from configlayer import Layer, Secret, comma

defaults = Layer({
    "S3_BUCKET": "some-bucket-name"
    "TIMEOUT": "3600",
    "ALLOWED_HOSTS": "http://localhost,https://frontend.com"
})
env = Layer.from_env()
file = Layer.from_env_file(".env")

config = file / env / defaults

if config.get("CI", False):
    testenv = Layer.from_env_file(".testing.env")
    config = testenv / config

S3_BUCKET = config["S3_BUCKET"]
TIMEOUT = config("TIMEOUT", cast=int) # equivalent to int(config["TIMEOUT"])
ALLOWED_HOSTS = config("ALLOWED_HOSTS", cast=CommaSeparatedStrings)
RDS_SECRET = config("RDS_SECRET", cast=Secret)
OAUTH_SECRET = config("OAUTH_SECRET", cast=Secret)
```

Interact with it like normal dict, e. g. 
```
for k, v in config:
    print(k, v)
```
