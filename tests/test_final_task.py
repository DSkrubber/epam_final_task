"""Tests for final_task to run with pytest"""
from datetime import datetime
from unittest.mock import patch

from pytest import mark

from data.cite_config import today
from data.fetch_db import GetStats
from data.soup_parser import parse_data
from tests.db_config import session


@mark.parametrize("client", ["default"], indirect=True)
def test_index(client):
    """Tests correct behaviour for web site index page"""
    rv = client.get("/not/exists/page")
    assert rv.status == "404 NOT FOUND"


@mark.parametrize("client", ["default"], indirect=True)
def test_404(client):
    """Tests correct behaviour for web site page in cases of 404 error"""
    rv = client.get("/not/exists/page")
    assert rv.status == "404 NOT FOUND"


@mark.parametrize("client", ["random_city"], indirect=True)
def test_500(client):
    """Tests correct behaviour for web site page in cases of 500 error"""
    rv = client.get("/reports/default")
    assert rv.status == "500 INTERNAL SERVER ERROR"


@mark.parametrize("client", ["default"], indirect=True)
def test_main_application(statistics_parse, page, client, parse_result):
    """Tests correct behaviour for web page with generated weather statistics"""
    assert statistics_parse == parse_result


@patch("data.fetch_db.session_manager", return_value=session, autospec=True)
def test_get_max_temp(mock_session_manager, mock_db):
    """Tests correct behaviour for get_max_temp database-fetch function"""
    stats = GetStats()
    result = stats.get_max_temp("default", today, today)
    assert result == 100


@patch("data.fetch_db.session_manager", return_value=session, autospec=True)
def test_get_min_temp(mock_session_manager, mock_db):
    """Tests correct behaviour for get_min_temp database-fetch function"""
    stats = GetStats()
    result = stats.get_min_temp("default", today, today)
    assert result == -100


@patch("data.fetch_db.session_manager", return_value=session, autospec=True)
def test_get_avg_temp(mock_session_manager, mock_db):
    """Tests correct behaviour for get_avg_temp database-fetch function"""
    stats = GetStats()
    result = stats.get_avg_temp("default", today, today)
    assert result == 0


@patch("data.fetch_db.session_manager", return_value=session, autospec=True)
def test_get_wind_speed(mock_session_manager, mock_db):
    """Tests correct behaviour for get_wind_speed database-fetch function"""
    stats = GetStats()
    result = stats.get_wind_speed("default", today, today)
    assert result == 100


@patch("data.fetch_db.session_manager", return_value=session, autospec=True)
def test_get_wind_dir(mock_session_manager, mock_db):
    """Tests correct behaviour for get_wind_dir database-fetch function"""
    stats = GetStats()
    result = stats.get_wind_dir("default", today, today)
    assert result == "S"


@patch("data.fetch_db.session_manager", return_value=session, autospec=True)
def test_get_date_temp(mock_session_manager, mock_db):
    """Tests correct behaviour for get_date_temp database-fetch function"""
    stats = GetStats()
    result = stats.get_date_temp("default", today, today)
    day = datetime.strftime(today, "%d.%m.%Y")
    assert result == [day, day]


@patch("data.fetch_db.session_manager", return_value=session, autospec=True)
def test_precipitations(mock_session_manager, mock_db):
    """Tests correct behaviour for precipitations database-fetch function"""
    stats = GetStats()
    day = datetime.strftime(today, "%Y-%m-%d")
    result = stats.precipitations("default", day, day)
    assert result == 1100


def test_parse_data(mock_page):
    """Tests correct behaviour for weather parameters parser function"""
    data = parse_data(mock_page)
    assert ("1", "-10", "-14", None, "N", "1m/s") == list(data)[0]
