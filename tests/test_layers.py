import os

from configlayer import CommaSeparatedStrings, Layer, Secret

test_dir = os.path.dirname(os.path.abspath(__file__))


def p(name: str):
    return os.path.join(test_dir, name)


def test_all():
    defaults = Layer(
        {
            "RDS_DSN": "defaults_rds_dsn",
            "REDIS_URL": "redis://localhost:9874",
            "ABC": "Liam,James,Oliver",
            "stage": "local",
        }
    )
    dotenv = Layer.from_env_file(p(".env"))
    env = Layer.from_env()
    jsoncfg = Layer.from_json_file(p("example.json"))
    yamlcfg = Layer.from_yaml_file(p("example.yaml"))
    testcfg = Layer.from_aws_ssm("/")
    Layer.from_toml_file(p("example.toml"))
    local = Layer({"RDS_DSN": "postgres-4b83h.docker.local"})
    config = env / dotenv / jsoncfg / yamlcfg / defaults
    if config.get("stage", "local"):
        config = local / config

    try:
        config / {}
    except TypeError:
        pass
    else:
        raise AssertionError("the '/' operation should only be valid between instances of Layer")

    print(config["GOBIN"])
    print(config("GOBIN", cast=Secret))
    print(testcfg)
    {**config}
    "ABC" in config
    "23987482345" not in config
    config.maps
    for k, v in config.items():
        print(f"{k}={v}")

    abc = config("ABC", cast=CommaSeparatedStrings)
    assert len(abc) == 3

    print(testcfg)


if __name__ == "__main__":
    test_all()
