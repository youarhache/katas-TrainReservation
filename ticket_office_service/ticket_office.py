import json
from dataclasses import dataclass
from train_services_adapters import TrainDataAdapter, BookingReferenceAdapter


@dataclass
class Reservation:
    train_id: str
    seats: list
    booking_reference: str


class TicketOffice:
    MAXIMUM_OCCUPATION_PERCENTAGE = 70

    def __init__(
        self,
        train_service_adapter: TrainDataAdapter,
        booking_reference_adapter: BookingReferenceAdapter,
    ) -> None:
        self.train_service_adapter = train_service_adapter
        self.booking_reference_adapter = booking_reference_adapter

    def reserve(self, train_id: str, seat_count: str) -> str:
        reservation = self.make_reservation(train_id, int(seat_count))
        if not reservation:
            return None
        return json.dumps(reservation.__dict__)

    def make_reservation(self, train_id: str, seat_count: int):
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

        if best_coach_empty_seats:

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

    def get_best_coach_empty_seats(self, seat_count, train_seats):
        best_seats_occupation = (
            100  # intitialise occupation to maximum == 100% occupation
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
    def compute_seats_occupation_persentage(all_seats, empty_seats, nb_seats_to_book=0):
        return 100 * (1 - (len(empty_seats) - nb_seats_to_book) / len(all_seats))


if __name__ == "__main__":
    """Deploy this class as a web service using CherryPy"""
    import cherrypy

    TicketOffice.reserve.exposed = True
    cherrypy.config.update({"server.socket_port": 8083})
    cherrypy.quickstart(TicketOffice(TrainDataAdapter(), BookingReferenceAdapter()))
