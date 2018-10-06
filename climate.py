import numpy as np
import pandas as pd
import datetime as dt
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func, desc

from flask import Flask, jsonify

engine = create_engine('sqlite:///hawaii.sqlite', echo = False)

Base = automap_base()
Base.prepare(engine, reflect = True)

Measurement = Base.classes.measurement
Station = Base.classes.stations

session = Session(engine)


app = Flask(__name__)


@app route("/")
def welcome():
    print ("Someone has visited the index page")
    return ("Welcome")

#Query for the dates and temperature observations from the last year.
#Return the JSON representation of your dictionary.
@app.route("/api/v1.0/precipitation")
def precipitation():
    latest_date = session.query(Measurement).order_by(Measurement.date.desc()).limit(1)
    
    for date in latest_date:
        date_now = date.date

    date_now = dt.datetime.strptime(date_now, "%Y-%m-%d")
    date_oneyear_ago = date_now - dt.timedelta(days=365)

    data = session.query(Measurement.date, Measurement.prcp).filter(Measurement.date >= date_oneyear_ago).order_by(Measurement.date).all()
    
    precipitation_data = []
    for prcp_data in data:
        prcp_data_dict = {}
        prcp_data_dict["Date"] = prcp_data.date
        prcp_data_dict["Precipitation"] = prcp_data.prcp
        precipitation_data.append(prcp_data_dict)
    
    return jsonify(precipitation_data)

#Return a JSON list of stations from the dataset.
@app.route("/api/v1.0/stations")
def stations():
    stations_list = []
  
    stations = session.query(Station).all()
    
    for station in stations:
        station_dict = {}
        stations_dict["Station Name"] = stations.name
        stations_dict["Latitude"] = stations.latitude
        stations_dict["Longitude"] = stations.longitude
        stations_dict["Elevation"] = stations.elevation
        stations_list.append(station_dict)
   
    return jsonify(stations_list)

#Return a JSON list of Temperature Observations (tobs) for the previous year.

@app.route("/api/v1.0/tobs")
def tobs():
    results = session.query(Measurement.station, Measurement.date, Measurement.tobs).group_by(Measurement.date).filter(Measurement.date > date_oneyear_ago).order_by(Measurement.station).all()

    tob_data = []
    for tobs_data in results:
        tobs_data_dict = {}
        tobs_data_dict["Station"] = tobs_data.station
        tobs_data_dict["Date"] = tobs_data.date
        tobs_data_dict["Temperature"] = tobs_data.tobs
        tob_data.append(tobs_data_dict)
    
    return jsonify(tob_data)

#Return a JSON list of the minimum temperature, the average temperature, and the max temperature for a given start or start-end range.
#When given the start only, calculate TMIN, TAVG, and TMAX for all dates greater than and equal to the start date.
@app.route("/api/v1.0/<start>")
def start_temps(start=none):
    results = session.query(func.min(Measurement.tobs), func.max(Measurement.tobs),func.avg(Measurement.tobs)).filter(Measurement.date >= start).all()

    start_stats = []
    
    for Tmin, Tmax, Tavg in results:
        temp_stats_dict = {}
        temp_stats_dict["Minimum Temp"] = Tmin
        temp_stats_dict["Maximum Temp"] = Tmax
        temp_stats_dict["Average Temp"] = Tavg
        start_stats.append(temp_stats_dict)
    
    return jsonify(start_stats)

#When given the start and the end date, calculate the TMIN, TAVG, and TMAX for dates between the start and end date inclusive.
@app.route("/api/v1.0/<start>/<end>")
def temp_stats(start=none, end=none):
    results = session.query(func.min(Measurement.tobs), func.max(Measurement.tobs),func.avg(Measurement.tobs)).filter(Measurement.date >= start).filter(Measurement.date <= end).all()

    temp_stats = []
    
    for Tmin, Tmax, Tavg in results:
        begin_end_stats_dict = {}
        begin_end_stats_dict["Minimum Temp"] = Tmin
        begin_end_stats_dict["Maximum Temp"] = Tmax
        begin_end_stats_dict["Average Temp"] = Tavg
        temp_stats.append(begin_end_stats_dict)
    
    return jsonify(temp_stats)

if __name__ == '__main__':
    app.run(debug=True)
