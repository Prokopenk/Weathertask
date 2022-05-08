from django.conf.urls import url

from engine import views

urlpatterns = [
    url(r'^$', views.CityListView.as_view(), name='main'),
    url(r'^remove_city/$', views.CityDeleteView.as_view(), name='remove_city'),
    url(r'^add_city/$', views.AddCityView.as_view(), name='add_city'),
    url(r'^get_city/$', views.GetCityView.as_view(), name='get_city'),
    url(r'^location_weather/$', views.LocationWeatherView.as_view(), name='location_weather')
]
