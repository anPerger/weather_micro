 
from flask import Flask, jsonify, request
import random
import numpy as np
import scipy
from scipy import stats
import requests

from key import geo_key

 
app = Flask(__name__)

geocode_base_url = "https://maps.googleapis.com/maps/api/geocode/json?"
weather_base_url = "https://api.open-meteo.com/v1/forecast?" 

weather_codes = {0: "Clear Sky",
                 1: "Mostly Clear",
                 2: "Partly Cloudy",
                 3: "Overcast",
                 45: "Fog",
                 48: " depositing rime fog",
                 51: "Light Drizzle",
                 53: "Moderate Drizzle",
                 55: "Dense Drizzle",
                 56: "Light Freezing Drizzle",
                 57: "Dense Freezing Drizzle",
                 61: "Slight Rain",
                 63: "Moderate Rain",
                 65: "Heavy Rain",
                 66: "Light Freezing Rain",
                 67: "Heavy Freezing Rain",
                 71: "Slight Snow",
                 73: "Moderate Snow",
                 75: "Heavy Snow",
                 77: "Snow Grains",
                 80: "Slight Rain Showers",
                 81: "Moderate Rain Showers",
                 82: "Heavy Rain Showers",
                 85: "Slight Snow Showers",
                 86: "Heavy Snow Showers",
                 95: "Thunderstorm",
                 96: "Thunderstorm w/ Slight Hail",
                 99: "Thunderstorm w/ Heavy Hail"}

def call_geocoder(geocode_query):
    response = requests.get(geocode_query)
    for resp in response:
        print(resp)
    return response.json().get("results")
 
def call_weather(weather_query):
    response = requests.get(weather_query)
    return response.json().get("daily"), response.json().get("timezone")

@app.route("/fetch-weather", methods=['GET'])
def fetch_weather():

    city = request.args.get("city")
    state = request.args.get("state")
    country = request.args.get("country")
    zipcode = request.args.get("zipcode")

    
    custom_query = f"components=locality:{city}|administrative_area:{state}|country:{country}|postal_code:{zipcode}"
  
    
    geocode_query = geocode_base_url + custom_query + "&key=" + geo_key
    # print(geocode_query)

    try:
        response = call_geocoder(geocode_query)[0]
    except IndexError:
        return jsonify({"results": "No data found"})
    
    geometry = response["geometry"]
    formatted_address = response["formatted_address"]
    
    lat = str(geometry["location"]["lat"])
    lng = str(geometry["location"]["lng"])


    weather_query = weather_base_url + "latitude=" + lat + "&longitude=" + lng + "&daily=weather_code,temperature_2m_max,temperature_2m_min,precipitation_probability_max&timezone=auto"
    response, timezone = call_weather(weather_query)
    


    forecast = {}

    for x in range(len(response["time"])):
        day = response["time"][x]
        weather_code = response["weather_code"][x]
        temp_min = response["temperature_2m_min"][x]
        temp_max = response["temperature_2m_max"][x]
        precip = response["precipitation_probability_max"][x]

        weather_code = weather_codes[weather_code]


        forecast[day] = {"weather_code": weather_code,
                         "temp_min_c": temp_min,
                         "temp_max_c": temp_max,
                         "precipitation_%": precip,
                         "days_away": x}

    results = {"timezone": timezone,
               "forecast": forecast,
               "params": {"city": city, "state": state, "country": country, "zipcode": zipcode},
               "city_found": {"formatted_address": formatted_address, "geocodes": {"lat": lat, "lng": lng}}
               }

    return jsonify({"results": results})

if __name__ == "__main__":
    app.run(port=8001, debug=True)