from fastapi import FastAPI
import httpx
import requests
import os
from dotenv import load_dotenv
from fastapi.responses import FileResponse, JSONResponse
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import json
import openai
from fastapi_cache import FastAPICache
from fastapi_cache.backends.inmemory import InMemoryBackend
from fastapi_cache.decorator import cache

load_dotenv()  # Load environment variables

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY")
GAS_API_KEY = os.getenv("GAS_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

load_dotenv()  # Load environment variables

app = FastAPI()


@app.on_event("startup")
async def startup_event() -> None:
    """Initialize caching backend."""
    FastAPICache.init(InMemoryBackend(), prefix="goscenic-cache")


# Load API keys
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY")
GAS_API_KEY = os.getenv("GAS_API_KEY")


@app.get("/")
def read_root():
    return {"message": "Welcome to the GoScenic API!"}


@app.get("/distance")
@cache(expire=3600)
async def get_distance(origin: str, destination: str):
    url = (
        "https://maps.googleapis.com/maps/api/distancematrix/json"
        f"?origins={origin}&destinations={destination}&key={GOOGLE_API_KEY}"
    )
    async with httpx.AsyncClient() as client:
        response = await client.get(url)
    return response.json()


@app.get("/directions")
@cache(expire=3600)
async def get_directions(origin: str, destination: str):
    url = (
        "https://maps.googleapis.com/maps/api/directions/json"
        f"?origin={origin}&destination={destination}&key={GOOGLE_API_KEY}"
    )
    async with httpx.AsyncClient() as client:
        response = await client.get(url)
    return response.json()


@app.get("/config")
def get_config():
    return {
        "GoogleAPI": bool(GOOGLE_API_KEY),
        "OpenWeatherAPI": bool(OPENWEATHER_API_KEY),
        "GasAPI": bool(GAS_API_KEY),
    }


@app.get("/trip-cost")
def calculate_trip_cost(origin: str, destination: str, mileage: float = 25.0):
    """Calculate trip cost based on distance, fuel price, lodging, and food."""

    # 1. Get Trip Distance from Google Maps API
    distance_url = f"https://maps.googleapis.com/maps/api/distancematrix/json?origins={origin}&destinations={destination}&key={GOOGLE_API_KEY}"
    distance_response = requests.get(distance_url).json()

    try:
        distance_meters = distance_response["rows"][0]["elements"][0][
            "distance"
        ]["value"]
        distance_miles = distance_meters / 1609.34  # Convert meters to miles
    except KeyError:
        return {
            "error": "Unable to calculate distance. Check the origin and destination."
        }

    # 2. Get Gas Price (Using Default Value or Gas API)
    gas_price = 4.00  # Default value per gallon
    try:
        gas_price_url = (
            f"https://api.gasbuddy.com/api/v1/gas-prices?api_key={GAS_API_KEY}"
        )
        gas_response = requests.get(gas_price_url).json()
        gas_price = gas_response.get(
            "average_gas_price", 4.00
        )  # Default to $4.00 if no response
    except Exception:
        pass  # Use default gas price

    # 3. Calculate Fuel Cost
    fuel_needed = distance_miles / mileage  # Gallons required
    fuel_cost = fuel_needed * gas_price

    # 4. Calculate Lodging & Food Costs
    travel_days = max(
        1, distance_miles // 500
    )  # Assume 1 night stay per 500 miles
    lodging_cost = travel_days * 100  # $100 per night
    food_cost = travel_days * 3 * 15  # $15 per meal, 3 meals per day

    # 5. Calculate Total Trip Cost
    total_cost = fuel_cost + lodging_cost + food_cost

    return {
        "distance_miles": round(distance_miles, 2),
        "fuel_cost": round(fuel_cost, 2),
        "lodging_cost": round(lodging_cost, 2),
        "food_cost": round(food_cost, 2),
        "total_cost": round(total_cost, 2),
    }


@app.get("/lodging")
def get_lodging(location: str, radius: int = 5000):
    """Get hotels near a location using Google Places API."""
    url = f"https://maps.googleapis.com/maps/api/place/nearbysearch/json?location={location}&radius={radius}&type=lodging&key={GOOGLE_API_KEY}"
    response = requests.get(url).json()

    hotels = []
    for place in response.get("results", []):
        hotels.append(
            {
                "name": place.get("name"),
                "address": place.get("vicinity"),
                "rating": place.get("rating", "N/A"),
                "user_ratings_total": place.get("user_ratings_total", 0),
            }
        )

    return {"lodging": hotels}


@app.get("/restaurants")
def get_restaurants(location: str, radius: int = 5000):
    """Get restaurants near a location using Google Places API."""
    url = f"https://maps.googleapis.com/maps/api/place/nearbysearch/json?location={location}&radius={radius}&type=restaurant&key={GOOGLE_API_KEY}"
    response = requests.get(url).json()

    restaurants = []
    for place in response.get("results", []):
        restaurants.append(
            {
                "name": place.get("name"),
                "address": place.get("vicinity"),
                "rating": place.get("rating", "N/A"),
                "user_ratings_total": place.get("user_ratings_total", 0),
            }
        )

    return {"restaurants": restaurants}


@app.get("/download-itinerary")
def download_itinerary(
    origin: str, destination: str, mileage: float = 25.0, format: str = "json"
):
    """Generate and download trip itinerary as JSON or PDF"""

    # Fetch trip cost details
    trip_cost = calculate_trip_cost(origin, destination, mileage)

    # Fetch lodging & food suggestions
    lodging_data = get_lodging(origin)
    restaurant_data = get_restaurants(origin)

    itinerary = {
        "trip_details": trip_cost,
        "lodging": lodging_data.get("lodging", []),
        "restaurants": restaurant_data.get("restaurants", []),
    }

    if format == "json":
        # Save as JSON file
        filename = "itinerary.json"
        with open(filename, "w") as json_file:
            json.dump(itinerary, json_file, indent=4)

        return FileResponse(
            filename, media_type="application/json", filename=filename
        )

    elif format == "pdf":
        # Save as PDF file
        filename = "itinerary.pdf"
        c = canvas.Canvas(filename, pagesize=letter)
        c.setFont("Helvetica", 12)

        y = 750
        c.drawString(100, y, f"Trip Itinerary: {origin} to {destination}")
        y -= 20
        c.drawString(100, y, f"Distance: {trip_cost['distance_miles']} miles")
        y -= 20
        c.drawString(100, y, f"Total Cost: ${trip_cost['total_cost']}")
        y -= 40

        c.drawString(100, y, "Lodging Suggestions:")
        for hotel in lodging_data["lodging"]:
            y -= 20
            c.drawString(120, y, f"- {hotel['name']} ({hotel['rating']}⭐)")

        y -= 40
        c.drawString(100, y, "Restaurant Suggestions:")
        for restaurant in restaurant_data["restaurants"]:
            y -= 20
            c.drawString(
                120, y, f"- {restaurant['name']} ({restaurant['rating']}⭐)"
            )

        c.save()

        return FileResponse(
            filename, media_type="application/pdf", filename=filename
        )

    return JSONResponse(
        content={"error": "Invalid format. Use 'json' or 'pdf'."},
        status_code=400,
    )


@app.get("/weather-along-route")
@cache(expire=1800)
async def get_weather_along_route(origin: str, destination: str):
    """Fetch weather forecasts along the trip route."""

    # Step 1: Get waypoints along the route from Google Directions API
    directions_url = (
        "https://maps.googleapis.com/maps/api/directions/json"
        f"?origin={origin}&destination={destination}&key={GOOGLE_API_KEY}"
    )
    async with httpx.AsyncClient() as client:
        directions_response = (await client.get(directions_url)).json()

    if (
        "routes" not in directions_response
        or not directions_response["routes"]
    ):
        return {"error": "Unable to get route directions."}

    # Extract waypoints (latitude, longitude) from route
    waypoints = []
    for step in directions_response["routes"][0]["legs"][0]["steps"]:
        lat = step["end_location"]["lat"]
        lng = step["end_location"]["lng"]
        waypoints.append(f"{lat},{lng}")

    # Step 2: Get weather forecasts for each waypoint
    weather_forecasts = []
    async with httpx.AsyncClient() as client:
        for waypoint in waypoints[
            :5
        ]:  # Limit to 5 waypoints to optimize API usage
            weather_url = (
                "https://api.openweathermap.org/data/2.5/weather"
                f"?lat={waypoint.split(',')[0]}&lon={waypoint.split(',')[1]}"
                f"&appid={OPENWEATHER_API_KEY}&units=imperial"
            )
            weather_response = (await client.get(weather_url)).json()

            weather_forecasts.append(
                {
                    "location": waypoint,
                    "temperature": weather_response.get("main", {}).get(
                        "temp", "N/A"
                    ),
                    "condition": weather_response.get("weather", [{}])[0].get(
                        "description", "N/A"
                    ),
                    "wind_speed": weather_response.get("wind", {}).get(
                        "speed", "N/A"
                    ),
                }
            )

    return {"weather_forecasts": weather_forecasts}


@app.get("/scenic-route")
@cache(expire=3600)
async def get_scenic_route(origin: str, destination: str):
    """Fetch scenic route with scenic places along the way."""

    # Step 1: Get multiple routes from Google Directions API
    directions_url = (
        "https://maps.googleapis.com/maps/api/directions/json"
        f"?origin={origin}&destination={destination}&alternatives=true&key={GOOGLE_API_KEY}"
    )
    async with httpx.AsyncClient() as client:
        directions_response = (await client.get(directions_url)).json()

    if (
        "routes" not in directions_response
        or not directions_response["routes"]
    ):
        return {"error": "Unable to get route directions."}

    # Step 2: Analyze each route for scenic landmarks
    scenic_routes = []
    async with httpx.AsyncClient() as client:
        for route in directions_response["routes"]:
            waypoints = []
            for step in route["legs"][0]["steps"]:
                lat = step["end_location"]["lat"]
                lng = step["end_location"]["lng"]
                waypoints.append(f"{lat},{lng}")

            # Step 3: Find scenic landmarks along the route using Google Places API
            scenic_places = []
            scenic_score = 0
            for waypoint in waypoints[
                :5
            ]:  # Limit to 5 waypoints for optimization
                places_url = (
                    "https://maps.googleapis.com/maps/api/place/nearbysearch/json"
                    f"?location={waypoint}&radius=10000&type=park|tourist_attraction|scenic_viewpoint|natural_feature&key={GOOGLE_API_KEY}"
                )
                places_response = (await client.get(places_url)).json()

                for place in places_response.get("results", []):
                    scenic_places.append(
                        {
                            "name": place.get("name"),
                            "location": place.get(
                                "vicinity", "Unknown Location"
                            ),
                            "rating": place.get("rating", "N/A"),
                        }
                    )

                scenic_score += len(places_response.get("results", []))

        # Step 4: Save route data
        scenic_routes.append(
            {
                "route_summary": route["summary"],
                "distance_miles": round(
                    route["legs"][0]["distance"]["value"] / 1609.34, 2
                ),  # Convert meters to miles
                "duration_minutes": round(
                    route["legs"][0]["duration"]["value"] / 60, 2
                ),
                "scenic_score": scenic_score,  # Higher score = more scenic
                "scenic_places": scenic_places,  # List of scenic places along the route
            }
        )

    # Step 5: Sort routes by highest scenic score
    scenic_routes = sorted(
        scenic_routes, key=lambda x: x["scenic_score"], reverse=True
    )

    return {
        "recommended_scenic_route": scenic_routes[0],
        "all_routes": scenic_routes,
    }


# Load OpenAI API key
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
client = openai.OpenAI(api_key=OPENAI_API_KEY)


@app.get("/chatbot")
@app.post("/chatbot")
def chatbot(prompt: str, model: str = "gpt-4-turbo"):
    """AI Chatbot for trip planning using the latest OpenAI model."""

    if not OPENAI_API_KEY:
        return {"error": "OpenAI API key is missing."}

    # Fallback to GPT-3.5-turbo if GPT-4-turbo is not available
    available_models = ["gpt-4-turbo", "gpt-3.5-turbo"]
    if model not in available_models:
        model = "gpt-3.5-turbo"

    try:
        response = client.chat.completions.create(
            model=model,
            messages=[
                {
                    "role": "system",
                    "content": "You are a helpful travel assistant.",
                },
                {"role": "user", "content": prompt},
            ],
        )
        return {
            "model_used": model,
            "response": response.choices[0].message.content,
        }
    except openai.OpenAIError as e:
        return {"error": str(e)}


# Run with: uvicorn main:app --reload
