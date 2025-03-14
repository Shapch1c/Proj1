from .views import AppointmentView
from django.urls import path, include
app_name = 'appointments'
urlpatterns = [
   path('', AppointmentView.as_view(), name='make_appointment'),
]