from dotenv import load_dotenv
import os
import google.auth
import google.auth.transport.requests
import httpx
from fastapi import FastAPI
import asyncio

load_dotenv()  # loads .env file

app = FastAPI()

credentials, project = google.auth.default(
    scopes=["https://www.googleapis.com/auth/cloud-platform"]
)
credentials.refresh(google.auth.transport.requests.Request())

access_token = credentials.token
headers_geocoding = {"Authorization": f"Bearer {access_token}"}

@app.post("/maps.googleapis.com/maps/api/geocode/json")
async def geocode():
    params = {"address": "Mumbai"}
    async with httpx.AsyncClient() as client:
        response = await client.get(
            "https://maps.googleapis.com/maps/api/geocode/json",
            headers=headers_geocoding,
            params=params
        )
        data = response.json()

        print(data)
    if response.status_code == 200 and data["results"]:
        loc = data["results"][0]["geometry"]["location"]
        print(loc)
        return loc["lat"], loc["lng"]
    return None

asyncio.run(geocode())

