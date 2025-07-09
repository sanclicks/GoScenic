from models.itinerary import ItineraryRequest

async def generate_itinerary(req: ItineraryRequest):
    # Placeholder for real APIs (Google, GasBuddy, Yelp, etc.)
    route = {
        "miles": 2200,
        "stops": ["Columbus, OH", "Denver, CO", "Moab, UT"]
    }

    gas_price = 3.6  # Static for now
    total_gas_cost = (route["miles"] / req.car_mpg) * gas_price

    lodging_per_night = {
        "camping": 30, "motel": 80, "hotel": 150
    }[req.lodging_type]

    lodging_total = lodging_per_night * req.num_days
    food_total = 40 * req.num_people * req.num_days

    total_estimated = total_gas_cost + lodging_total + food_total

    return {
        "route": route,
        "gas_cost": round(total_gas_cost, 2),
        "lodging_total": lodging_total,
        "food_total": food_total,
        "total_estimated": round(total_estimated, 2),
        "budget_remaining": round(req.total_budget - total_estimated, 2)
    }
