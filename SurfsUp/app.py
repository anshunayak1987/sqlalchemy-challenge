###############################################
# Import statments
#################################################

import numpy as np

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify

import datetime as dt
from dateutil.relativedelta import relativedelta
###############################################
# Database Setup
#################################################
engine = create_engine("sqlite:///./Resources/hawaii.sqlite")
# Reflect an existing database into a new model.
base = automap_base()
# Reflect the tables.
base.prepare(engine, reflect=True)
# Save reference to the tables.
measurement = base.classes.measurement
Station = base.classes.station
#print(base.classes.keys())
#################################################
# Flask Setup
#################################################
app = Flask(__name__,static_url_path='/Images/surfs-up.png')
#################################################
# Flask Routes
#################################################

#Creating home page and the routes

@app.route("/")
def welcome():
    """List all available api routes."""
    return (
        f"<h1>Home page - Climate App</h1>"
        f"<h2>Available routes:</h2>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/start<br/>"
        f"/api/v1.0/start/end<br/>"
        f"<h2>Links to the routes:</h2>"
####################################################
#giving the data link.
####################################################
        f"<ol><li><a href=http://127.0.0.1:5000/api/v1.0/precipitation>"
        f"Precipitation amounts </a></li>"
        f"<li><a href=http://127.0.0.1:5000/api/v1.0/stations>"
        f"Stations </a></li>"
        f"<li><a href=http://127.0.0.1:5000/api/v1.0/tobs>"
        f"Temperatures</a></li>"
        f"<li><a href=http://127.0.0.1:5000/api/v1.0/2017-08-23>"
        f"Given start date (YYYY-MM-DD), calculate the minimum, average, and maximum temperature for all dates greater than and equal to the start date</a></li>"
        f"<li><a href=http://127.0.0.1:5000/api/v1.0/2016-08-23/2017-08-23>"
        f"Given the start and the end date (YYYY-MM-DD), calculate the minimum, average, and maximum temperature for dates between the start and end date</a></li></ol>"
        f" <img width='500' src='https://newacttravel.com/wp-content/uploads/2018/12/main-hawaii-pool_0.jpg'/ >"
       
    )
#################################################
# precipitation Route
#################################################
@app.route("/api/v1.0/precipitation")
def precipitation():
    #retrieve only the last 12 months of data.to a dictionary using date as the key and prcp as the value.
    # Create our session (link) from Python to the DB.
    session = Session(engine)

    #Calculate the date 1 year ago from the last data point in the database.
    #Calculating the date 1 year ago from last data point. 
    last_measurement_data_point_tuple = session.query(
        measurement.date).order_by(measurement.date.desc()).first()
    (latest_date, ) = last_measurement_data_point_tuple
    latest_date = dt.datetime.strptime(latest_date, '%Y-%m-%d')
    latest_date = latest_date.date()
    date_year_ago = latest_date - relativedelta(years=1)

    #Perform a query to retrieve the data and precipitation scores.
    #Retrieveing the data and precipitation scores.
    data_from_last_year = session.query(measurement.date, measurement.prcp).filter(
        measurement.date >= date_year_ago).all()

    session.close()

   
    #Converting the query results to a dictionary.
    all_precipication = []
    for date, prcp in data_from_last_year:
        if prcp != None:
            precip_dict = {}
            precip_dict[date] = prcp
            all_precipication.append(precip_dict)

    #Return the JSON.
    return jsonify(all_precipication)

#################################################
# stations Route
#################################################
@app.route("/api/v1.0/stations")
def stations():
    """Return a JSON list of stations from the dataset."""
   
    #Creating our session from Python.
    session = Session(engine)

    #stations query.
    stations = session.query(Station.station, Station.name,
                             Station.latitude, Station.longitude, Station.elevation).all()

    session.close()

    
    #creating dictionary for result.
    all_stations = []
    for station, name, latitude, longitude, elevation in stations:
        station_dict = {}
        station_dict["station"] = station
        station_dict["name"] = name
        station_dict["latitude"] = latitude
        station_dict["longitude"] = longitude
        station_dict["elevation"] = elevation
        all_stations.append(station_dict)

    # Return the JSON 
    return jsonify(all_stations)

#################################################
#Temperature Route
#################################################
@app.route("/api/v1.0/tobs")
def tobs():
    #Query the dates and temperature observations of the most-active station for the previous year of data.
    #Return a JSON list of temperature observations for the previous year.
    
    #Createing session .
    session = Session(engine)

    
    #Calculate the date 1 year ago from the latest date
    last_measurement_data_point_tuple = session.query(
        measurement.date).order_by(measurement.date.desc()).first()
    (latest_date, ) = last_measurement_data_point_tuple
    latest_date = dt.datetime.strptime(latest_date, '%Y-%m-%d')
    latest_date = latest_date.date()
    date_year_ago = latest_date - relativedelta(years=1)

        #Identifing most active station.
    most_active_station = session.query(measurement.station).\
        group_by(measurement.station).\
        order_by(func.count().desc()).\
        first()

    #station id of the most active station.
    #finding the station id for the most active station.
    (most_active_station_id, ) = most_active_station
    print(
        f"Station id of most active station : {most_active_station_id}.")

    #Retrieveing the data temperature scores for the most active station.
    data_from_last_year = session.query(measurement.date, measurement.tobs).filter(
        measurement.station == most_active_station_id).filter(measurement.date >= date_year_ago).all()

    session.close()

    
    #Converting the query results to a dictionary.
    all_temperatures = []
    for date, temp in data_from_last_year:
        if temp != None:
            temp_dict = {}
            temp_dict[date] = temp
            all_temperatures.append(temp_dict)
   
    #Return the Json.
    return jsonify(all_temperatures)

#################################################
#start Route
#################################################
@app.route('/api/v1.0/<start>', defaults={'end': None})

#################################################
# start/end Route
#################################################
@app.route("/api/v1.0/<start>/<end>")
def determine_temps_for_date_range(start, end):
    #Return a JSON list of the minimum temperature, the average temperature, and the maximum temperature for a specified start or start-end range.
    #For a specified start, calculate TMIN, TAVG, and TMAX for all the dates greater than or equal to the start date.
    #For a specified start date and end date, calculate TMIN, TAVG, and TMAX for the dates from the start date to the end date, inclusive.

  
    #Creating our session link.
    session = Session(engine)

    #If statment for start date and end date 
    if end != None:
        temperature_data = session.query(func.min(measurement.tobs), func.avg(measurement.tobs), func.max(measurement.tobs)).\
            filter(measurement.date >= start).filter(
            measurement.date <= end).all()
   
    #If statment for start date only
    else:
        temperature_data = session.query(func.min(measurement.tobs), func.avg(measurement.tobs), func.max(measurement.tobs)).\
            filter(measurement.date >= start).all()

    session.close()
    #Converting our query results to list.
    temperature_list = []
    no_temperature_data = False
    for min_temp, avg_temp, max_temp in temperature_data:
        if min_temp == None or avg_temp == None or max_temp == None:
            no_temperature_data = True
        temperature_list.append(min_temp)
        temperature_list.append(avg_temp)
        temperature_list.append(max_temp)
      #Return the JSON.
    if no_temperature_data == True:
        return f"No temperature data found for date range provided. Try again"
    else:
        return jsonify(temperature_list)
if __name__ == '__main__':
    app.run(debug=True)