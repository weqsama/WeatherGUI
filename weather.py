import requests as r
import PyQt6
import sys
from PyQt6.QtWidgets import QApplication, QStackedWidget, QTableWidgetItem
from PyQt6.QtGui import QColor
from weather_ui import Ui_top

api_key = "aeb03ea5c2b5b52c4ad266008823acae" # I've included my API key for convenience, under normal circumstances I would not expose the key but in this case it is acceptable.
weather_url = "https://api.openweathermap.org/data/2.5/weather"
geo_url = "http://api.openweathermap.org/geo/1.0/direct"

class WeatherApp(QStackedWidget): # App class, do not touch
    def __init__(self):
        super().__init__()
        self.ui = Ui_top()
        self.ui.setupUi(self)
        self.units = "imperial" # Units set to imperial by default

        # Button mapping
        self.ui.imp_button.clicked.connect(self.click_imp_button)
        self.ui.met_button.clicked.connect(self.click_met_button)
        self.ui.int_button.clicked.connect(self.click_int_button)
        self.ui.check_button.clicked.connect(self.click_check_button)
        self.ui.pushButton.clicked.connect(self.click_compare_button)
        self.ui.pushButton_2.clicked.connect(self.click_back_to_home)
        self.ui.compare_button.clicked.connect(self.click_check_compare)
        self.ui.pushButton_3.clicked.connect(self.click_back_to_home)

    # Radio button definitions
    def click_imp_button(self, units): # Imperial system button
        self.units = "imperial"

    def click_met_button(self, units): # Metric system button
        self.units = "metric"
    
    def click_int_button(self, units): # International system button
        self.units = "default"

    def click_compare_button(self): # Sends the user to the grab_compare screen to enter a second city to compare to the first
        self.setCurrentWidget(self.ui.grab_compare)

    def click_back_to_home(self): # Returns the user to the home page, allowing for another city to be observed
        self.setCurrentWidget(self.ui.home)

    # Helper functions
    def get_city(self): # Returns whatever is in the city_field text box as a string
        return self.ui.city_field.toPlainText()
    
    def cityIsValid(self): # Checks if the city is valid. If not it sets the coordinates to the South Pole and returns False
        coords = get_coords(self.get_city())
        if coords == (90, 45):
            return False
        return True
    
    def get_comparison(self): # Returns whatever is in the city_field_2 text box as a string
        return self.ui.city_field_2.toPlainText()
    
    def comparisonIsValid(self): # Checks if the second city is valid. If not it sets the coordinates to the South Pole and returns False
        coords = get_coords(self.get_comparison())
        if coords == (90, 45):
            return False
        return True
    
    def get_units(self): # Returns the units used based on the selected system
        if self.units == "imperial":
            return ("°F", "MPH")
        elif self.units == "metric":
            return ("°C", "m/s")
        else:
            return ("°K", "m/s")
        
    def check_coverage(self, coverage): # Returns the cloud coverage as a string
        if coverage == 0:
            return "Clear"
        elif 1 <= coverage <= 10:
            return "Mostly clear"
        elif 11 <= coverage <= 30:
            return "Partly cloudly"
        elif 51 <= coverage <= 80:
            return "Cloudy"
        else:
            return "Overcast"
        
    def dupe_table(self, old_table, new_table): # Function that allows table elements to be copied
        for i in range(5):
            temp_item = old_table.item(i, 0).text()
            new_table.setItem(i, 0, QTableWidgetItem(temp_item))

    # More button definitions (Defined later to use helper functions)
    
    def click_check_button(self): # Check weather button logic
        if self.cityIsValid():
            coords = get_coords(self.get_city())
            weather = get_weather(self, coords[0], coords[1])
            self.setCurrentWidget(self.ui.display)
            self.ui.city_label.setText(self.get_city().title().strip())

            # Table population (Would turn into a function if given more time, hard code was easier to think about)
            temp = f"{int(weather['main']['temp'])}{self.get_units()[0]}"
            humidity = f"{weather['main']['humidity']}%"
            wind_speed = f"{weather['wind']['speed']} {self.get_units()[1]}"
            hi = f"{int(weather['main']['temp_max'])}{self.get_units()[0]}"
            lo = f"{int(weather['main']['temp_min'])}{self.get_units()[0]}"
            clouds = f"{self.check_coverage(weather['clouds']['all'])}"
            self.ui.tableWidget.setHorizontalHeaderLabels(["Weather Data"])
            self.ui.tableWidget.setItem(0, 0, QTableWidgetItem(temp))
            self.ui.tableWidget.setItem(1, 0, QTableWidgetItem(humidity))
            self.ui.tableWidget.setItem(2, 0, QTableWidgetItem(hi + " / " + lo))
            self.ui.tableWidget.setItem(3, 0, QTableWidgetItem(wind_speed))
            self.ui.tableWidget.setItem(4, 0, QTableWidgetItem(clouds))
            
            self.dupe_table(self.ui.tableWidget, self.ui.tableWidget_2)
            self.ui.city_label_2.setText(self.ui.city_field.toPlainText().title().strip())
        else:
            self.ui.city_field.setText("Invalid city. Please check spelling.")

    def click_check_compare(self): # Comparison button logic
        if self.comparisonIsValid():
            coords = get_coords(self.get_comparison())
            weather = get_weather(self, coords[0], coords[1])
            self.setCurrentWidget(self.ui.compare)
            self.ui.city_label_3.setText(self.get_comparison().title().strip())

            # Table population (Same deal)
            temp = f"{int(weather['main']['temp'])}{self.get_units()[0]}"
            humidity = f"{weather['main']['humidity']}%"
            wind_speed = f"{weather['wind']['speed']} {self.get_units()[1]}"
            hi = f"{int(weather['main']['temp_max'])}{self.get_units()[0]}"
            lo = f"{int(weather['main']['temp_min'])}{self.get_units()[0]}"
            clouds = f"{self.check_coverage(weather['clouds']['all'])}"
            self.ui.tableWidget_3.setHorizontalHeaderLabels(["Weather Data"])
            self.ui.tableWidget_3.setItem(0, 0, QTableWidgetItem(temp))
            self.ui.tableWidget_3.setItem(1, 0, QTableWidgetItem(humidity))
            self.ui.tableWidget_3.setItem(2, 0, QTableWidgetItem(hi + " / " + lo))
            self.ui.tableWidget_3.setItem(3, 0, QTableWidgetItem(wind_speed))
            self.ui.tableWidget_3.setItem(4, 0, QTableWidgetItem(clouds))
        else:
            self.ui.city_field_2.setText("Invalid city. Please check spelling.")
           
def get_coords(city): # Function uses the geocoding API to return the latitude and longitude of the desired city. If the city is not found, an error message is printed 
    req_params = {
        "q" : city,
        "limit" : 1,
        "appid" : api_key
    }
    try:
        response = r.get(geo_url, params=req_params) # Requesting geocoding info from openweathermap 
        location_data = response.json() # Allows for the data to be indexed (BIG)

        if response.ok: # Status code is 200
            return (location_data[0]["lat"], location_data[0]["lon"]) # Returns a tuple of the coordinates searched (lat, long)
        else:
            print(response)
            print(response.reason) # Prints the error message for a status code that isn't 200
            return (90, 45)
    except IndexError: # An IndexError indicates that the latitude and longitude values for the input city don't exist. Meaning that the input was incorrect
        print("City not found.")
        return (90, 45)

def get_weather(self, lat, long): # Returns the JSON format of the weather data from the openweathermap API
    req_params = {
        "lat" : lat,
        "lon" : long,
        "units" : self.units,
        "appid" : api_key
    }
    try:
        response = r.get(weather_url, params=req_params)
        location_data = response.json() 

        if response.ok: # Checks if the API is working properly, if not prints an error message to the console.
            return location_data
        else:
            print(response.reason)
            return response
    except:
        print("error")
        return 0

def main(): # Main function
    weather = QApplication(sys.argv)
    window = WeatherApp()
    window.show()
    sys.exit(weather.exec())
    coords = get_coords("London")
    weather = get_weather(window, coords[0], coords[1])
    print(weather)
    
main()
