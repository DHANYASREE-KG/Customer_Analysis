from django.urls import path
from . import views

urlpatterns = [
    path("", views.dashboard, name="dashboard"),
    path("state/<str:state_name>/", views.state_dashboard, name="state_dashboard"),
]
