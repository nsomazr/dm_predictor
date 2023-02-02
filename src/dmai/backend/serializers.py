from rest_framework import serializers
from .models import Inference
from .models import DataAPI

class InferenceModelSerializer(serializers.ModelSerializer):

    class Meta:

        model = Inference

        fields = ('__all__')


class DataAPTModelSerializer(serializers.ModelSerializer):
    processed_at = serializers.DateTimeField(format=None, input_formats=None)
    class Meta:

        model = DataAPI

        fields = ('__all__')