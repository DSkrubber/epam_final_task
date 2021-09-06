"""Defines SQLAlchemy models for project weather statistics database"""
from datetime import date

from sqlalchemy import Column, Date, Integer, String

from data.db import Base, Session, engine


class Stat(Base):
    """
    Creates Stat object with provided weather data. Automatically adds row
    data to db.py engine database table "statistic" after instantiation.
    Database table will have fields with data for weather statistics: stat_id,
    city, day, max_temp, min_temp, avg_temp, weather, w_direction, w_speed.

    Stat(city: str, day: date, max_temp: str, min_temp: str, weather: str,
    w_direction: str, w_speed: str)

    :param city: city name.
    :param day: date for weather data row.
    :param max_temp: maximal temperature for given city and date.
    :param min_temp: minimal temperature for given city and date.
    :param weather: information about precipitations for given city and date.
    :param w_direction: direction of wind for given city and date.
    :param w_speed: speed of wind for given city and date.

    """

    __tablename__ = "statistic"
    stat_id = Column(Integer, primary_key=True, autoincrement=True)
    city = Column(String, nullable=False)
    day = Column(Date, nullable=False)
    max_temp = Column(Integer, default=None)
    min_temp = Column(Integer, default=None)
    avg_temp = Column(Integer, default=None)
    weather = Column(String, default=None)
    w_direction = Column(String, default="Calm")
    w_speed = Column(Integer, default=0)

    def __init__(
        self,
        city: str,
        day: date,
        max_temp: str,
        min_temp: str,
        weather: str,
        w_direction: str,
        w_speed: str,
    ) -> None:
        self.city = city
        self.day = day
        self.max_temp = max_temp
        self.min_temp = min_temp
        self.avg_temp = f"{(int(self.max_temp) + int(self.min_temp)) / 2:+.2f}"
        self.weather = weather
        self.w_direction = w_direction
        self.w_speed = w_speed

    @classmethod
    def add_commit(cls, rows: Base) -> None:
        """Saves data from iterable with db.py Base instances to engine database

        Creates database and table on first commit if not exists.
        Closes session after commit.

        :param rows: iterable with rows - db.py Base instances.
        :return: None.

        """
        if rows:
            session = Session()
            Base.metadata.create_all(engine)
            session.add_all(rows)
            session.commit()
            session.close()
