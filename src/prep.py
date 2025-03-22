import src.db as db
import src.get as get
import pandas as pd
from collections import defaultdict

'''
These methods prepare the data from the database, to be plotted
'''


def params(gameId):
    ''''
    Defining the params that will be passed
    args:
        gameId(int)
    returns:
        id_home(int):          team Id for home team
        id_away(int)           team Id for away team
        team_home(str):        team abbreviation for home team
        team_away(str):        team abbreviation for away team
        team_name_home(str):    team Name for home team
        team_name_away(str):    team Name for away team
        date(str):          date of the game in mm-dd-yyyy format
        place(str):         place of the game
    '''
    call=get.data.team(gameId)
    id_home=call[0][0]
    id_away=call[1][0]
    team_home=call[0][1]
    team_away=call[1][1]
    team_name_home=call[0][2]
    team_name_away=call[1][2]
    date=get.data.game_info(gameId)[1]
    place=get.data.game_info(gameId)[0]
    return {'id_home':id_home,'id_away':id_away,'team_home':team_home,'team_away':team_away,
            'team_name_home':team_name_home,'team_name_away':team_name_away,
            'date':date,'place':place,'gameId':gameId}

def kde(id_home,id_away,gameId):
    '''
    Kernel Density Estimation of the list of shotpositions for each team

  
    args:
        id_home(int):      team Id of the home Team
        id_away(int):      team Id of the away Team
        gameId(int):    the Id of the game
    returns   
        dict:           the result of the KDE 
    '''
    positions_home=db.query.kdePlot(id_home,gameId)
    positions_away=db.query.kdePlot(id_away,gameId)
    data_home=pd.DataFrame({'xPos':[-x[0] for x in positions_home],'yPos':[x[1] for x in positions_home],'team': f'{id_home}'})
    data_away=pd.DataFrame({'xPos':[x[0] for x in positions_away],'yPos':[x[1] for x in positions_away],'team': f'{id_away}'})
    combined_data = pd.concat([data_home, data_away])
    return {'data_home':data_home,'data_away':data_away,'combined_data':combined_data}

def shooters_by_area(id_home,id_away,gameId):
    '''
    Reordering the list of target counts by players as a dict

    args:
        id_home(int):      team Id of the home Team
        id_away(int):      team Id of the away Team
        gameId(int):    the Id of the game
    returns
        d_home(dict):      the players, their shot targets and 
                        associated counts as a dict for the home team
        d_away(dict):      the players, their shot targets and 
                        associated counts as a dict for the away team
    '''
    d_home= defaultdict(lambda:defaultdict(int))
    d_away= defaultdict(lambda:defaultdict(int))
    for (player,reason,count) in db.query.targetByShooter(id_home,gameId):
        d_home[player][reason]+=count
    for (player,reason,count) in db.query.targetByShooter(id_away,gameId):
        d_away[player][reason]+=count
    return {'d_home':d_home,'d_away':d_away}


def shot_types(id_home,id_away,gameId):
    '''
    args:
        id_home(int):      team Id of the home Team
        id_away(int):      team Id of the away Team
        gameId(int):    the Id of the game
    returns
        dict:           different shot types and sum of shots per team as a dict
    '''
    shot_types_home=db.query.shotTypePlot(id_home,gameId)
    shot_types_away=db.query.shotTypePlot(id_away,gameId)
    shot_sums_home=sum([x[1] for x in shot_types_home])
    shot_sums_away=sum([x[1] for x in shot_types_away])
    return {'shot_sums_home':shot_sums_home,'shot_sums_away':shot_sums_away,
            'shot_types_home':shot_types_home,'shot_types_away':shot_types_away}

def table(id_home,id_away,gameId):
    '''
    args:
        id_home(int):      team Id of the home Team
        id_away(int):      team Id of the away Team
        gameId(int):    the Id of the game
    returns
        dict:           the table data as a dict
    '''
    table_home=db.query.tablePlot(id_home,gameId)
    table_away=db.query.tablePlot(id_away,gameId)
    table_data = [[' ', ' ', ' '],
            [sum([x[0] for x in table_home]), 'Total Shots', sum([x[0] for x in table_away])],
            [table_home[1][0], 'Goals', table_away[1][0]],
            [table_home[0][0], 'On Goal', table_away[0][0]],
            [table_home[2][0], 'Misses', table_away[2][0]],
            [table_home[3][0],'Post/bar',table_away[3][0]],
            [table_home[4][0],'Opponent blocked',table_away[4][0]],
            [table_home[5][0],'Teammate blocked',table_away[5][0]]]
    return {'table_data':table_data}

def targets_by_period(id_home,id_away,gameId):
    '''
    args:
        id_home(int):      team Id of the home Team
        id_away(int):      team Id of the away Team
        gameId(int):    the Id of the game
    returns
        dict:           the counts of the targets with the period as a dict
    '''
    event_counts_home= defaultdict(lambda: defaultdict(lambda:defaultdict))
    event_counts_away= defaultdict(lambda: defaultdict(lambda:defaultdict))
    for elem in db.query.targetByPeriod(id_home,gameId):
        event_counts_home[str(elem[1])][elem[2]]=elem[0]
    for elem in db.query.targetByPeriod(id_away,gameId):
        event_counts_away[elem[1]][elem[2]]=elem[0]
    return {'event_counts_home':event_counts_home,'event_counts_away':event_counts_away}

def prepare(gameId):
    '''
    peparing the params like id_home,id_away so all the functions are callable
    '''
    data={}
    data.update(params(gameId))
    return data

def all(gameId):
    '''
    Taking all the results of the functions above and put them into
    a dict structure to be easily callable
    '''
    data={}
    id_home=prepare(gameId)['id_home']
    id_away=prepare(gameId)['id_away']
    data.update(prepare(gameId))
    data.update(kde(id_home, id_away,gameId))
    data.update(shooters_by_area(id_home, id_away,gameId))
    data.update(shot_types(id_home, id_away,gameId))
    data.update(table(id_home, id_away,gameId))
    data.update(targets_by_period(id_home, id_away,gameId))
    return data

