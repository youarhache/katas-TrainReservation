from unittest.mock import patch
from ticket_office import TicketOffice, Reservation
from train_services_adapters import Seat


@patch("ticket_office.BookingReferenceClient")
@patch("ticket_office.TrainDataAdapter")
def test_should_return_none_when_reserve_0_seat(
    mock_train_data_adapter, mock_booking_ref_adapter
):
    ticket_office = TicketOffice(
        train_service_adapter=mock_train_data_adapter.return_value,
        booking_reference_adapter=mock_booking_ref_adapter.return_value,
    )

    result = ticket_office.make_reservation(train_id="express_2000", seat_count=0)

    assert result is None


@patch("ticket_office.BookingReferenceClient")
@patch("ticket_office.TrainDataAdapter")
def test_should_return_none_when_train_not_found(
    mock_train_data_adapter, mock_booking_ref_adapter
):
    no_train_data = {}
    mock_train_data_adapter.return_value.get_train_data.return_value = no_train_data
    ticket_office = TicketOffice(
        train_service_adapter=mock_train_data_adapter.return_value,
        booking_reference_adapter=mock_booking_ref_adapter.return_value,
    )

    result = ticket_office.make_reservation(train_id="fake_train", seat_count=1)

    assert result is None


@patch("ticket_office.BookingReferenceClient")
@patch("ticket_office.TrainDataAdapter")
def test_should_return_none_when_full_train(
    mock_train_data_adapter, mock_booking_ref_adapter
):
    empty_train_data = [
        Seat(seat_name="1A", seat_number="1", coach="A", booking_reference="75bcd15"),
        Seat(seat_name="2A", seat_number="2", coach="A", booking_reference="75bcd15"),
    ]
    mock_train_data_adapter.return_value.get_train_data.return_value = empty_train_data
    mock_booking_ref_adapter.return_value.get_booking_reference.return_value = "75bcd15"
    ticket_office = TicketOffice(
        train_service_adapter=mock_train_data_adapter.return_value,
        booking_reference_adapter=mock_booking_ref_adapter.return_value,
    )

    result = ticket_office.make_reservation(train_id="express_2000", seat_count=1)

    assert result is None


@patch("ticket_office.BookingReferenceClient")
@patch("ticket_office.TrainDataAdapter")
def test_should_reserve_seat_when_empty_train(
    mock_train_data_adapter, mock_booking_ref_adapter
):
    empty_train_data = [
        Seat(seat_name="1A", seat_number="1", coach="A", booking_reference=""),
        Seat(seat_name="2A", seat_number="2", coach="A", booking_reference=""),
    ]
    mock_train_data_adapter.return_value.get_train_data.return_value = empty_train_data
    mock_booking_ref_adapter.return_value.get_booking_reference.return_value = "75bcd15"
    ticket_office = TicketOffice(
        train_service_adapter=mock_train_data_adapter.return_value,
        booking_reference_adapter=mock_booking_ref_adapter.return_value,
    )

    result = ticket_office.make_reservation(train_id="express_2000", seat_count=1)

    assert isinstance(result, Reservation)
    assert result.train_id == "express_2000"
    (seat1,) = result.seats
    assert seat1 == "1A"
    assert result.booking_reference == "75bcd15"
    mock_booking_ref_adapter.return_value.get_booking_reference.assert_called_once()
    mock_train_data_adapter.return_value.reserve.assert_called_once_with(
        train_id="express_2000", seats=["1A"], booking_reference="75bcd15"
    )


@patch("ticket_office.BookingReferenceClient")
@patch("ticket_office.TrainDataAdapter")
def test_should_reserve_two_seats_when_empty_train(
    mock_train_data_adapter, mock_booking_ref_adapter
):
    empty_train_data = [
        Seat(seat_name="1A", seat_number="1", coach="A", booking_reference=""),
        Seat(seat_name="2A", seat_number="2", coach="A", booking_reference=""),
        Seat(seat_name="3A", seat_number="3", coach="A", booking_reference=""),
    ]
    mock_train_data_adapter.return_value.get_train_data.return_value = empty_train_data
    mock_booking_ref_adapter.return_value.get_booking_reference.return_value = "75bcd15"
    ticket_office = TicketOffice(
        train_service_adapter=mock_train_data_adapter.return_value,
        booking_reference_adapter=mock_booking_ref_adapter.return_value,
    )

    result = ticket_office.make_reservation(train_id="express_2000", seat_count=2)

    assert isinstance(result, Reservation)
    assert result.train_id == "express_2000"
    (seat1, seat2) = result.seats
    assert seat1 == "1A"
    assert seat2 == "2A"
    assert result.booking_reference == "75bcd15"
    mock_booking_ref_adapter.return_value.get_booking_reference.assert_called_once()
    mock_train_data_adapter.return_value.reserve.assert_called_once_with(
        train_id="express_2000", seats=["1A", "2A"], booking_reference="75bcd15"
    )


@patch("ticket_office.BookingReferenceClient")
@patch("ticket_office.TrainDataAdapter")
def test_should_reserve_two_seats_in_second_coach_when_first_coach_full(
    mock_train_data_adapter, mock_booking_ref_adapter
):
    empty_train_data = [
        Seat(seat_name="1A", seat_number="1", coach="A", booking_reference="ref1"),
        Seat(seat_name="2A", seat_number="2", coach="A", booking_reference="ref2"),
        Seat(seat_name="3A", seat_number="3", coach="A", booking_reference=""),
        Seat(seat_name="1B", seat_number="1", coach="B", booking_reference=""),
        Seat(seat_name="2B", seat_number="2", coach="B", booking_reference=""),
        Seat(seat_name="3B", seat_number="3", coach="B", booking_reference=""),
    ]
    mock_train_data_adapter.return_value.get_train_data.return_value = empty_train_data
    mock_booking_ref_adapter.return_value.get_booking_reference.return_value = "75bcd15"
    ticket_office = TicketOffice(
        train_service_adapter=mock_train_data_adapter.return_value,
        booking_reference_adapter=mock_booking_ref_adapter.return_value,
    )

    result = ticket_office.make_reservation(train_id="express_2000", seat_count=2)

    assert isinstance(result, Reservation)
    assert result.train_id == "express_2000"
    (seat1, seat2) = result.seats
    assert seat1 == "1B"
    assert seat2 == "2B"
    assert result.booking_reference == "75bcd15"
    mock_booking_ref_adapter.return_value.get_booking_reference.assert_called_once()
    mock_train_data_adapter.return_value.reserve.assert_called_once_with(
        train_id="express_2000", seats=["1B", "2B"], booking_reference="75bcd15"
    )


@patch("ticket_office.BookingReferenceClient")
@patch("ticket_office.TrainDataAdapter")
def test_should_reserve_two_seats_in_second_coach_when_first_coach_go_over_70(
    mock_train_data_adapter, mock_booking_ref_adapter
):
    empty_train_data = [
        Seat(seat_name="1A", seat_number="1", coach="A", booking_reference="ref1"),
        Seat(seat_name="2A", seat_number="2", coach="A", booking_reference=""),
        Seat(seat_name="1B", seat_number="1", coach="B", booking_reference="ref2"),
        Seat(seat_name="2B", seat_number="2", coach="B", booking_reference=""),
        Seat(seat_name="3B", seat_number="3", coach="B", booking_reference=""),
        Seat(seat_name="4B", seat_number="4", coach="B", booking_reference=""),
    ]
    mock_train_data_adapter.return_value.get_train_data.return_value = empty_train_data
    mock_booking_ref_adapter.return_value.get_booking_reference.return_value = "75bcd15"
    ticket_office = TicketOffice(
        train_service_adapter=mock_train_data_adapter.return_value,
        booking_reference_adapter=mock_booking_ref_adapter.return_value,
    )

    result = ticket_office.make_reservation(train_id="express_2000", seat_count=2)

    assert isinstance(result, Reservation)
    assert result.train_id == "express_2000"
    (seat1, seat2) = result.seats
    assert seat1 == "2B"
    assert seat2 == "3B"
    assert result.booking_reference == "75bcd15"
    mock_booking_ref_adapter.return_value.get_booking_reference.assert_called_once()
    mock_train_data_adapter.return_value.reserve.assert_called_once_with(
        train_id="express_2000", seats=["2B", "3B"], booking_reference="75bcd15"
    )


@patch("ticket_office.BookingReferenceClient")
@patch("ticket_office.TrainDataAdapter")
def test_should_prefer_coach_C_when_coach_C_is_empty(
    mock_train_data_adapter, mock_booking_ref_adapter
):
    empty_train_data = [
        Seat(seat_name="1A", seat_number="1", coach="A", booking_reference="ref1"),
        Seat(seat_name="2A", seat_number="2", coach="A", booking_reference=""),
        Seat(seat_name="1B", seat_number="1", coach="B", booking_reference="ref2"),
        Seat(seat_name="2B", seat_number="2", coach="B", booking_reference=""),
        Seat(seat_name="3B", seat_number="3", coach="B", booking_reference=""),
        Seat(seat_name="4B", seat_number="4", coach="B", booking_reference=""),
        Seat(seat_name="1C", seat_number="1", coach="C", booking_reference=""),
        Seat(seat_name="2C", seat_number="2", coach="C", booking_reference=""),
        Seat(seat_name="3C", seat_number="3", coach="C", booking_reference=""),
        Seat(seat_name="4C", seat_number="4", coach="C", booking_reference=""),
    ]
    mock_train_data_adapter.return_value.get_train_data.return_value = empty_train_data
    mock_booking_ref_adapter.return_value.get_booking_reference.return_value = "75bcd15"
    ticket_office = TicketOffice(
        train_service_adapter=mock_train_data_adapter.return_value,
        booking_reference_adapter=mock_booking_ref_adapter.return_value,
    )

    result = ticket_office.make_reservation(train_id="express_2000", seat_count=2)

    assert isinstance(result, Reservation)
    assert result.train_id == "express_2000"
    (seat1, seat2) = result.seats
    assert seat1 == "1C"
    assert seat2 == "2C"
    assert result.booking_reference == "75bcd15"
    mock_booking_ref_adapter.return_value.get_booking_reference.assert_called_once()
    mock_train_data_adapter.return_value.reserve.assert_called_once_with(
        train_id="express_2000", seats=["1C", "2C"], booking_reference="75bcd15"
    )
