from django.urls import path
from .views import FrontendAPIView

app_name = "frontend"  

urlpatterns = [
                path('', FrontendAPIView.index, name = 'index'),
                # path('home/api/', FrontendAPIView.as_view(), name="home-api")
                ]