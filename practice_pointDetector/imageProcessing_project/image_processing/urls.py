from django.urls import path
from .views import ImageViewSet

urlpatterns = [
    path('images/', ImageViewSet.as_view()),
]
