import random

from collections import defaultdict
from datetime import date
from typing import Dict, List, Optional

import requests

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel


app = FastAPI()


@app.get("/schedule/{match_date}")
async def get_match(match_date: date) -> List[Dict[str, str]]:
    match_date_str = match_date.isoformat()

    return per_date_matches.get(match_date_str, (lambda: [])())


class ReservationResponse(BaseModel):
    success: bool
    message: str
    game_id: str
    reservation_id: Optional[str] = None
    seat_number: Optional[str] = None


# seat reservation logic
def reserve_seat(game_id: str) -> Optional[tuple]:
    if random.random() < 0.5:
        return ("reservation123", "42A")
    else:
        return None


@app.post("/reserve-seat/{game_id}", response_model=ReservationResponse)
async def reserve_seat_endpoint(game_id: str):
    result = reserve_seat(game_id)

    if result:
        reservation_id, seat_number = result
        return ReservationResponse(
            success=True,
            message="Seat reserved successfully.",
            game_id=game_id,
            reservation_id=reservation_id,
            seat_number=seat_number,
        )
    else:
        raise HTTPException(status_code=409, detail="No seats available for the requested game.")


def prepare_nba_schedule_data():
    response = requests.get(
        "https://data.nba.com/data/10s/v2015/json/mobile_teams/nba/2023/league/00_full_schedule_week_tbds.json"
    )

    per_date_matches = defaultdict(list)
    for per_month_data in response.json()["lscd"]:
        for game_data in per_month_data["mscd"]["g"]:
            processed_game_data = {
                "ID": game_data["gid"],
                "Home team": game_data["h"]["tn"],
                "Away team": game_data["v"]["tn"],
            }
            per_date_matches[game_data["gdtutc"]].append(processed_game_data)

    return per_date_matches


if __name__ == "__main__":
    per_date_matches = prepare_nba_schedule_data()

    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
