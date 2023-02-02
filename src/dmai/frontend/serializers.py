from rest_framework import serializers
from .models import Frontend

class FrontendModelSerializer(serializers.ModelSerializer):

    class Meta:

        model = Frontend

        # fields = ('__all__')