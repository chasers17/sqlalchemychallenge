# Import the dependencies.
import numpy as np
import pandas as pd
import datetime as dt
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify

#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite", connect_args={"check_same_thread": False})

Base = automap_base()

# reflect an existing database into a new model
Base.prepare(engine, reflect=True)

# reflect the tables
# Save references to each table
measure = Base.classes.measurement
station = Base.classes.station

# Create our session (link) from Python to the DB
session = Session(engine)

#################################################
# Flask Setup
#################################################
app = Flask(__name__)

#################################################
# Flask Routes
#################################################
@app.route("/")
def home():
    """List all available routes."""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/&lt;start&gt;<br/>"
        f"/api/v1.0/&lt;start&gt;/&lt;end&gt;"
    )

#Convert the query results from your precipitation analysis (i.e. retrieve only the last 12 months of data) to a dictionary using `date` as the key and `prcp` as the value.
@app.route("/api/v1.0/precipitation")
def precipitation():
    """Last 12 Months of Precipitation Data."""
    last_date = session.query(measure.date).order_by(measure.date.desc()).first()[0]
    query_date = dt.datetime.strptime(last_date, '%Y-%m-%d') - dt.timedelta(days=365)
    results = session.query(measure.date, measure.prcp).filter(measure.date >= query_date).all()
    precipitation = {date: prcp for date, prcp in results}
    
    return jsonify(precipitation)

#Return a JSON list of stations from the dataset.
@app.route("/api/v1.0/stations")
def stations():
    """All Stations."""
    results = session.query(station.station, station.name).all()
    stations = [{"Station": station, "Name": name} for station, name in results]
    
    return jsonify(stations)

#Query the dates and temperature observations of the most-active station for the previous year of data.
@app.route("/api/v1.0/tobs")
def tobs():
    """Last 12 Months Temp Data."""
    last_date = session.query(measure.date).order_by(measure.date.desc()).first()[0]
    query_date = dt.datetime.strptime(last_date, '%Y-%m-%d') - dt.timedelta(days=365)
    
    most_active_station = session.query(measure.station).\
        group_by(measure.station).\
        order_by(func.count().desc()).\
        first()[0]
    results = session.query(measure.date, measure.tobs).\
        filter(measure.station == most_active_station).\
        filter(measure.date >= query_date).all()
    temperatures = [{"Date": date, "Temperature": temp} for date, temp in results]
    
    #Return a JSON list of temperature observations for the previous year.
    return jsonify(temperatures)

#Return a JSON list of the minimum temperature, the average temperature, and the maximum temperature for a specified start or start-end range.
#For a specified start, calculate `TMIN`, `TAVG`, and `TMAX` for all the dates greater than or equal to the start date.
@app.route("/api/v1.0/<start>")
def temps_start(start):
    start_date = dt.datetime.strptime(start, '%Y-%m-%d')
    temps = session.query(func.min(measure.tobs), func.avg(measure.tobs), func.max(measure.tobs)).filter(measure.date >= start_date).all()
    temps_dict = {}
    temps_dict['TMIN'] = temps[0][0]
    temps_dict['TAVG'] = temps[0][1]
    temps_dict['TMAX'] = temps[0][2]

    # Return the JSON representation of the dictionary
    return jsonify(temps_dict)

# For a specified start date and end date, calculate `TMIN`, `TAVG`, and `TMAX` for the dates from the start date to the end date, inclusive.
@app.route("/api/v1.0/<start>/<end>")
def temps_start_end(start, end):
    start_date = dt.datetime.strptime(start, '%Y-%m-%d')
    end_date = dt.datetime.strptime(end, '%Y-%m-%d')
    
    temps = session.query(func.min(measure.tobs), func.avg(measure.tobs), func.max(measure.tobs)).filter(measure.date >= start_date).filter(measure.date <= end_date).all()
    temps_dict = {}
    temps_dict['TMIN'] = temps[0][0]
    temps_dict['TAVG'] = temps[0][1]
    temps_dict['TMAX'] = temps[0][2]

    # Return the JSON representation of the dictionary
    return jsonify(temps_dict)


if __name__ == '__main__':
    app.run(debug=True)