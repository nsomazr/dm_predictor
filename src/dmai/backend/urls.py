from django.urls import path
from .views import InferenceAPIView, DataInferenceAPIView
from . import views

app_name = "backend"  

urlpatterns = [
                path('inference/api/', DataInferenceAPIView.as_view(), name="inference-api"),
                path('results/api', InferenceAPIView.as_view(), name="results-api"),
                path('predict/', views.prediction, name="predict")
                 ]