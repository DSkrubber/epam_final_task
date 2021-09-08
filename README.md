# Repository for EPAM summer'21 final_task "Weather Statistics"
***
There is a simple application to create webserver using Flask which allows to access web page with weather statistics for multiple cities.

By default there are available cities:
* "moscow", 
* "saint-petersburg", 
* "sevastopol", 
* "krasnodar", 
* "sochi", 
* "novosibirsk", 
* "vladivostok", 
* "irkutsk", 
* "volgograd", 
* "kazan", 
* "berlin", 
* "canberra", 
* "tokyo", 
* "new-deli", 
* "cairo"

Statistics archive allows to gather weather data from **01.01.2010** till **present day**.

For chosen city and time period there are represented:
1. Temperature statistics:
    * absolute minimum temperature,
    * absolute maximum temperature,
    * average temperature,
    * if period is longer that 2 years:
        - average maximum temperatures per years,
        - average minimum temperatures per years,
    * dates in which average temperature was closest to period last date temperature,
2. Precipitations statistics:
    * percentage of days with any precipitations,
    * percentage of days without any precipitations,
    * list of up to two most common precipitations,
3. Wind statistics:
    * average wind speed,
    * average wind direction.

To run application make shure to install **Docker and Docker Compose** and simply run in terminal within project directory:

    docker-compose up -d

After server starts all weather statistics loads asynchronously from source web archive cite into local Docker volume SQLite database
Every day database will gather new weather statistics in background using Celery workers and Celery beat schedule processes (with RabbitMQ as brocker).

Web site will be available at *<http://localhost:5000>*.