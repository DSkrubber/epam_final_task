"""Different config data for application scripts"""
from datetime import date
from json import load
from typing import List

url_main = "https://www.gismeteo.ru/diary"
today = date.today()


def load_agents() -> List[str]:
    """Loads data with different user-agents for web request from config file.

    :return: list of user-agent strings.

    """
    with open("data/configs/user_agents.txt") as file:
        return file.read().splitlines()


def load_json_config(file_path: str) -> dict:
    """Loads data from provided json file path

    :param file_path: config file name.
    :return: dict object with data from json file.

    """
    with open(f"data/configs/{file_path}") as file:
        return load(file)


agents = [agent for agent in load_agents()]
wind_codes = load_json_config("wind_codes.json")
headers = load_json_config("headers.json")
cities = load_json_config("cities.json")
