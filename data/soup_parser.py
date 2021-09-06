"""Gathers weather statistics data from weather archive site via bs4"""
from typing import Iterator, Optional, Tuple

from bs4 import Tag


def parse_data(soup: Tag) -> Optional[Iterator[Tuple[str, ...]]]:
    """Returns weather data from provided BeautifulSoup Tag.

    :param soup: Tag with page data.
    :return: Iterable with weather data string tuples.

    """
    table = soup.find("table")
    if not table:
        return None
    rows = table.find_all("tr", attrs={"align": "center"})
    days = [row.find("td", class_="first").text for row in rows]
    temps = [row.find("td", class_="first_in_group") for row in rows]
    max_temps = [temp.text if temp else None for temp in temps]
    min_temps = [get_sibling(temp, 9).text if temp else None for temp in temps]
    weather_pics = [get_sibling(temp, 5).img for temp in temps]
    precipitations = [get_weather(pic) if pic else None for pic in weather_pics]
    winds = [get_sibling(temp, 7).text for temp in temps]
    wind_dir = [dir_eng(wind.split()[0]) if wind else "" for wind in winds]
    wind_speed = [speed_eng(wind.split()[-1]) if wind else "" for wind in winds]
    return zip(days, max_temps, min_temps, precipitations, wind_dir, wind_speed)


def get_sibling(soup: Tag, index: int) -> Tag:
    """Helper function to get tags sibling from list of siblings.

    :param soup: tag object to find siblings.
    :param index: sibling's index in list of tags siblings.
    :return: sibling tag object.

    """
    return list(soup.next_siblings)[index]


def get_weather(pic: Tag) -> str:
    """Helper function to get string with weather from picture-src tag"""
    return pic["src"].split("/")[-1].split(".")[0]


def speed_eng(wind_speed: str) -> str:
    """Helper function to translate wind speed data from russian to english.

    :param wind_speed: wind speed information in russian language.
    :return: wind speed information in english language.

    """
    return wind_speed.replace("Ш", "0m/s").replace("м/с", "m/s")


def dir_eng(wind_dir: str) -> str:
    """Helper function to translate wind direction data from russian to english.

    :param wind_dir: wind direction information in russian language.
    :return: wind direction information in english language.

    """
    dictionary = [("С", "N"), ("Ю", "S"), ("З", "W"), ("В", "E"), ("Ш", "Calm")]
    for direction in dictionary:
        wind_dir = wind_dir.replace(direction[0], direction[1])
    return wind_dir
