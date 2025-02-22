from django.urls import path
from genai.views import Home
urlpatterns = [
    path('', Home, ),
]