from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import Frontend
from .serializers import FrontendModelSerializer
from backend.forms import DataForm
# Create your views here.

class FrontendAPIView(APIView):

    def get(self, request):
        frontend = Frontend.objects.all()
        serializer = FrontendModelSerializer(frontend, many = True)
        return Response(serializer.data)
    
    def post(self, request):
        serializer = FrontendModelSerializer(data = request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status = 201)
        return Response(serializer.errors, status = 400)

    def index(request):
        data_form = DataForm()
        return render(request, template_name='pages/index.html', context={'data_form':data_form})
