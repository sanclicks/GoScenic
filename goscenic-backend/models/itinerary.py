from pydantic import BaseModel
from typing import Literal

class ItineraryRequest(BaseModel):
    start_location: str
    end_location: str
    total_budget: float
    num_days: int
    num_people: int
    car_mpg: float
    car_year: int
    car_model: str
    lodging_type: Literal['camping', 'motel', 'hotel']
    food_pref: Literal['veg', 'non-veg', 'vegan', 'any']
