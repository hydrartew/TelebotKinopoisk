import requests, json

class FILM:
    def __init__(self, data: dict):
        self.filmId = data['kinopoiskId']
        self.name = data['nameOriginal'] if data['nameRu'] == None else data['nameRu']
        self.year = data['year']
        self.type = 'Сериал' if data['type'] == 'TV_SERIES' else 'Фильм'
        self.countries = ' '.join([data['countries'][i]['country'] for i in range(len(data['countries']))])  # str of countries
        self.rating = data['ratingKinopoisk']
        self.ratingVoteCount = str(("{:_d}".format(int(data['ratingKinopoiskVoteCount'])))).replace('_', ' ')
        self.posterUrl = data['posterUrlPreview']
        self.description = 'Описание отсутствует' if data['description'] == None else data['description']
        self.webUrl = data['webUrl']

class SEARCH:
    def __init__(self, data: dict):
        self.filmId = data['filmId']
        self.name = data['nameEn'] if 'nameRu' not in data else data['nameRu']
        self.year = data['year']

class MONEY:
    def __init__(self, data: dict):
        self.budget = str(("{:_d}".format(data["amount"]))).replace('_', ' ') + ' ' + data['symbol'] 
        self.amount = str(("{:_d}".format(data["amount"]))).replace('_', ' ') + ' ' + data['symbol']

class STAFF:
    def __init__(self, data: dict):
        self.professionKey = True if data['professionKey'] == 'ACTOR' else False
        self.actor_name = data['nameRu']

class KP:
    def __init__(self, token):
        self.token = token
        self.headers = {"X-API-KEY": self.token}
        self.api_version = 'v2.1'
        self.API = 'https://kinopoiskapiunofficial.tech/api/' + self.api_version + '/'
        self.secret_API = 'https://videocdn.tv/api/short'
        self.version = self.api_version + '.2-release'
        self.about = 'KinoPoiskAPI'

    def search(self, query):
        request = requests.get(self.API + 'films/search-by-keyword', headers=self.headers,
                                       params={"keyword": query, "page": 1})
        request_json = json.loads(request.text)
        output = []
        for film in request_json['films']:
            output.append(SEARCH(film))
        return output
    
    def get_film(self, film_id):
        API = 'https://kinopoiskapiunofficial.tech/api/v2.2/'
        request = requests.get(API + f'films/{str(film_id)}', headers=self.headers)
        request_json = json.loads(request.text)
        with open("req.json", "w") as f:
            json.dump(request_json, f, indent=4)
        return FILM(request_json)
    
    def money(self, film_id):
        API = 'https://kinopoiskapiunofficial.tech/api/v2.2/'
        request = requests.get(API + f'films/{str(film_id)}/box_office', headers=self.headers)
        request_json = json.loads(request.text)

        budget, amount = None, None
        for money in request_json['items']:
            if money["type"] == "BUDGET":
                budget = MONEY(money).budget
            if money["type"] == "WORLD":
                amount = MONEY(money).amount

        return budget, amount  # str/False, str/False 
    
    def seasonsCount(self, film_id):
        API = 'https://kinopoiskapiunofficial.tech/api/v2.2/'
        request = requests.get(API + f'films/{str(film_id)}/seasons', headers=self.headers)
        request_json = json.loads(request.text)
        return str(request_json['total'])  # 1 number (total seasons)
    
    def staff(self, film_id):  # top 5 actor
        try:
            API = 'https://kinopoiskapiunofficial.tech/api/v1/'
            request = requests.get(API + f'staff?filmId={str(film_id)}', headers=self.headers)
            request_json = json.loads(request.text)
            output = []
            for actor in request_json:
                if len(output) >= 5:
                    break
                if STAFF(actor).professionKey:
                    output.append(STAFF(actor).actor_name)
            return '\n'.join(output)      
        except:
            return None