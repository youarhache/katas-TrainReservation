import json
from typing import List, Optional, Union
from dataclasses import dataclass, asdict
from flask import Flask, request
from train_services_adapters import Seat
from train_services_adapters import TrainDataAdapter, BookingReferenceClient

app = Flask(__name__)


@dataclass
class Reservation:
    train_id: str
    seats: List[str]
    booking_reference: str


class TicketOffice:
    MAXIMUM_OCCUPATION_PERCENTAGE = 70

    def __init__(
        self,
        train_service_adapter: TrainDataAdapter,
        booking_reference_adapter: BookingReferenceClient,
    ) -> None:
        self.train_service_adapter = train_service_adapter
        self.booking_reference_adapter = booking_reference_adapter

    def make_reservation(self, train_id: str, seat_count: int) -> Optional[Reservation]:
        if seat_count == 0:
            return None

        seats = self.train_service_adapter.get_train_data(train_id)
        if not seats:
            return None

        empty_seats = [seat for seat in seats if not seat.booking_reference]
        if (
            self.compute_seats_occupation_persentage(seats, empty_seats, seat_count)
            > self.MAXIMUM_OCCUPATION_PERCENTAGE
        ):
            return None

        best_coach_empty_seats = self.get_best_coach_empty_seats(seat_count, seats)

        if not best_coach_empty_seats:
            return None
        # Since the coach might have more empty seats than we need, we select only the first `seat_count`
        seats_to_reserve = best_coach_empty_seats[:seat_count]
        booking_reference = self.booking_reference_adapter.get_booking_reference()
        self.train_service_adapter.reserve(
            train_id=train_id,
            seats=seats_to_reserve,
            booking_reference=booking_reference,
        )
        return Reservation(
            train_id, seats=seats_to_reserve, booking_reference=booking_reference
        )

    def get_best_coach_empty_seats(
        self, seat_count: int, train_seats: List[Seat]
    ) -> Optional[List[str]]:
        best_seats_occupation = (
            100.0  # intitialise occupation to maximum == 100% occupation
        )
        best_coach_empty_seats = None
        coaches = list({seat.coach for seat in train_seats})

        for coach in coaches:
            coach_seats = [
                seat.seat_name for seat in train_seats if seat.coach == coach
            ]
            empty_coach_seats = [
                seat.seat_name
                for seat in train_seats
                if not seat.booking_reference and seat.coach == coach
            ]

            if seat_count <= len(empty_coach_seats):
                new_seats_occupation = self.compute_seats_occupation_persentage(
                    coach_seats, empty_coach_seats
                )

                if best_seats_occupation > new_seats_occupation:
                    best_seats_occupation = new_seats_occupation
                    best_coach_empty_seats = empty_coach_seats

        return best_coach_empty_seats

    @staticmethod
    def compute_seats_occupation_persentage(
        all_seats: Union[List[str], List[Seat]],
        empty_seats: Union[List[str], List[Seat]],
        nb_seats_to_book: int = 0,
    ) -> float:
        return 100 * (1 - (len(empty_seats) - nb_seats_to_book) / len(all_seats))


@app.route("/reserve", methods=["POST"])
def reserve() -> Optional[str]:
    train_id = request.form["train_id"]
    seat_count = request.form["seat_count"]
    ticket_office = TicketOffice(TrainDataAdapter(), BookingReferenceClient())
    reservation = ticket_office.make_reservation(train_id, int(seat_count))
    if not reservation:
        return None
    return json.dumps(asdict(reservation))


if __name__ == "__main__":
    app.config["SERVER_NAME"] = "127.0.0.1:8083"
    app.config["DEBUG"] = True
    app.run()
