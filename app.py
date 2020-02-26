# Import dependencies
import numpy as np
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from flask import Flask, jsonify
import datetime as dt


#Setup database
engine = create_engine("sqlite:///Resources/hawaii.sqlite")
Base = automap_base()
Base.prepare(engine, reflect=True)

Measurement = Base.classes.measurement
Station = Base.classes.station


# Setup Flask
app = Flask(__name__)


#Create Routes
@app.route("/")
def home():
# List all routes that are available.
    return (
        f"Climate App<br/>"
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0//api/v1.0/<start><br/>"
        f'/api/v1.0/<start>/<end>'
)


@app.route("/api/v1.0/precipitation")
def precipitation():
    #Convert the query results to a Dictionary using date as the key and prcp as the value.
    session = Session(engine)
    prcpQuery = session.query(Measurement.date, Measurement.prcp).all()
    session.close()

    prcpDict = dict(prcpQuery)

    #Return the JSON representation of your dictionary.
    return jsonify(prcpDict)
  

@app.route("/api/v1.0/stations")
def stations():
    #Return a JSON list of stations from the dataset

    session = Session(engine)
    stationQuery = session.query(Station.station).all()
    session.close()

    stationList = []
    for station in stationQuery:
        stationList.append(station[0])
        
    return jsonify(stationList)


@app.route("/api/v1.0/tobs")
def tobs():
    #Query for the dates and temperature observations from a year from the last data point
    session = Session(engine)
    last = session.query(func.max(Measurement.date))[0][0]
    prev_yr = dt.datetime.strptime(last, '%Y-%m-%d') - dt.timedelta(days=364) 
    tempQuery = session.query(Measurement.date, Measurement.tobs).filter(Measurement.date >= prev_yr).order_by(Measurement.date).all()
    session.close()

    #Return a JSON list of Temperature Observations (tobs) for the previous year.
    tempList= []
    for temps in tempQuery:
        tempDict = {}
        tempDict = {temps.date: temps.tobs}
        tempList.append(tempDict)

    return jsonify(tempList)


@app.route("/api/v1.0/<start>")
def start_temp(start):
    #When given the start only, calculate TMIN, TAVG, and TMAX for all dates greater than and equal to the start date.
    session = Session(engine)
    startQuery = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).filter(Measurement.date >= start).all()
    session.close()

    startList = []

    startDict = {}
    startDict["Minimum"] = startQuery[0][0]
    startDict["Average"] = startQuery[0][1]
    startDict["Maximum"] = startQuery[0][2]
    startList.append(startDict)

    return jsonify(startList)


@app.route("/api/v1.0/<start>/<end>")
def start_end_temp(start, end):
    #When given the start and the end date, calculate the TMIN, TAVG, and TMAX for dates between the start and end date inclusive.
    session = Session(engine)
    start_end_query = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).filter(Measurement.date >= start).filter(Measurement.date <= end).all()
    session.close()

    start_end_list = []
    
    start_end_dict = {}
    start_end_dict["Minimum"] = start_end_query[0][0]
    start_end_dict["Average"] = start_end_query[0][1]
    start_end_dict["Maximum"] = start_end_query[0][2]
    start_end_list.append(start_end_dict)

    return jsonify(start_end_list)    


if __name__ == "__main__":
    app.run(debug=True)