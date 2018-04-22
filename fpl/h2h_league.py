import itertools
import requests

API_BASE_URL = "https://fantasy.premierleague.com/drf/"

class H2HLeague(object):
    """
    A class representing a h2h league in the Fantasy Premier League.
    """
    def __init__(self, league_id):
        self.id = league_id
        self._information = self._information()
        self._league = self._information["league"]

        #: A dictionary containing information about new entries to the league.
        self.new_entries = self._information["new_entries"]

        #: The name of the league.
        self.name = self._league["name"]
        #: The date the league was created.
        self.created = self._league["created"]
        #: The gameweek the league started in.
        self.started = self._league["start_event"]
        #: Information about the knockout rounds.
        self.ko_rounds = self._league["ko_rounds"]

        self.standings = self._information["standings"]["results"]
        """
        A list (of dictionaries) containing information about the league's
        standings.
        """

    @property
    def type(self):
        """The type of league that the league is."""
        return self._league["league_type"]

    def _information(self):
        """Returns information about the given league."""
        return requests.get("{}leagues-h2h-standings/{}".format(
            API_BASE_URL, self.id)).json()    

    def __str__(self):
        return "{} - {}".format(self.name, self.id)
        
    
    def get_fixtures(self, email, password):
        """
        Returns h2h results and fixtures for the given league.
        Login to FPL is required to access this data.
        
        :param string user: email 
        :param string password: password
        """
        # login to FPL
        session = self.login_session(email, password)
        
        fixtures = []
        # iterate through all available pages
        for page in itertools.count(start=1):
            url = "{}leagues-entries-and-h2h-matches/league/{}?page={}".format(API_BASE_URL, self.id, page)
            page_results = session.get(url).json()['matches']['results']
            # check if page exists 
            if page_results:
                fixtures.extend(page_results)
            else:
                return fixtures 
            
            
    def login_session(self, email, password):
        """
        Returns a requests session with FPL login authentication.
        
        :param string user: email 
        :param string password: password 
        """
        session = requests.Session()
        
        # initial request to retrieve csrftoken
        session.get('https://fantasy.premierleague.com/')
        csrftoken = session.cookies['csrftoken']
        
        # login request 
        body = {
            'csrfmiddlewaretoken': csrftoken, 
            'login': email, 
            'password': password, 
            'app': 'plfpl-web',
            'redirect_uri': 'https://fantasy.premierleague.com/a/login'
        }
        response = session.post('https://users.premierleague.com/accounts/login/', data=body)
        assert "Sign Out" in response.text, "Login unsuccessful, check credentials" 
        
        return session
    
   
    
