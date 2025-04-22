import os
from typing import List, Dict,Tuple
import requests
from datetime import date,timedelta
from src.basedata import BASE_URL
import matplotlib
import logging

class calc:
    '''
    Class for utility calculate functions
    '''
    
    def max_val(d1: Dict[str, Dict[str, int]], d2: Dict[str, Dict[str, int]]) -> int:     
        '''
        Getting the max val of 2 dicts
        args:
            d1,d2 Input dicts
        returns:
            int: the max Value from the dicts
        '''
        return max(max([sum(x.values()) for x in d1.values()]), max([sum(x.values()) for x in d2.values()]))
    
    def time(period: int, time: str) -> float:
        '''
        transform time from string to a float while adapting to the periods
        args:
            period
            time 
        return:
            time as a float
        '''
        t=str((period-1)*2 + int(time[:1]))+time[1:]
        mins,secs=t.split(":")
        logging.info(f'Fixed time for {period},{time}')
        return int(mins)+(int(secs)/60)
        
    def position(side: str, x_pos: int, y_pos: int) -> Tuple[int, int]:
        '''
        Change xPos,yPos so both teams get one side of the ice 
        in respect to playing direction.
        args:
            side    side of the homeDefendingSide
            x_pos   Position of the player on the x-axis
            y_pos   Position of the player on the y-axis
        returns
            x_pos,y_pos as transformed values
        '''
        logging.info(f'Attempting to fix positions {x_pos},{y_pos}')
        if side=='left':
            x_pos,y_pos=-x_pos,-y_pos 
            logging.info(f'Fixed positions {x_pos},{y_pos}')
        return x_pos,y_pos
    
class do:
    '''
    Class of utility functions that change/do somthing
    '''

    def clean_up(gameId: str,dump_img:bool,dump_db:bool) -> None:
        '''
        Remove files associated with a game ID.
        args: 
            game id : the id of the game that is supposed to be deleted
            dump_img: bool for the case that you want to keep the img,default False
            dump_db: bool for the case that you want to keep the db,default False
        returns:
            nothing
        '''
        if dump_img==True:
            try:
                os.remove(f'./data/{gameId}.png')
                logging.info('Clean up of img succesful')
            except FileNotFoundError as e:
                logging.error(f'IMG file not found,{e}')
        if dump_db==True:
            try:
                os.remove(f'./data/{gameId}.sqlite')   
                logging.info('Clean up of database succesful')         
            except FileNotFoundError as e:
                logging.error(f'database file not found,{e}')
        else:
            pass

    def configure_plot(ax,title:str, extent:list) -> None:
        '''
        configure the axis for the kde Plot
        '''
        ax.set_title(title)
        ax.set_xlim(extent[0], extent[1])
        ax.set_ylim(extent[2], extent[3])
        ax.tick_params(axis='both', which='both', length=0, labelsize=0)
        ax.set_xlabel("")
        ax.set_ylabel("")
        logging.info('Configured plot')

    def scheduler() -> List[int]:
        '''
        Get a list of game IDs for the previous day.

        Returns:
            gameList: List of game IDs.
        '''
        gameList=[]
        try:
            response = requests.get(f"{BASE_URL}schedule/{date.today() - timedelta(days=1)}").json()
            for entry in response['gameWeek']:
                if entry['date'] == str(date.today() - timedelta(days=1)):
                    gameList.extend(game['id'] for game in entry['games'])

            logging.info(f'Got gameIds for yesterday')
        except requests.RequestException as e:
            logging.error(f'Schedulerer failed, {e}')
        return gameList
   

