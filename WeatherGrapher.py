import requests
from matplotlib import pyplot as plt

import tkinter as tk
from PIL import ImageTk, Image

import pycountry
from datetime import datetime
import difflib

# Create a root window for the GUI
root = tk.Tk()
root.resizable(width=False, height=False)
root.title('CityTemp')

# Set screen dimensions
SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 900

# Create a canvas to put in the root window
canvas = tk.Canvas(root, width=SCREEN_WIDTH, height=SCREEN_HEIGHT)
canvas.pack()
canvas.create_line(0, 220, SCREEN_WIDTH, 220, fill='black')

# Create the frame which includes the entry box and the button to search for a city
search_frame = tk.Frame(canvas, bg='#e3b6b3', bd=5)
search_frame.place(relx=0.5, rely=0.02, relwidth=0.75, relheight=0.1, anchor='n')

# Create the entry box which the user types in the city that they want to search for
entry = tk.Entry(search_frame, font=('Calibri', 15))
entry.place(relwidth=0.75, relheight=1)

# Create the button which the user will press to search for the city that they inputted
button = tk.Button(search_frame, text='Search City', bg='#d7dbd7', font=('Calibri', 15),
                   command=lambda: check_input())
button.place(relx=0.75, relwidth=0.25, relheight=1)

# Lower frame for graph and error messages
lower_frame = tk.Frame(canvas, bd=3)
lower_frame.place(relx=0, rely=0.25, relwidth=1, relheight=0.75)

# Frame containing the start date label and entry.
start_date_frame = tk.Frame(canvas)
start_date_frame.place(relx=0.125, rely=0.13, relwidth=0.25, relheight=0.05)

# Entry for the user to type in the starting date of the time range
start_date_entry = tk.Entry(start_date_frame, font=('Calibri', 15))
start_date_entry.place(relx=0.5, rely=0, relwidth=0.5, relheight=1)

# Label to have the text to display 'Start Date:'
start_date_label = tk.Label(start_date_frame, text='Start Date:', font=('Calibri', 15))
start_date_label.place(relx=0, rely=0, relwidth=0.5, relheight=0.5)

# Label for an example of a start date
start_example_label = tk.Label(start_date_frame, text='Ex): 2010-01', font=('Calibri', 10))
start_example_label.place(relx=0, rely=0.5, relwidth=0.5, relheight=0.5)

# Frame containing the end date label and entry.
end_date_frame = tk.Frame(canvas)
end_date_frame.place(relx=0.125, rely=0.19, relwidth=0.25, relheight=0.05)

# Entry for the user to type in the ending date of the time range
end_date_entry = tk.Entry(end_date_frame, font=('Calibri', 15))
end_date_entry.place(relx=0.5, rely=0, relwidth=0.5, relheight=1)

# Label to have the text to display 'End Date:'
end_date_label = tk.Label(end_date_frame, text='End Date:', font=('Calibri', 15))
end_date_label.place(relx=0, rely=0, relwidth=0.5, relheight=0.5)

# Label for an example of an end date
end_example_label = tk.Label(end_date_frame, text='Ex): 2012-12', font=('Calibri', 10))
end_example_label.place(relx=0, rely=0.5, relwidth=0.5, relheight=0.5)

# Frame containing the country label and entry.
country_frame = tk.Frame(canvas)
country_frame.place(relx=0.4, rely=0.13, relwidth=0.32, relheight=0.05)

# Entry to input the country of the city
country_entry = tk.Entry(country_frame, font=('Calibri', 15))
country_entry.place(relx=0.5, rely=0, relwidth=0.5, relheight=1)

# Label to have the text to display 'Country:'
country_label = tk.Label(country_frame, text='Country:', font=('Calibri', 15))
country_label.place(relx=0, rely=0, relwidth=0.5, relheight=1)

# Key = Weather options the user sees, Value = # keyword that API uses to retrieve data
weather_options = {
    'Average Temperature (C)': 'temperature_mean',
    'Average Minimum Temperature (C)': 'temperature_mean_min',
    'Average Maximum Temperature (C)': 'temperature_mean_max',
    'Lowest Temperature (C)': 'temperature_min',
    'Highest Temperature (C)': 'temperature_max',
    'Precipitation (mm)': 'precipitation',
    'Pressure (hPa)': 'pressure'
}

# Need to pass this list in the menu object below. 
weather_choices = list(weather_options.keys())
current_item = tk.StringVar()
current_item.set('Select Measurement')

# Drop down menu for the measurement that you want to get a graph on and various weather options to choose from.
measurement_menu = tk.OptionMenu(canvas, current_item, *weather_choices)
measurement_menu.place(relx=0.44, rely=0.19, relwidth=0.285, relheight=0.05)


def check_input():
    """Make sure user filled out all entries and the provided starting dates are formatted correctly."""
    if entry.get() and start_date_entry.get() and end_date_entry.get() and country_entry.get() and \
            current_item.get() != 'Select Measurement':
        try:
            start_date_test = datetime.strptime(start_date_entry.get(), "%Y-%m")
            end_date_test = datetime.strptime(end_date_entry.get(), "%Y-%m")
        except ValueError:
            error_message(4)
        else:
            search_city()
    else:
        error_message(1)


# API Code:

api_key = 'IOBnNwPG'
station_url = 'https://api.meteostat.net/v1/history/monthly'
city_url = 'https://api.meteostat.net/v1/stations/search'


def search_city():
    """Search for weather stations associated with inputted city. If weather stations are available, use a station
    to retrieve weather data and make sure that that data is actually available. If no data available in any of the
    weather stations, print error messages. If data available, plot it."""

    country_input = correct_country()

    if not country_input:
        error_message(3)
        return None

    city_response = city_request(country_input)

    if city_response['data']:
        station_number = city_response['data'][0]['id']
        get_station_data(station_number)
        search_for_data(city_response)
        if station_data_output['data']:
            plot_data()
    else:
        error_message(2)


def correct_country():
    """Account for naming synonyms of England. Implement a spell-check feature which returns the correct county even
     if you misspelled it slightly."""

    if country_entry.get() == "England" or country_entry.get() == "Britain" or country_entry.get() == "Great Britain":
        country_input = "United Kingdom"
        return country_input
    else:
        countries = [c.name for c in pycountry.countries]
        try:
            country_input = difflib.get_close_matches(country_entry.get(), countries)[0]
            return country_input
        except IndexError:
            return None


def city_request(country_input):
    """Search for weather stations associated with the city the user inputted, using the country parameter to make
     sure that duplicate city names between countries do not occur. Return list of available weather stations."""

    country_obj = pycountry.countries.get(name=country_input)
    country_code = country_obj.alpha_2
    city_request_params = {'q': entry.get().strip(), 'key': api_key, 'country': country_code}
    city_data_response = requests.get(city_url, params=city_request_params)
    city_response = city_data_response.json()
    return city_response


def get_station_data(station_number):
    """Using the determined station number, request weather data for this specific station number."""

    station_request_params = {'station': station_number, 'start': start_date_entry.get(), 'end': end_date_entry.get(),
                              'key': api_key}
    station_data_response = requests.get(station_url, params=station_request_params)
    global station_data_output
    station_data_output = station_data_response.json()


def search_for_data(city_response):
    """If no data available for a certain weather station, loop through other weather stations until a station with
    weather data is found."""

    if not station_data_output['data']:
        for x in range(len(city_response['data'])):
            station_number = city_response['data'][x]['id']
            get_station_data(station_number)
            if station_data_output['data']:
                break
            elif not station_data_output['data'] and x == len(city_response['data']) - 1:
                error_message(2)
                break


def plot_data():
    """Plot data. Not much to explain."""

    months = [datetime.strptime(month['month'], "%Y-%m") for month in station_data_output['data']]
    temps = [month[weather_options[current_item.get()]] for month in station_data_output['data']]
    fig = plt.figure(figsize=(10, 6))
    plt.plot(months, temps, c='red')
    plt.title(
        f'{start_date_entry.get()} to {end_date_entry.get()} Monthly {current_item.get()} in {entry.get().title().strip()}',
        fontsize=15)
    plt.xlabel('', fontsize=5)
    plt.ylabel(current_item.get(), fontsize=16)
    plt.tick_params(axis='both', which='major', labelsize=12)
    plt.savefig('temp_graph.png')
    show_graph()


def show_graph():
    """Use PIL to display the image of the graph that was saved on the local directory."""
    img = ImageTk.PhotoImage(Image.open("temp_graph.png"), master=root)
    label = tk.Label(lower_frame, image=img)
    label.image = img
    label.place(relx=0, rely=0, relwidth=1, relheight=1)


def error_message(errortype):
    """Account for errors such as not filling out the entries, no data available, spelling, formatting, etc..."""

    if errortype == 1:
        error_label = tk.Label(lower_frame, text='Please fill out all the information for your search!',
                               font=('Calibri', 25))
        error_label.place(relx=0, rely=0, relwidth=1, relheight=1)
    elif errortype == 2:
        error_label = tk.Label(lower_frame,
                               text=f'Unfortunately there is no data for this city. \n Make sure you spell your city '
                                    f'correctly!', font=('Calibri', 30))
        error_label.place(relx=0, rely=0, relwidth=1, relheight=1)
    elif errortype == 3:
        error_label = tk.Label(lower_frame, text='Please make sure you spelled your country correctly!',
                               font=('Calibri', 25))
        error_label.place(relx=0, rely=0, relwidth=1, relheight=1)

    elif errortype == 4:
        error_label = tk.Label(lower_frame, text='Please make sure you formatted your start and end dates correctly! '
                                                 '\n Example: 2010-01, 2010-12, etc...', font=('Calibri', 25))
        error_label.place(relx=0, rely=0, relwidth=1, relheight=1)


def kill():
    root.quit()


root.protocol("WM_DELETE_WINDOW", kill)
root.mainloop()
