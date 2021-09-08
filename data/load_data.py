"""
Logic to load pages with new weather data from source website and create archive
db with weather data for all cities in dates interval from 2010-01-01 till today

"""
from asyncio import Future, gather, run
from concurrent.futures import ProcessPoolExecutor
from datetime import date
from itertools import chain
from os import cpu_count
from random import choice
from typing import Generator, Iterable, Optional, Tuple

from aiohttp import ClientSession
from bs4 import BeautifulSoup, SoupStrainer

from data.cite_config import agents, cities, headers, today, url_main
from data.models import Stat
from data.soup_parser import parse_data

retry = set()


async def load_page(sess: ClientSession, url: str) -> Optional[Tuple[str, ...]]:
    """
    Async function to load pages data with provided aiothhp ClientSession from
    url. Uses custom headers including random user-agent to avoid blocking from
    remote server. If newertheless request was blocked adds url to "retry" set
    for further another attempt to download page. If page from "retry" was
    successfully downloaded - discardes url from "retry". Number of retry
    attempts provided in "main" async function of the script.
    Also returns information of city, year and month for loaded page.

    :param sess: beforehand opened aiothhp ClientSession.
    :param url: url to load page text from.
    :return: tuple with page text data, city, year and month if page was
    successfully loaded, otherwise returns None.

    """
    global retry
    city, year, month = url.split("/")[-4:-1]
    headers["user-agent"] = choice(agents)
    async with sess.get(url, headers=headers) as response:
        if response.status not in range(200, 500):
            return retry.add(url)
        page_text = await response.text()
        retry.discard(url)
    return (page_text, city, year, month) if response.status == 200 else None


def city_urls() -> Generator[str, None, None]:
    """Creates URL templates for cities dict from cite_config.py

    :return: generator expression object which yields URL templates.

    """
    urls = (f"{url_main}/{code}" for code in cities.keys())
    return urls


def city_full_urls(city_url: str) -> Generator[str, None, None]:
    """
    Generates full URLs from provided city_url template to get pages with data
    in range from 2010-01-01 till today from weather data source website.

    :param city_url: city URL template.
    :return: generator expression object which yields full time period URLs.

    """
    years, months = range(2010, int(today.year) + 1), range(1, 13)
    urls = (f"{city_url}/{year}/{month}/" for year in years for month in months)
    return urls


def all_urls() -> Iterable[str]:
    """Generates URLs for all cities in full time period according to task.

    :return: iterable with URLs.

    """
    urls = (city_full_urls(city_url) for city_url in city_urls())
    return chain.from_iterable(urls)


async def load_page_loop(session: ClientSession, urls: Iterable[str]) -> Future:
    """Creates tasks event loop to async load data from provided URLs

    :param session: beforehand opened aiothhp ClientSession.
    :param urls: iterable with URLs to load page from.
    :return: Future object with scheduled tasks.

    """
    tasks = []
    for url in urls:
        tasks.append(load_page(session, url))
    return await gather(*tasks)


def archive_pages_data(load_page_result: Tuple[str, ...]) -> None:
    """
    With provided result of load_page function creates list with Stats model
    instances and saves all weather information in database table.
    Weather information parses via "parse_data" function using bs4.

    :param load_page_result: tuple with result of load_function with page text,
    city name, year and month,
    :return: None.

    """
    if not load_page_result:
        return None
    city_page_text, city_code, year, month = load_page_result
    city = cities[city_code]
    page_strainer = SoupStrainer("div", id="data_block")
    soup = BeautifulSoup(city_page_text, "lxml", parse_only=page_strainer)
    data = parse_data(soup)
    datarows = [(city, get_date(year, month, row[0]), *row[1:]) for row in data]
    Stat.add_commit([Stat(*row) for row in datarows])


def get_date(year: str, month: str, day: str) -> date:
    """Helper function to create datetime.date object from date str info.

    :param year: string with page year info.
    :param month: string with page month info.
    :param day: string with page day info.
    :return: datetime.date object.

    """
    return date(year=int(year), month=int(month), day=int(day))


async def main() -> None:
    """
    Main script to asynchronously load data from all pages with weather info
    from source website, parse weather data from loaded pages using
    multiprocessing and finally save weather statistics into database.
    If there are some pages that doesn't load - retry to load them for 20
    attempts or until all pages loads, whichever occurs first.

    :return: None.

    """
    pool = ProcessPoolExecutor(max_workers=(cpu_count()))
    async with ClientSession(headers=headers) as session:
        pages_data = await load_page_loop(session, all_urls())
        for _ in range(20):
            if retry:
                pages_new_data = await load_page_loop(session, retry)
                pages_data.extend(pages_new_data)
    pool.map(archive_pages_data, pages_data)


def create_weather_archive() -> None:
    """Function that executes main async script via asyncio "run" function.

    :return: None.

    """
    run(main())
