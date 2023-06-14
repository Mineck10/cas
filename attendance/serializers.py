from rest_framework import serializers
from .models import PI_Data

class RaspberryPiDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = PI_Data
        fields = '__all__'
        #Alternative can be defined as:
        #fields = ['id', 'fingerprint', 'registration_number', 'date_added']

        