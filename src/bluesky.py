from atproto import Client, models,client_utils
from typing import Dict
import os
from dotenv import load_dotenv 


class Bluesky:
    '''
    Class with the functions for bluesky
    Not a lot 
    '''
    def post_game(game_id: str, data: Dict[str, str],post: bool) -> None:   
        '''
        takes the created img and posts it to the account given by the .env file
        args
            gameId  the gameId
            data    the output of the prep.py functions with all the data that is plotted.
                    we only use the teamnames,dates and so on
            post    bool to decide if you want to post the img
        ''' 
        if post==True:
            client = Client()
            load_dotenv()

            client.login(os.environ.get('BLUESKY_USERNAME'), os.environ.get('BLUESKY_PASSWORD'))

            message=f"Shot overview for {data['team_name_home']} vs. {data['team_name_away']}\n"
            tag="#"+data['team_home']+"vs"+data['team_away']
            text = client_utils.TextBuilder().text(message).tag(tag,tag[1:])
            try:
                with open(f'./img/{game_id}.png', 'rb') as f:
                    img_data = f.read()
                aspect_ratio = models.AppBskyEmbedDefs.AspectRatio(height=100, width=100)
                client.send_image(
                    text=text,
                    image=img_data,
                    image_alt=f"{data['team_name_home']} vs. {data['team_name_away']}",
                    image_aspect_ratio=aspect_ratio)
            except FileNotFoundError as e:
                print(f"Error: {e}")
        else:
            pass
