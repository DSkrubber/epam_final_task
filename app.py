"""Flask web application with views for weather statistics site"""
from os import environ, path, urandom
from typing import Tuple, Union

from flask import Flask as Flask
from flask import Response, abort, redirect, render_template, request, session
from werkzeug.exceptions import HTTPException

from data.cite_config import today, wind_codes
from data.fetch_db import GetStats
from data.forms import WeatherForm
from data.load_data import create_weather_archive

SECRET_KEY = environ.get("SECRET_KEY") or urandom(24).hex()
app = Flask(__name__)
app.config["SECRET_KEY"] = SECRET_KEY


@app.route("/", methods=["GET", "POST"])
@app.route("/index", methods=["GET", "POST"])
def index() -> Union[Response, str]:
    """Generates site main page with form for period and city input.
    In case of form validation redirects to city report page.
    Adds data from form into Flask "session" to share with another flask views.

    """
    form = WeatherForm()
    if form.validate_on_submit():
        city = form.city.data
        session["city"] = city
        session["date_from"] = request.form["date_from"]
        session["date_until"] = request.form["date_until"]
        return redirect(f"/reports/{city}")
    return render_template("index.html", form=form, today=today)


@app.route("/reports/<string:city>")
def report(city: str) -> str:
    """
    Generates site page - report for chosen city and period with weather
    statistics from Flask "session" parameters.

    """
    stats = GetStats()
    city = session["city"]
    date_from = session["date_from"]
    date_until = session["date_until"]
    try:
        params = {
            "max_temp": stats.get_max_temp(city, date_from, date_until),
            "min_temp": stats.get_min_temp(city, date_from, date_until),
            "avg_temp": stats.get_avg_temp(city, date_from, date_until),
            "wind_speed": stats.get_wind_speed(city, date_from, date_until),
            "wind_dir": stats.get_wind_dir(city, date_from, date_until),
            "date_temp": stats.get_date_temp(city, date_from, date_until),
            "precipitations": stats.precipitations(city, date_from, date_until),
            "common_weather": stats.common_weather(city, date_from, date_until),
            "years_max": stats.get_years_max(city, date_from, date_until),
            "years_min": stats.get_years_min(city, date_from, date_until),
            "wind_codes": wind_codes,
        }
    except Exception:
        abort(500)
    return render_template("report.html", city=city, params=params)


@app.errorhandler(404)
def page_not_found(error: HTTPException) -> Tuple[str, int]:
    """Renders page for 404 error cases"""
    return render_template("404.html"), 404


@app.errorhandler(500)
def server_error(error: HTTPException) -> Tuple[str, int]:
    """Renders page for 500 error cases"""
    return render_template("500.html"), 500


if __name__ == "__main__":
    if not path.isfile("/db/statistic.db"):
        create_weather_archive()
    app.run(host="0.0.0.0", debug=True)
