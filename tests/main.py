from configpipe import providers
from configpipe.datastructures import Secret, CommaSeparatedStrings

# Goal: Enable simple and declarative Configuration loaded and overwritten from different sources.
# - configpipe.Layer() is a dict compatible class.
# - using / you can Layer these classes and they implement a __call__(key, cast=None, default=undefined)
"""
from configpipe import Layer
defaults = Layer({})
env = Layer.from_env()
dotenv = Layer.from_dotenv_file(".env")
cfg_file = Layer.from_yaml_file("settings.yaml")
ini_file = Layer.from_ini_file("settings.ini")
json_file = Layer.from_json_file("settings.json")
toml_file = Layer.from_toml_file("abc.toml")
ssm = Layer.from_aws_ssm(root="/prod/env")

config = ssm / env / dotenv / defaults

if config.get("stage", "testing") == "testing":
    config = testing / config
"""
# - We do not enforce input constrains on the individual layers. 
# - To finalize one reading of the configuartion, we suggest using a pydantic model like so
"""
form pydantic import BaseModel

class ServiceConfig(BaseModel):
    RDS_DSN: str|Secret[str]

    class Config:
        extra = "forbid"
        cast = False

config = ServiceConfig.from_obj(dict(unsafe_config))
"""


defaults = providers.Dict({
    "RDS_DSN": "defaults_rds_dsn",
    "REDIS_URL": "defaults_redis_url",
    "ABC": "Liam,James,Oliver",
    "stage": "local"
})
dotenv = providers.EnvFile(".env")
env = providers.Env()
# ssm = providers.SSM()
testing = providers.Dict({})
config = env | dotenv | defaults

if config("stage") == "testing":
    config = testing | config

print(config("sdfsdf", cast=Secret, default="Yes here we go!"))
print(config("ABC", cast=CommaSeparatedStrings))
