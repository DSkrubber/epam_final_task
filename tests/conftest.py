"""Fixtures for pytest tests"""
from datetime import datetime
from typing import Generator, List
from unittest.mock import patch

from bs4 import BeautifulSoup, SoupStrainer, Tag
from flask.testing import FlaskClient
from pytest import fixture

from app import app
from data.cite_config import today
from data.fetch_db import last_day
from data.models import Base, Session, Stat, engine
from tests.db_config import engine, session


@fixture(scope="function")
def client(request) -> Generator[FlaskClient, None, None]:
    """
    Prepares flask application for testing, and binds to test temporary database

    :return: generator that yields FlaskClient instance.

    """
    app.config["TESTING"] = True
    app.config["SERVER_NAME"] = "127.0.0.1:5000"
    app.testing = True
    with app.test_client() as client:
        Base.metadata.create_all(bind=engine)
        rows = [
            Stat("default", last_day, "100", "-100", "Sunny", "S", "100 m/sec"),
            Stat("default", today, "100", "-100", "Sunny", "S", "100 m/sec"),
        ]
        session.add_all(rows)
        session.commit()
        with client.session_transaction() as sess:
            date_str = datetime.strftime(today, "%Y-%m-%d")
            sess["city"] = request.param
            sess["date_from"] = sess["date_until"] = date_str
        yield client
    app.config["TESTING"] = False
    app.config["SERVER_NAME"] = "0.0.0.0:5000"


@fixture
@patch("data.fetch_db.session_manager", return_value=session, autospec=True)
def page(mock_session_manager, client) -> str:
    """
    Returns page data for response of "/reports/default" web page URL

    :return: statistics report page data.

    """
    rv = client.get("/reports/default")
    return rv.data


@fixture
def statistics_parse(page) -> List[str]:
    """Returns parsed weather statistics from "/reports/default" web page

    :return: list with weather statistics data for tests.

    """
    soup = BeautifulSoup(page, "lxml")
    statistic = soup.find_all("span", class_="param-value")
    data = [row.text for row in statistic]
    data.pop(3)
    return data


@fixture
def parse_result() -> List[str]:
    """Returns expected result data for "test_main_application

    :return:  list with expected results.

    """
    with open("tests/expected_parse_result.txt", encoding="utf-8") as result:
        return result.read().splitlines()


@fixture
def mock_db() -> Generator[Session, None, None]:
    """
    Creates temporary database for tests and adds row with data in Stats table

    :return: generator that yields SQLAlchemy Session instance for database.

    """
    Base.metadata.create_all(bind=engine)
    session = Session(bind=engine)
    row = Stat("default", today, "+100", "-100", "Sunny", "S", "100m/sec")
    session.add(row)
    session.commit()
    yield session


@fixture
def mock_page() -> Generator[Tag, None, None]:
    """Returns bs4 Tag for mock web pag

    :return: generator that yields bs4 Tag object for tests.

    """
    with open("tests/mock_page.html", "rb") as page:
        text = page.read()
    page_strainer = SoupStrainer("div", id="data_block")
    soup = BeautifulSoup(text, "lxml", parse_only=page_strainer)
    yield soup
