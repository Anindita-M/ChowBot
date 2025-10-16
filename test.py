from fastapi import FastAPI, Query, HTTPException, Depends, Request
from fastapi.responses import JSONResponse
from dotenv import load_dotenv
import os
import httpx
import google.auth
import google.auth.transport.requests
import requests
import asyncio

app = FastAPI()

@app.get("/get_location_from_ip")
async def get_location_from_ip(request: Request):
    ip = request.client.host  # Get client IP
    async with httpx.AsyncClient() as client:
        resp = await client.get(f"https://ipinfo.io/{ip}/json")
    data = resp.json()
    lat, lon = map(float, data["loc"].split(","))

    print(lat,lon)

