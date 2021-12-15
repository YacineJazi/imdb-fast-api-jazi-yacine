from typing import List
from fastapi import FastAPI, HTTPException
from fastapi import FastAPI, File, UploadFile
import pandas as pd
import numpy as np
from io import StringIO
import uvicorn
import urllib.request
import json
import os
import ssl
import re

app = FastAPI()

def allowSelfSignedHttps(allowed):
    # bypass the server certificate verification on client side
    if allowed and not os.environ.get('PYTHONHTTPSVERIFY', '') and getattr(ssl, '_create_unverified_context', None):
        ssl._create_default_https_context = ssl._create_unverified_context

allowSelfSignedHttps(True) # this line is needed if you use self-signed certificate in your scoring service.

@app.get("/")
def start():
    return "Welcome to API"

@app.get("/movie-list")
async def getMovieList():
    movies = pd.read_csv('movies.dat',sep='::',header=None, engine='python',encoding="ISO-8859-1")
    return movies.values.tolist()


#Extra => try catch with bad data
@app.post("/predict_movies", status_code=200)
def getPrediction(file: UploadFile = File(...)):
    data = preprocess_data(file)
    url = 'http://2b0d1556-471f-449b-8de8-383b6f303fda.westeurope.azurecontainer.io/score'
    api_key = '' # Replace this with the API key for the web service
    body = str.encode(json.dumps({"data":[data]}))
    headers = {'Content-Type':'application/json', 'Authorization':('Bearer '+ api_key)}
    req = urllib.request.Request(url, body, headers)
    try:
        response = urllib.request.urlopen(req)
        result = response.read()
    except urllib.error.HTTPError as error:
        print("The request failed with status code: " + str(error.code))
        print(error.info())
        print(json.loads(error.read().decode("utf8", 'ignore')))
        return error.code
    movies = postprocess_data(json.loads(result.decode('utf8')))
    return movies 
    

def preprocess_data(file):
    user_movies = pd.read_csv(StringIO(str(file.file.read(), 'utf-8')), encoding='utf-16',header=None)
    movies = pd.read_csv('movies.dat',sep='::',header=None, engine='python',encoding="ISO-8859-1")
    length = movies.iloc[-1,0]
    data = [0.]*length
    for row in user_movies.iterrows():
        data[row[1][0]-1]=float(row[1][1]/5)     
    #user_movies = pd.read_csv(data,sep='::',header=None, engine='python',encoding='utf-16')
    return data
  
def postprocess_data(response):
    movies = pd.read_csv('movies.dat',sep='::',header=None, engine='python',encoding="ISO-8859-1")
    result = np.array(response['result']).flatten()
    top_10_indeces = np.array(result).argsort()[-10:][::-1]
    top_movies = []
    for i in top_10_indeces:
        top_movies.append(re.sub(r"[\[\]]+","",str(movies.loc[movies[0]==i][1].values)))
    return top_movies

# Run the script
#if __name__ == "__main__":
#    uvicorn.run(app)