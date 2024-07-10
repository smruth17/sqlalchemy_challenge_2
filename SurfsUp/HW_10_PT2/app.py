import numpy as np
import pandas as pd
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
import datetime as dt
from datetime import datetime

from flask import Flask, jsonify

# Database Setup
engine = create_engine("sqlite:///hawaii.sqlite")
# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(autoload_with=engine)
# Save reference to the table
Measurement = Base.classes.measurement
Station = Base.classes.station

# Flask Setup
app = Flask(__name__)

# Flask Routes
@app.route("/")
def home():
	return (
	f"Available Routes:<br/>"
	f"/api/v1.0/precipitation<br/>" 
	f"/api/v1.0/stations<br/>"
	f"/api/v1.0/tobs<br/>"    
	f"/api/v1.0/2016-08-23<br/>"
	f"/api/v1.0/2016-08-23/2016-12-31<br/>"
	)

# QUERIES

# Returns Json with the date as the key and the value as precipitation
# Only returns the jsonified precipitation data for the last year in the database

@app.route("/api/v1.0/precipitation")
def precipitation():

	session = Session(engine)

	# Calculate the date one year from the last date in data set.
	begin_date = dt.date(2017, 8, 23) - dt.timedelta(days=365)

	# Perform a query to retrieve the data and precipitation scores
	results = session.query(Measurement.date, Measurement.prcp)\
		.filter(Measurement.date >= begin_date)\
		.group_by(Measurement.date)\
		.all()
	
	session.close()

	precipitation_data = {}
	for date, prcp in results:
		precipitation_data[date] = prcp

	return jsonify(precipitation_data)


# Returns jsonified data of all of the stations in the database

@app.route("/api/v1.0/stations")
def stations():

	session = Session(engine)

	results = session.query(Station.station, Station.name).all()

	session.close()

	station_data = []
	for station, name in results:
		station_dict = {}
		station_dict["name"] = name
		station_data.append(station_dict)

	return jsonify(station_data)

# Query the dates and temperature observations of the most active station (USC00519281)
# for the previous year of data

@app.route("/api/v1.0/tobs")
def tobs():
	session = Session(engine)
	begin_date = dt.date(2017, 8, 23) - dt.timedelta(days=365)

	results = session.query(Measurement.tobs).\
		filter(Measurement.station == 'USC00519281').\
		filter(Measurement.date >= begin_date).all()

	session.close()
	tobs_data = list(np.ravel(results))
	return jsonify(tobs_data=tobs_data)


# Accepts the start date as a parameter from the URL 
# Returns the min, max, and average temperatures calculated from the given start date to the end of the dataset
# Received help from the Xpert Learning Assistant
@app.route("/api/v1.0/<start>")
def start(start):
	session = Session(engine)
	start_date = datetime.strptime(start, '%Y-%m-%d')
	results = session.query(
		func.min(Measurement.tobs),
		func.max(Measurement.tobs),
		func.avg(Measurement.tobs)
	).filter(Measurement.date >= start_date).all()

	session.close()

	start_dict = []
	for result in results:
		start_dict.append({
		"Min_Temp": result[0],
		"Max_Temp": result[1],
		"Avg_Temp": result[2]
		})
	return(jsonify(start_dict))


# Accepts the start and end dates as parameters from the URL 
# Returns the min, max, and average temperatures calculated from the given start date to the given end date 
@app.route("/api/v1.0/<start>/<end>")
def start_end(start, end):
	session = Session(engine)
	start_date = datetime.strptime(start, '%Y-%m-%d')
	end_date = datetime.strptime(end, '%Y-%m-%d')
	results = session.query(
		func.min(Measurement.tobs),
		func.max(Measurement.tobs),
		func.avg(Measurement.tobs),
	).filter(
		Measurement.date >= start_date
	).filter(
		Measurement.date <= end_date
	).all()
	
	session.close()

	end_dict = {
        "start_date": start,
        "end_date": end,
        "min_temp": results[0][0],
        "max_temp": results[0][1],
        "avg_temp": results[0][2]
    }
    
	return jsonify(end_dict)

if __name__ == '__main__':
	app.run(debug=True)