from dataclasses import dataclass
from typing import Optional, List
import requests
import json


@dataclass
class Seat:
    seat_name: str
    seat_number: str
    coach: str
    booking_reference: str


class TrainDataAdapter:
    URL = "http://127.0.0.1:8081"

    def get_train_data(self, train_id: str) -> Optional[List[Seat]]:
        response = requests.get(self.URL + f"/data_for_train/{train_id}")
        train_data = response.json()
        if "seats" not in train_data:
            return None
        seats = []
        for seat_name, seat_data in train_data["seats"].items():
            seats.append(
                Seat(
                    seat_name,
                    seat_data.get("seat_number"),
                    seat_data.get("coach"),
                    seat_data.get("booking_reference"),
                )
            )

        return seats

    def reserve(self, train_id: str, seats: List[str], booking_reference: str) -> str:
        form_data = {
            "train_id": train_id,
            "seats": json.dumps(seats),
            "booking_reference": booking_reference,
        }
        response = requests.post(self.URL + "/reserve", data=form_data)
        return f"situation after reservation: {response.json()}"


class BookingReferenceClient:
    URL = "http://127.0.0.1:8082"

    def get_booking_reference(self) -> str:
        response = requests.get(self.URL + "/booking_reference")
        return response.text
