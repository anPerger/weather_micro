import requests
import json




weather_microservice_url = "http://127.0.0.1:8001/fetch-weather?"


def call_weather_microservie(sim_request_string):
    response = requests.get(sim_request_string)
    return response.json().get("results")


city = input("city: ")
state = input("state: ")
country = input("country: ")
zipcode = input("zipcode: ")


custom_query = f"city={city}&state={state}&country={country}&zipcode={zipcode}"

query_string = weather_microservice_url + custom_query


weather_results_by_city = call_weather_microservie(query_string)

print(weather_results_by_city)