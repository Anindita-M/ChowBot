from fastapi import FastAPI, Query, HTTPException, Depends, Request
from fastapi.responses import JSONResponse
from dotenv import load_dotenv
import os
import httpx


app = FastAPI()

load_dotenv()

FOURSQUAREAPIKEY = os.getenv("FOUR_SQUARE_API_KEY")
GOOGLEGEOCODEAPIKEY = os.getenv("GOOGLE_GEOCODING_API_KEY")

headers = {"Accept": "application/json",
           "Authorization": FOURSQUAREAPIKEY}

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
        place_type = params["place_type"]
        location = params["location"]

        if not location or not place_type:
            return JSONResponse({"fulfilment_text":"Please enter a location and a place type"})
        
        coords = await geocode(location)

        if not coords:

            return JSONResponse({"fulfilment_text":"Can't find your specified location"})
        
        lat, lon = coords
        
        query_params = {
            "query" : place_type,
            "ll" : f"{lat},{lon}",
            "radius" : 10000,
            "limit" : 5,
            "sort" : "rating"
        }

        async with httpx.AsyncClient() as client:
            response = await client.get("https://places-api.foursquare.com/places/search", params=query_params,headers=headers)

        if response.status_code!=200:
            return JSONResponse({"fulfilment_text":"Error from FourSquareAPI"})

        if not response:
            return JSONResponse({f"fulfilment_text":"No places found near {location}"})
        
        results = response["results"]

        message = f"Here are some places in location {location}"
        
        for place in results:
            
            curr_place = ""
            location = place["location"]["address"] + place["location"]["locality"] + place["location"]["region"]
            hours = place["hours"]["display"]
            open_now = place["hours"]["open_now"]
            name = place["name"]
            link = place["link"]
            price = place["price"]
            rating = place["rating"]
            description = place["description"]

            curr_place = f"•{name} :- {location}\n{description}\n{link}\n{price}\n{rating}\n{hours}\n{open_now}"
            message += curr_place

        return message
    
    except Exception as e:
        return JSONResponse({
            "fulfilmentText": "Someting went wrong processing your request"
        })


        


        
