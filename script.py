import requests
from bs4 import BeautifulSoup
import re
from colorama import init
from colored import fore, back, style

init()  # calls colorama's init so that colored works on windows


class color:
    PURPLE = '\033[95m'
    CYAN = '\033[96m'
    DARKCYAN = '\033[36m'
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    END = '\033[0m'


class Cinema(object):
    def __init__(self, location, hours):
        self.location = location
        self.hours = hours

    def __str__(self):
        format_location = fore.INDIAN_RED_1A+'\t\t'+self.location+":"+style.RESET
        cinema_string = format_location
        for hour in self.hours:
            cinema_string += '\n\t\t\t' + str(hour)
        return cinema_string


class Hour(object):
    def __init__(self, hour, _3D=False, dubbed=False):
        self.hour = hour
        self._3D = _3D
        self.dubbed = dubbed

    def __str__(self):
        format_hour = str(self.hour)
        hour_string = format_hour
        if self._3D:
            hour_string += " 3D"
        if self.dubbed:
            hour_string += ' dubbed'
        return hour_string


class Movie(object):

    def __init__(self, id, title, rating, genres, schedules):
        self.id = id
        self.title = title
        self.rating = rating
        self.genres = genres
        self.schedules = schedules

    def __str__(self):
        format_title = '\t'+fore.TURQUOISE_2 + style.BOLD + self.title+style.RESET
        format_rating = '\n\t\tIMDB:'
        if float(self.rating) > 7.9:
            format_rating += fore.LIGHT_GREEN
        elif float(self.rating) > 4.9:
            format_rating += fore.GOLD_1
        else:
            format_rating += fore.RED_3B
        format_rating += self.rating+style.RESET
        format_genres = '\n\t\tGenres: '+','.join(self.genres)
        movie_string = format_title + format_rating + format_genres
        for schedule in self.schedules:
            movie_string += '\n'+str(schedule)
        return movie_string+'\n'


def get_location():
    url = 'http://ipinfo.io/json'
    try:
        response = requests.get(url)
        data = response.json()
        city = data['city']
        if not city:
            return 'Sibiu'
        return city
    except KeyError:
        print("There is no city in the json ")
    return ""


def generate_url():
    url = "https://www.cinemagia.ro/program-cinema/"
    return url+get_location()+'/duminica'


def get_cinemagia_page():
    page = requests.get(generate_url())
    if page.status_code == 200:
        return page.text


def get_movies():
    document = get_cinemagia_page()
    soup = BeautifulSoup(document, 'html.parser')
    movies = soup.find_all('div', id=re.compile('^movieShows\d+'))
    movies_list = []
    for movie in movies:
        id = movie.get('id').replace('movieShows', '')
        title = movie.find_all('a')[1].get('title')
        rating = movie.find('div', class_='info').find(
            'div').text.split(' ')[-1]  # get IMDB rating
        genres = movie.find('div', class_='info').find_all('div')[
            1].find_all('a')
        genres_copy = genres
        genres = []
        for genre in genres_copy:
            genres.append(genre.text)
        schedules = movie.find('div', class_='program').findChildren(
            'div', recursive=False)
        schedule = []
        for _schedule in schedules:
            location = _schedule.find('a').text
            hours = []
            hours_list = _schedule.find_all('span')
            for hour in hours_list:
                text = hour.text
                _3D = dubbed = False
                if '3D' in text:
                    _3D = True
                if 'ro' in text:
                    dubbed = True
                hours.append(Hour(text[:5], _3D, dubbed))
            schedule.append(Cinema(location, hours))
        movie_obj = Movie(id, title, rating, genres, schedule)
        movies_list.append(movie_obj)

        # manipulate movies to show the movie
    return movies_list


def print_start_message():
    print(fore.ORANGE_3+style.UNDERLINED+style.BOLD +
          'Showing all movies that run on Sunday:\n'+style.RESET)


def display_movies():
    movies = get_movies()
    print_start_message()
    for movie in movies:
        print(movie)


display_movies()
# print('\tAN')
# print(color.BOLD +color.GREEN+ 'Hello World !' + color.END)
