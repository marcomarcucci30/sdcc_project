import json
import pathlib

config_path = pathlib.Path(__file__).parent / 'config.json'


def retrieve_config():
    """
    A function to load configuration file.json
    Returns: configurations in json format

    """
    config_file = open(config_path, "r")
    json_object = json.load(config_file)
    config_file.close()
    return json_object
