from fastapi import FastAPI, Query, HTTPException, Depends, Request, BackgroundTasks
from fastapi.responses import JSONResponse
from dotenv import load_dotenv
import os
import httpx
import google.auth
import google.auth.transport.requests
import requests

app = FastAPI()

load_dotenv()

FOURSQUAREAPIKEY = os.getenv("FOURSQUARE_API_KEY")
GOOGLEGEOCODEAPIKEY = os.getenv("GOOGLE_GEOCODING_API_KEY")

#headers_geocoding = {"Authorization": f"Bearer {access_token}"}

headers_foursquare = {"accept": "application/json",
           "Authorization": f"Bearer {FOURSQUAREAPIKEY}",
           "X-Places-Api-Version": "2025-06-17"}

def slow_task(data):

    import time
    time.sleep(10)
    print("Finished slow task")

@app.post("/maps.googleapis.com/maps/api/geocode/json")
async def geocode(location:str):
    
    params = {
        "address" : location,
        "key": GOOGLEGEOCODEAPIKEY
    }
    async with httpx.AsyncClient(timeout=3.0) as client:
        response = await client.get("https://maps.googleapis.com/maps/api/geocode/json",params=params)
        data = response.json()

    if response.status_code==200 and data["results"]:
        loc = data["results"][0]["geometry"]["location"]
        return loc["lat"],loc['lng']
    
    return None

@app.get("/")
async def root():
    return {"message":"Welcome to ChowBot! Search to find places to eat"}

async def process_dialogflow(body):

    try:
        intent_name = body["queryResult"]["intent"]["displayName"]
        params = body["queryResult"]["parameters"]
        cuisine = params["cuisine"]
        location = f"{params['location']['street-address']},{params['location']['business-name']}{params['location']['subadmin-area']}{params['location']['city']},{params['location']['country']}"

        if not location or not cuisine:
            return JSONResponse({"fulfilment_text":"Please enter a location and a place type"})
        
        coords = await geocode(location)

        if not coords:

            return JSONResponse({"fulfilment_text":f"Can't find {location}"})
        
        lat, lon = coords
        
        query_params = {
            "query" : cuisine,
            "ll" : f"{lat},{lon}",
            "radius" : 10000,
            "limit" : 5,
            "sort" : "POPULARITY"
        }

        async with httpx.AsyncClient(timeout=3.0) as client:
            response = await client.get("https://places-api.foursquare.com/places/search", headers=headers_foursquare, params=query_params)

        if response.status_code!=200:
            return JSONResponse({"fulfilment_text":f"Error from FourSquareAPI, {response.json()}"})

        if not response:
            return JSONResponse({f"fulfilment_text":"No places found near {location}"})
        
        results = response.json()["results"]

        message = [f"Here are some places in {location}: \n"]
        
        for place in results:
            
            location = place["location"]["formatted_address"]
            name = place["name"]

            message.append(f"• **{name}**:-{location} \n")

        return JSONResponse(content={
        "fulfillmentMessages": [
            {
                "text": {
                    "text": message
                }
            }
        ]
    })
    
    except Exception as e:
        return JSONResponse({
            "fulfilmentText": f"Someting went wrong processing your request.{results}"
        })
   
@app.post("/dialogflow/webhook")
async def dialogflow_webhook(request: Request, background_tasks: BackgroundTasks):
    body = await request.json()
    background_tasks.add_task(process_dialogflow, body)

    # Respond immediately so Dialogflow doesn’t time out
    #return JSONResponse(content={
     #   "fulfillmentMessages": [
      #      {
       #         "text": {
        #            "text": ["Got it! Looking up places for you... 🍽️"]
         #       }
          #  }
        #]
    #})



        


        
