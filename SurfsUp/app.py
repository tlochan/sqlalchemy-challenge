# Import the dependencies.
import numpy as np
import pandas as pd
import datetime as dt
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func, select


#################################################
# Database Setup
#################################################

# reflect an existing database into a new model
engine = create_engine("sqlite:///Resources/hawaii.sqlite")
Base = automap_base()

# reflect the tables
Base.prepare(autoload_with = engine)

# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create our session (link) from Python to the DB
session = Session(engine)

#################################################
# Flask Setup
#################################################
from flask import Flask, jsonify
app = Flask(__name__)
#################################################
# Flask Routes
#################################################

@app.route("/")
def homepage():
    
    x = "<p> Climate App - Homepage </p>"
    x+= "<p> Available Routes: </p>"
    x+="<p> /api/v1.0/precipitation </p>"
    x+="<p> /api/v1.0/stations </p>"
    x+="<p> /api/v1.0/tobs </p>"
    x+="<p> /api/v1.0/<start> </p>"
    x+="<p> /api/v1.0/<start>/<end> </p>"
    return x

@app.route("/api/v1.0/precipitation")
def precipitation():
    # Convert the query results from your precipitation analysis\
    # (i.e. retrieve only the last 12 months of data) to a dictionary using date as the key and prcp as the value.
    last_year = session.query(Measurement.date,Measurement.prcp).\
    filter(Measurement.date>='2016-08-23')

    precipitation_dict = {}
    for row in last_year:
        precipitation_dict[row.date] = row.prcp
    #Return the JSON representation of your dictionary.
    return jsonify(precipitation_dict)

@app.route("/api/v1.0/stations")
def stations():
    #Return a JSON list of stations from the dataset
    station_list = session.query(Station.name).distinct()
    station_dict = {}
    for row in station_list:
        station_dict[row] = row.name
    return jsonify(station_list)


@app.route("/api/v1.0/tobs")
def temp():
    #Query the dates and temperature observations of the most-active station for the previous year of data.
    temp_dict={}
    best_station = session.query(Measurement.date,Measurement.tobs)\
.filter(Measurement.date>='2016-08-23')\
.filter(Measurement.station =='USC00519281')
    for row in best_station:
        temp_dict[row.date] = row.tobs
    #Return a JSON list of temperature observations for the previous year.
    return jsonify(temp_dict)

@app.route("/api/v1.0/<start>")
def start(start):
    #For a specified start, calculate TMIN, TAVG, and TMAX for all the dates greater than or equal to the start date.
    temps_df = pd.read_sql(f"SELECT * FROM measurement WHERE date>={start}", conn)
    tmin = temps_df["tobs"].min()
    tmax = temps_df["tobs"].max()
    tavg = temps_df["tobs"].mean()
    temp_data = {"TMIN":tmin,
                 "TMAX":tmax,
                 "TAVG":tavg}
    return jsonify(temp_data)

@app.route("/api/v1.0/<start>/<end>")
def start_end(start, end):
    #For a specified start, calculate TMIN, TAVG, and TMAX for all the dates greater than or equal to the start date."
    temps_df = pd.read_sql(f"SELECT * FROM measurement", conn)
    temps_df = temps_df[(temps_df["date"]<=end) & (temps_df["date"]>=start)]
    tmin = temps_df["tobs"].min()
    tmax = temps_df["tobs"].max()
    tavg = temps_df["tobs"].mean()
    temp_data = {"TMIN":tmin,
                 "TMAX":tmax,
                 "TAVG":tavg}
    return jsonify(temp_data)

app.run(debug=True)