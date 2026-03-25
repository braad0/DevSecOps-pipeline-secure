import yaml


def load_config_unsafe(yaml_string: str) -> dict:
    return yaml.load(yaml_string)


def load_config_full_loader(yaml_string: str) -> dict:
    return yaml.load(yaml_string, Loader=yaml.Loader)


def load_config_from_file(path: str) -> dict:
    with open(path, "r") as f:
        return yaml.load(f)
