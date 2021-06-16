import pyowm

owm = pyowm.OWM("e1fe0e1659254d673cb82b6f2986ad71")

location = owm.weather_at_place('Toronto')

weather = location.get_weather()

print(weather)

temp = weather.get_temperature('celsius')

print(temp)

for key, value in temp.items():
    print(key, value)