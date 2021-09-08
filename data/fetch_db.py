"""
Defines class that provides API for fetching data from database for user request
in Flask app.

"""
from contextlib import contextmanager
from datetime import datetime, timedelta
from typing import Generator, List, Optional, Tuple

from sqlalchemy import desc, func

from data.cite_config import today
from data.models import Session, Stat

last_day = today - timedelta(days=1)


@contextmanager
def session_manager() -> Generator[Session, None, None]:
    session = Session()
    try:
        yield session
    finally:
        session.close()


class GetStats:
    """
    Class that provides facade API for Flask app to load data from database
    according to request parameters. Has multiple methods for gather weather
    statistics parameters.

    """

    def get_min_temp(self, city: str, begin: str, end: str) -> int:
        """
        Make query to database and returns absolute minimum temperature for
        provided city and time period.

        :param city: city to gather min_temp data for.
        :param begin: date from which gather statistics.
        :param end: date until which gather statistics.
        :return: absolute minimum temperature value.

        """
        with session_manager() as session:
            min_temp = (
                session.query(func.min(Stat.min_temp))
                .filter(Stat.city == city, Stat.day.between(begin, end))
                .first()[0]
            )
        return min_temp

    def get_max_temp(self, city: str, begin: str, end: str) -> int:
        """
        Make query to database and returns absolute maximum temperature for
        provided city and time period.

        :param city: city to gather max_temp data for.
        :param begin: date from which gather statistics.
        :param end: date until which gather statistics.
        :return: absolute maximum temperature value.

        """
        with session_manager() as session:
            max_temp = (
                session.query(func.max(Stat.max_temp))
                .filter(Stat.city == city, Stat.day.between(begin, end))
                .first()[0]
            )
        return max_temp

    def get_avg_temp(self, city: str, begin: str, end: str) -> float:
        """
        Make query to database and returns average temperature for provided
        city and time period.

        :param city: city to gather avg_temp data for.
        :param begin: date from which gather statistics.
        :param end: date until which gather statistics.
        :return: average temperature value.

        """
        with session_manager() as session:
            avg_temp = (
                session.query(func.avg(Stat.avg_temp))
                .filter(Stat.city == city, Stat.day.between(begin, end))
                .first()[0]
            )
        return round(avg_temp, 2)

    def get_wind_speed(self, city: str, begin: str, end: str) -> float:
        """
        Make query to database and returns average wind speed for provided
        city and time period.

        :param city: city to gather w_speed data for.
        :param begin: date from which gather statistics.
        :param end: date until which gather statistics.
        :return: average wind speed value.

        """
        with session_manager() as session:
            wind_speed = (
                session.query(func.avg(Stat.w_speed))
                .filter(Stat.city == city, Stat.day.between(begin, end))
                .first()[0]
            )
        return round(wind_speed, 2)

    def get_wind_dir(self, city: str, begin: str, end: str) -> str:
        """
        Make query to database and returns average wind direction for provided
        city and time period.

        :param city: city to gather w_direction data for.
        :param begin: date from which gather statistics.
        :param end: date until which gather statistics.
        :return: string with average wind direction value.

        """
        with session_manager() as session:
            wind_dir = (
                session.query(
                    Stat.w_direction, func.count(Stat.w_direction).label("dir")
                )
                .filter(Stat.city == city, Stat.day.between(begin, end))
                .group_by(Stat.w_direction)
                .order_by(desc("dir"))
                .first()[0]
            )
        return wind_dir

    def get_date_temp(self, city: str, begin: str, end: str) -> List[str]:
        """
        Make query to database and returns list with dates for provided
        city and time period in which average temperature was closest to last
        date temperature.

        :param city: city to gather date data for.
        :param begin: date from which gather statistics.
        :param end: date until which gather statistics.
        :return: list of strings with dates in which average temperature was
        closest to last date temperature.

        """
        with session_manager() as session:
            today_data = (
                session.query(Stat)
                .filter(Stat.city == city, Stat.day == last_day)
                .first()
            )
            today_t = today_data.avg_temp
            dates = (
                session.query(Stat)
                .filter(Stat.city == city, Stat.day.between(begin, end))
                .all()
            )
            days = [(abs(date.avg_temp - today_t), date.day) for date in dates]
            dates = sorted(days, key=lambda x: x[0])
        return [datetime.strftime(day[1], "%d.%m.%Y") for day in dates][:2]

    def precipitations(self, city: str, begin: str, end: str) -> float:
        """
        Make query to database and returns percentage of days with any
        precipitations for provided city and time period.

        :param city: city to gather weather data for.
        :param begin: date from which gather statistics.
        :param end: date until which gather statistics.
        :return: percentage value of days with any precipitations.

        """
        day_from = datetime.strptime(begin, "%Y-%m-%d")
        day_until = datetime.strptime(end, "%Y-%m-%d")
        period = day_until - day_from
        days = period.days + 1
        with session_manager() as session:
            precipitations_count = (
                session.query(func.count(Stat.weather))
                .filter(Stat.city == city, Stat.day.between(begin, end))
                .first()[0]
            )
        percentage = precipitations_count / days * 100
        return round(percentage, 2)

    def common_weather(self, city: str, begin: str, end: str) -> List[str]:
        """
        Make query to database and returns list with most common precipitations
        for provided city and time period.

        :param city: city to gather weather data for.
        :param begin: date from which gather statistics.
        :param end: date until which gather statistics.
        :return: list with most common precipitations.

        """
        with session_manager() as ses:
            weathers = (
                ses.query(Stat.weather, func.count(Stat.weather).label("count"))
                .filter(Stat.city == city, Stat.day.between(begin, end))
                .group_by(Stat.weather)
                .order_by(desc("count"))
                .limit(2)
                .all()
            )
        return [weather[0] for weather in weathers if weather[0]]

    def get_years_max(
        self, city: str, begin: str, end: str
    ) -> Optional[List[Tuple[int, float]]]:
        """
        If provided time period is 2 years and more - make query to database
        and returns list with city's average maximum temperature for all years
        except current year.

        :param city: city to gather max_temp data for.
        :param begin: date from which gather statistics.
        :param end: date until which gather statistics.
        :return: list with years and appropriate average maximum temperatures.

        """
        first_year, last_year = int(begin[:4]), int(end[:4])
        if last_year - first_year < 2:
            return None
        years = range(first_year, last_year)
        year_temps = []
        session = Session()
        for year in years:
            start, stop = f"{year}-01-01", f"{year}-12-31"
            year_max_temp = (
                session.query(func.avg(Stat.max_temp))
                .filter(Stat.city == city, Stat.day.between(start, stop))
                .first()[0]
            )
            year_temps.append((year, round(year_max_temp, 2)))
        session.close()
        return year_temps

    def get_years_min(
        self, city: str, begin: str, end: str
    ) -> Optional[List[Tuple[int, float]]]:
        """
        If provided time period is 2 years and more - make query to database
        and returns list with city's average minimum temperature for all years
        except current year.

        :param city: city to gather min_temp data for.
        :param begin: date from which gather statistics.
        :param end: date until which gather statistics.
        :return: list with years and appropriate average minimum temperatures.

        """
        first_year, last_year = int(begin[:4]), int(end[:4])
        if last_year - first_year < 2:
            return None
        years = range(first_year, last_year)
        year_temps = []
        session = Session()
        for year in years:
            start, stop = f"{year}-01-01", f"{year}-12-31"
            year_min_temp = (
                session.query(func.avg(Stat.min_temp))
                .filter(Stat.city == city, Stat.day.between(start, stop))
                .first()[0]
            )
            year_temps.append((year, round(year_min_temp, 2)))
        session.close()
        return year_temps
