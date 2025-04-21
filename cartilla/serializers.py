from rest_framework import serializers
from .models import Cartilla

class CartillaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cartilla
        fields = '__all__'