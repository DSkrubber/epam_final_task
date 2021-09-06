"""Loads pages with new weather data, parses values and adds new rows into db"""
from typing import Optional, Tuple

from bs4 import BeautifulSoup, SoupStrainer
from requests import get

from data.cite_config import cities, headers, url_main
from data.fetch_db import last_day
from data.models import Stat
from data.soup_parser import parse_data


def city_last_url(city_code: str) -> str:
    """
    Generates URL from provided city_code to get pages with data for last_day
    from weather data source website.

    :param city_code: URL code for city.
    :return: URL for provided city with last_day weather data.

    """
    year, month = last_day.year, last_day.month
    url = f"{url_main}/{city_code}/{year}/{month}/"
    return url


def load_page(url: str) -> str:
    """
    Loads page text from provided URL via requests.get with custom headers
    (to avoid connection blocking from remote server).

    :param url: url to load page text from.
    :return: page text data.

    """
    with get(url, headers=headers) as response:
        return response.text


def get_last_weather(data: str) -> Optional[Tuple[str, ...]]:
    """Returns tuple with parsed weather parameters from provided page text.

    :param data: web page text data.
    :return: tuple with weather parameters strings if page provided,
    None otherwise.

    """
    if not data:
        return None
    page_strainer = SoupStrainer("div", id="data_block")
    soup = BeautifulSoup(data, "lxml", parse_only=page_strainer)
    weather_data = parse_data(soup)
    return next(weather_data)


def add_today_weather() -> None:
    """
    Function to load data from all pages with all cities weather info for
    last date from source website, parse weather data from loaded pages and
    finally save weather statistics into database. Used for Celery task in
    celery_task.daily_worker.py

    :return: None.

    """
    last_weather_data = []
    for city in cities:
        city_url = city_last_url(city)
        city_weather_page = load_page(city_url)
        _, *weather_data = get_last_weather(city_weather_page)
        last_weather_data.append(Stat(cities[city], last_day, *weather_data))
    Stat.add_commit(last_weather_data)
