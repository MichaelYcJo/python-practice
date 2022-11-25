from rest_framework.serializers import ModelSerializer
from rooms.models import Amenity, Room


class AmenitySerializer(ModelSerializer):
    class Meta:
        model = Amenity
        fields = "__all__"

class RoomSerializer(ModelSerializer):
    class Meta:
        model = Room
        fields = "__all__"
        depth = 1 # ID값을 기반으로 해당하는 Object 데이터를 가져온다