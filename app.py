# import dependencies
import datetime as dt
import numpy as np
import pandas as pd

# import SQLAlchemy & flask
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from flask import Flask, jsonify

# set up database engine
engine = create_engine("sqlite:///hawaii.sqlite")

# reflect database into classes, reflect tables
Base = automap_base()
Base.prepare(engine, reflect=True)

# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station

# create a session link from python to database
session = Session(engine)

# set up our flask application 
app = Flask(__name__)

# define the 'welcome' route
@app.route('/')

def welcome():
    return(
    '''
    Welcome to the Climate Analysis API!
    Available Routes:
    /api/v1.0/precipitation
    /api/v1.0/stations
    /api/v1.0/tobs
    /api/v1.0/temp/start/end
    ''')


# create second route for precpiptation data
@app.route("/api/v1.0/precipitation")

# create precipitation function
def precipitation():
    # calculate date 1 year ago from most recent date in database
    prev_year = dt.date(2017,8,23) - dt.timedelta(days=365)

    # write a query to get the date and precip frm prev yr
    precipitation = session.query(Measurement.date, Measurement.prcp).\
        filter(Measurement.date >= prev_year).all()
    
    # use list comprehension to create a json file structure
    precip = {date: prcp for date, prcp in precipitation}

    # return the data as a json file
    return jsonify(precip)


# create route for station list
@app.route("/api/v1.0/stations")

# define function for returning stations
def stations():

    # build query with sqlalchemy
    results = session.query(Station.station).all()
    
    # unravel results into 1d array as a list
    stations = list(np.ravel(results))
    
    # the list as json with formatting (stations=stations)
    return jsonify(stations=stations)

# create route for the temp observations
@app.route("/api/v1.0/tobs")

# define function for temp observations
def temp_monthly():

    # calc prev yr from last day
    prev_year = dt.date(2017,8,23) - dt.timedelta(days=365)
    results = session.query(Measurement.tobs).\
        filter(Measurement.station == "USC00519281").\
        filter(Measurement.date >= prev_year).all()

    # turn into 1d array and then list
    temps = list(np.ravel(results))
    return jsonify(temps=temps)



# create route for desckiptive stats with variable start/end dates
@app.route("/api/v1.0/temp/<start>")
@app.route("/api/v1.0/temp/<start>/<end>")

# create stats function with parameters
def stats(start=None, end=None):

    # create query to to select min, avg, max temp.  create list
    sel = [func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)]

    # add if-not statement
    if not end:
        results = session.query(*sel).\
            filter(Measurement.date >= start).all()
        temps = list(np.ravel(results))
        return jsonify(temps=temps)
        
    results = session.query(*sel).\
        filter(Measurement.date >= start).\
        filter(Measurement.date <= end).all()
    temps = list(np.ravel(results))
    return jsonify(temps)