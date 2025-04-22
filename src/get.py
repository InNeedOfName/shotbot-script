from src.basedata import NHL_TEAMS,BASE_URL
import requests
from PIL import Image
import cairosvg
import json
from io import BytesIO
from typing import List,Dict 
import logging

class image:
    def team_img(team_id: int) -> Image.Image:        
        '''
        looks up and returns team logo
        args:
            takes team Abbrev
        returns: 
            the team image from svg as png
        '''
        try:
            team = NHL_TEAMS.get(team_id)
            response = requests.get(f"https://assets.nhle.com/logos/nhl/svg/{team}_light.svg")
            logging.info(f'Fetched teamImg for team {team_id}')
            return Image.open(BytesIO(cairosvg.svg2png(bytestring=response.content)))
        except requests.RequestException as e:
           logging.error(f'Error in fetching teamImg for team {team_id}, error: {e}')

    def player_img(player_id: int) -> Image.Image:
        '''
        get a players headshot
            args: 
                playerId
            returns:
                headshot as png
        '''
        try:
            headshot_url = json.loads(requests.get(f"{BASE_URL}player/{player_id}/landing").content)['headshot']
            response = requests.get(headshot_url)
            logging.info(f'Fetched playerImg for player {player_id}')
            return Image.open(BytesIO(response.content))
        except requests.RequestException as e:
            logging.error(f'Error in fetching playerImg for player {player_id}, error: {e}')
            return Image.new('RGB', (1, 1))  # Return a blank image in case of failure

class data:
    def team(gameId: str) -> List[List[str]]:        
        '''
        For a gameId, get the teams iD,abbreviation and Name
        args:
            gameId
        returns:
            for both teams teamId,teamAbbrev,TeamName
        '''
        try:
            response = requests.get(f"{BASE_URL}gamecenter/{gameId}/landing").json()
            logging.info(f'Fetched teamData for {gameId} ')
            return [
                [response['homeTeam']['id'], response['homeTeam']['abbrev'], response['homeTeam']['commonName']['default']],
                [response['awayTeam']['id'], response['awayTeam']['abbrev'], response['awayTeam']['commonName']['default']]
            ]
        except requests.RequestException as e:
            logging.error(f'Error when fetching team data for game {gameId},Error: {e}')
            return []

    def game_info(gameId: str) -> List[str]:
        '''
        Get the games venue and gameDate from the gameId
        args 
            gameId
        return:
            venue,date
        '''
        try:
            response = requests.get(f"{BASE_URL}gamecenter/{gameId}/play-by-play").json()
            logging.info(f'Fetched gameVanue and gameDate from game {gameId}')
            return [response['venue']['default'], response['gameDate']]
        except requests.RequestException as e:
            print(f"Request failed: {e}")
            logging.error(f'Error when fetching game venue and date for game {gameId}')
            return []

    
    def game_data(gameId: str) -> List[Dict]:
        '''
        get a games event from the gameId
        args:
            gameId
        returns 
            play-by-play information for the gameId
        '''
        try:
            response = requests.get(f"{BASE_URL}gamecenter/{gameId}/play-by-play").json()
            logging.info(f'fetched plays for game {gameId}')
            return response.get('plays', [])
        except requests.RequestException as e:
            print(f"Request failed: {e}")
            logging.error(f'Error when fetching gameEvents from game {gameId}')
            return []
    def player_name(player_id: int) -> str:        
        '''
        transform a playerId to to corresponding Name
        args:
            playerId
        returns:
            Playername in the shape C. Caufield
        '''
        try:
            response = requests.get(f"{BASE_URL}player/{player_id}/landing").json()
            logging.info(f'transformed player {player_id} to name')
            return f"{response['firstName']['default'][0]}. {response['lastName']['default']}"
        except requests.RequestException as e:
            logging.error(f'Error when transforming playerId to name for player {player_id}')
            return "Unknown Player"