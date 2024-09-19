import dataclasses


@dataclasses.dataclass
class CoordinatesRequest:
    longitude: float
    latitude: float

    def __post_init__(self) -> None:
        print("post init 호출!")
        self.longitude = round(self.longitude, 5)
        self.latitude = round(self.latitude, 5)


coordinates_request = CoordinatesRequest(longitude=127.005926, latitude=37.490061)
print(coordinates_request.longitude, coordinates_request.latitude)
