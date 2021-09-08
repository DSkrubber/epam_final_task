"""Defines form for gather data from user on index page of website"""
from flask_wtf import FlaskForm
from wtforms import SelectField
from wtforms.validators import DataRequired

from data.cite_config import cities

city_list = [cities for cities in cities.values()]


class WeatherForm(FlaskForm):
    """Website form with list of cities.

    Also allows to add hidden_tag for web page to avoid CSRF"""

    city = SelectField(
        "Select city:",
        choices=city_list,
        default=cities["4079"],
        validators=[DataRequired()],
    )
