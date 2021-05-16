from django.urls import path, include
# from django.conf.urls import url
from . import views

urlpatterns = [
    path("", views.index, name="Main page"),
    path("tracker/", views.tracker, name="Tracker"),

    path("tracker/api/<mode>/<view>/<many>/<user>/<order>/", views.api.as_view()),
    path("tracker/api/chart/<duration>/", views.chart),
]