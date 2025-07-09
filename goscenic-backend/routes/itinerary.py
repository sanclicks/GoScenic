from fastapi import APIRouter
from models.itinerary import ItineraryRequest
from services.planner import generate_itinerary

router = APIRouter()

@router.post("/itinerary")
async def plan_trip(req: ItineraryRequest):
    return await generate_itinerary(req)
