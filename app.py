import pandas as pd
import requests
import os
from datetime import datetime
from datetime import date

import json
from flask import Flask, request

app = Flask(__name__)


@app.route('/', methods=['GET', 'POST'])
def crop_recommendation():
    """ function which take json input
    json input name :['n','p','k','ph','state','city'] """
    ## extract user input information
    if request.method =="POST":
        re = request.get_json()
        print(re)
        city= request.get_json["city"]
        print(city)
        #state = re['state']
        model_ph = re['ph']
        model_n = re['n']
        model_p = re['p']
        model_k = re['k']
    ##Api key for the call
        user_api = "6c4043b2272bb3cf1e7330517937f690"
    
        ## extract the weather data such as temp,humidity as per user given location
        complete_api_link = "https://pro.openweathermap.org/data/2.5/forecast/climate?q=" + \
                            city + "&appid=" + user_api
        api_link = requests.get(complete_api_link)
    
        ## response of api in api_data
        api_data = api_link.json()
    
        ## lets get the average of the temp and humidity for monthly
        humidity_sum = 0
        temp_sum = 0
        ll = api_data["list"]
        for i in range(30):
            temp = ll[i]['temp']
            temp_avg = (temp['day'] + temp['min'] + temp["max"] + temp["night"] + temp["eve"]) / 5
            temp_sum = (temp_avg - 273) + temp_sum
            humidity = ll[i]['humidity']
            humidity_sum = humidity + humidity_sum
    
        ## store the of avg of humidity and temperature in the varibale which we pass to model
        model_humidity = humidity / 30
        model_temp = temp_sum / 30
    
        ## lets get rainfall of the location
        today = date.today()
        current_month = today.month
        current_date = today.day
        current_year = today.year
    
        ## harvesting time get from database
        harvesting_time = 4
    
        ## create an list for the month number for which we have to get rainfall
        temp_month = current_month
        rainfall_month_list = []
        for i in range(harvesting_time):
            if temp_month > 12:
                temp_month = 1
            else:
                rainfall_month_list.append(temp_month)
                temp_month = temp_month + 1
    
        ## get the rainfall from the database for the given month
    
        model_rainfall = 154
    
        ## get the dataset and append in list for model
        model_para = [model_n, model_p, model_k, model_temp, model_humidity, model_ph, model_rainfall]
        # NOTE: you must manually set API_KEY below using information retrieved from your IBM Cloud account.
        API_KEY = "6Pe2pNaBxpPB0eN7oyIPBQgDZ6d_ujIp8h4W1ik-pyk5"
        token_response = requests.post('https://iam.cloud.ibm.com/identity/token',
                                       data={"apikey": API_KEY, "grant_type": 'urn:ibm:params:oauth:grant-type:apikey'})
        mltoken = token_response.json()["access_token"]
    
        header = {'Content-Type': 'application/json', 'Authorization': 'Bearer ' + mltoken}
    
        # NOTE: manually define and pass the array(s) of values to be scored in the next line
        payload_scoring = {"input_data": [
            {"field": ['N', 'P', 'K', 'temperature', 'humidity', 'ph', 'rainfall', 'label'], "values": [model_para]}]}
    
        response_scoring = requests.post(
            'https://us-south.ml.cloud.ibm.com/ml/v4/deployments/91bf6a6b-7d60-4e50-b75b-bc99fd76d42a/predictions?version=2021-07-08',
            json=payload_scoring, headers={'Authorization': 'Bearer ' + mltoken})
    
        response_score = response_scoring.json()
    return response_score


if __name__ == '__main__':
    app.run(debug=False)
