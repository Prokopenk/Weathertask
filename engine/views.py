from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.views import generic
from .models import City
from weather import Weather, Unit  # библиотека для определения погоды
import geocoder  # библиотека от google для определения города по координатам


weather = Weather(unit=Unit.CELSIUS)  # устанавливаем измерение погоду в цельсиях в библиотеке weather


# функция получения текущей погоды
def get_current_weather(city):
    try:
        # возвращаем текущую погоду для города city из библиотеки weather. Если город не существует, возвращаем None
        return weather.lookup_by_location(city).condition  # condition in some cases is callable (.condition())
    except Exception as e:
        print(e)
        return None


# функция получения прогноза погоды
def get_future_weather(city):
    try:
        # возвращаем прогноз на 5 дней для города city из библиотеки weather. Если город не существует, возвращаем None
        return weather.lookup_by_location(city).forecast[0:5]  # forecast in some cases is callable (.forecast())
    except Exception as e:
        print(e)
        return None


# listview городов из базы и view главной страницы
class CityListView(generic.ListView):
    model = City  # модель города
    context_object_name = 'cities'  # название массива с городами в шаблоне
    template_name = "engine/base.html"

    def get_queryset(self):
        return City.objects.order_by('-pk')  # выводим города по убыванию ключа


# view погоды по локации пользователя
class LocationWeatherView(generic.View):
    template_name = "engine/location_weather.html"

    def get(self, request):
        latitude = request.GET.get('latitude', '')    # получаем широту
        longitude = request.GET.get('longitude', '')    # получаем долготу
        city = None  # название города из котого наш пользователь
        while city is None:
            g = geocoder.google([latitude, longitude], method='reverse')  # по координатам вычесляем город
            city = g.city  # город пользователя. Иногда может быть None, поэтому делаем в цикле, пока не определим норм
        current = get_current_weather(city)  # текущая погода в городе пользователя
        future = get_future_weather(city)  # прогноз погоды для города пользователя
        return render(request, self.template_name, {"city": city, 'current': current, 'forecasts': future})


# view добавления города в базу
class AddCityView(generic.View):
    def get(self, request):
        city = request.GET.get('city', '').lower()  # получаем из url название города и делаем текст в нижнем регистре
        if get_current_weather(city):  # проверка или существует прогноз для города city, если нет - return "None"
            if not City.objects.filter(name=city):  # проверяем или нет города city в нашей базе
                new_city = City.objects.create(name=city)  # если нет, то добавляем в базу
                return HttpResponse(new_city.pk)  # возвращаем pk только что созданного в базе города
        return HttpResponse("None")


# view погоды для города с базы
class GetCityView(generic.View):
    template_name = "engine/city_weather.html"

    def get(self, request):
        city = request.GET.get('city', '')  # достаем из url название города
        current = get_current_weather(city)  # получаем текущую погоду для города
        future = get_future_weather(city)  # получаем ближайшую погоду для города
        return render(request, self.template_name, {'city': city, 'current': current, 'forecasts': future})


# view удаления города из базы
class CityDeleteView(generic.DeleteView):
    model = City
    success_url = '/'

    def get_object(self, queryset=None):
        return get_object_or_404(City, pk=self.request.POST.get("pk"))

