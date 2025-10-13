import httpx
import asyncio

SERVICE_KEY = "Bearer 2IJJRA05HYC1JGHV0JALCCMAQ2RFAO41JJFQVNOFKSEXZNUM"  # Use same one that worked with requests

async def search_places():
    headers = {
        "Authorization": SERVICE_KEY,
        "accept": "application/json",
        "X-Places-Api-Version": "2025-06-17"
    }

    params = {
        "query": "Italian",
        "ll": "18.9582,72.8321",
        "radius": 10000,
        "limit": 5,
        "sort": "RATING"
    }

    async with httpx.AsyncClient() as client:
        response = await client.get(
            "https://places-api.foursquare.com/places/search",
            headers=headers,
            params=params
        )

    if response.status_code == 401:
        print("⚠️ 401 Unauthorized — headers may not be applied correctly.")
        print("📤 Sent headers:", headers)
        print("📤 Sent params:", params)
        print("📩 Response:", response.text)
        raise Exception("Unauthorized")
    
    print(response.json())

    return response.json()

asyncio.run(search_places())



