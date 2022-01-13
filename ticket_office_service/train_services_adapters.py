import urllib.request
import json


class TrainDataAdapter:
    URL = "http://127.0.0.1:8081"
    
    def get_train_data(self, train_id):
        train_data = urllib.request.urlopen(self.URL + f"/data_for_train/{train_id}")
        return json.loads(train_data.read().decode("utf-8"))

    def reserve(self, train_id, seats, booking_reference):
        form_data = {"train_id": train_id, "seats": json.dumps(seats), "booking_reference": booking_reference}
        data = urllib.parse.urlencode(form_data)
        req = urllib.request.Request(self.URL + "/reserve", bytes(data, encoding="ISO-8859-1"))
        return f"situation after reservation: {urllib.request.urlopen(req).read().decode('utf-8')}"


class BookingReferenceAdapter:
    URL = "http://127.0.0.1:8082"

    def get_booking_reference(self):
        data = urllib.request.urlopen(self.URL + "/booking_reference")
        return data.read().decode("utf-8")