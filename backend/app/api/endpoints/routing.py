from fastapi import APIRouter
from typing import List
from decimal import Decimal
from datetime import datetime, timedelta

router = APIRouter()

@router.post("/options")
async def get_routes(request: dict):
    origin = request.get("origin_country", "CN")
    destination = request.get("destination_port", "USLAX")
    container_type = request.get("container_type", "FCL")
    
    base_cost = 2500 if container_type == "FCL" else 1200
    
    routes = [
        {
            "carrier": "Maersk",
            "service_name": "Ocean Express",
            "origin": f"{origin}-Shanghai",
            "destination": destination,
            "transit_days": 18,
            "freight_cost": float(base_cost + Decimal("200")),
            "reliability_score": 0.92,
            "co2_emissions_kg": 1200,
            "departure_dates": [(datetime.now() + timedelta(days=i*3)).isoformat() for i in range(1, 4)]
        },
        {
            "carrier": "MSC",
            "service_name": "Economy Ocean",
            "origin": f"{origin}-Ningbo",
            "destination": destination,
            "transit_days": 24,
            "freight_cost": float(base_cost - Decimal("300")),
            "reliability_score": 0.88,
            "co2_emissions_kg": 1150,
            "departure_dates": [(datetime.now() + timedelta(days=i*5)).isoformat() for i in range(1, 4)]
        },
        {
            "carrier": "COSCO + Rail",
            "service_name": "Prince Rupert Express",
            "origin": f"{origin}-Shanghai",
            "destination": "Prince Rupert, CA",
            "transit_days": 15,
            "freight_cost": float(base_cost + Decimal("700")),
            "reliability_score": 0.85,
            "co2_emissions_kg": 1300,
            "departure_dates": [(datetime.now() + timedelta(days=2)).isoformat()],
            "note": "Avoids US port congestion, potential Section 301 savings"
        }
    ]
    
    # Sort by freight cost
    routes.sort(key=lambda x: x["freight_cost"])
    
    return {
        "routes": routes,
        "best_value": routes[0],
        "fastest": min(routes, key=lambda x: x["transit_days"]),
        "most_reliable": max(routes, key=lambda x: x["reliability_score"])
    }
