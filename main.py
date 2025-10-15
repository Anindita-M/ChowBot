from fastapi import FastAPI, Query, HTTPException, Depends, Request
from fastapi.responses import JSONResponse
from dotenv import load_dotenv
import os
import httpx


app = FastAPI()

load_dotenv()

FOURSQUAREAPIKEY = os.getenv("FOURSQUARE_API_KEY")
GOOGLEGEOCODEAPIKEY = os.getenv("GOOGLE_GEOCODING_API_KEY")

headers = {"accept": "application/json",
           "Authorization": f"Bearer {FOURSQUAREAPIKEY}",
           "X-Places-Api-Version": "2025-06-17"}

print(headers)

@app.post("/maps.googleapis.com/maps/api/geocode/json")
async def geocode(location:str,key:str=GOOGLEGEOCODEAPIKEY):
    
    params = {
        "address" : location,
        "key" : key
    }
    async with httpx.AsyncClient() as client:
        response = await client.get("https://maps.googleapis.com/maps/api/geocode/json",params=params)
        data = response.json()

    if response.status_code==200 and data["results"]:
        loc = data["results"][0]["geometry"]["location"]
        return loc["lat"],loc['lng']
    
    return None

@app.get("/")
async def root():
    return {"message":"Welcome to ChowBot! Search to find places to eat"}

@app.post("/dialogflow/webhook")
async def dialogflow_webhook(request: Request):

    body = await request.json()

    try:
        intent_name = body["queryResult"]["intent"]["displayName"]
        params = body["queryResult"]["parameters"]
        cuisine = params["cuisine"]
        location = f"{params['location']['street-address']},{params['location']['city']},{params['location']['country']}"

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
            "sort" : "RATING"
        }

        async with httpx.AsyncClient() as client:
            response = await client.get("https://places-api.foursquare.com/places/search", headers=headers, params=query_params)

        if response.status_code!=200:
            return JSONResponse({"fulfilment_text":f"Error from FourSquareAPI, {response.json()}"})

        if not response:
            return JSONResponse({f"fulfilment_text":"No places found near {location}"})
        
        results = response.json()["results"]

        message = f"Here are some places in {location}: \n\n"
        
        for place in results:
            
            curr_place = ""
            location = place["location"]["formatted_address"]
            name = place["name"]

            curr_place = f"•{name} :- {location}"
            message += curr_place + "\n\n"

        return JSONResponse(content={
        "fulfillmentMessages": [
            {
                "text": {
                    "text": message.splitlines()
                }
            }
        ]
    })
    
    except Exception as e:
        return JSONResponse({
            "fulfilmentText": f"Someting went wrong processing your request.{results}"
        })


        


        
