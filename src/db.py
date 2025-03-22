
import src.Util as Util
import src.get as Get
import sqlite3
from typing import List, Tuple

class table:
    '''
    Defining the tables that we are going to use
    '''
    def create(gameId:str) -> None:
        '''
        Creating the tables that are being used
        '''
        tables=[
    '''CREATE TABLE IF NOT EXISTS goal_table(
        eventOwnerTeamId INTEGER, shooterId INTEGER, shotType TEXT,
        assist1 INTEGER, assist2 INTEGER, reason TEXT, time FLOAT,
        xPos INTEGER, yPos INTEGER);''',

    '''CREATE TABLE IF NOT EXISTS shot_table(
        eventOwnerTeamId INTEGER, shooterId INTEGER, shotType TEXT,
        time FLOAT, xPos INTEGER, yPos INTEGER, goalieId INTEGER);''',

    '''CREATE TABLE IF NOT EXISTS miss_table(
        eventOwnerTeamId INTEGER, shooterId INTEGER, shotType TEXT,
        miss_reason TEXT, time FLOAT, xPos INTEGER, yPos INTEGER);''',

    '''CREATE TABLE IF NOT EXISTS block_table(
        eventOwnerTeamId INTEGER, shooterId INTEGER, reason TEXT,
        time FLOAT, xPos INTEGER, yPos INTEGER);'''
        ]
        conn = sqlite3.connect(f'./db/{gameId}.sqlite')
        cursor = conn.cursor()
        for query in tables:
            cursor.execute(query)
        conn.commit()
        
        

    def fill(gameId:str ) ->None :
        '''
        Filling the tables we created with create()
        '''
        conn = sqlite3.connect(f'./db/{gameId}.sqlite')
        cursor = conn.cursor()
        mapping = {
        'goal': {
        'query': '''INSERT INTO goal_table(eventOwnerTeamId, shooterId, shotType, assist1, assist2, reason, time, xPos, yPos)
                    VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?)''',
        'params': lambda elem: (
            elem['details'].get('eventOwnerTeamId'),
            elem['details'].get('scoringPlayerId'),
            elem['details'].get('shotType'),
            elem['details'].get('assist1PlayerId'),
            elem['details'].get('assist2PlayerId'),
            'Goal',
            Util.calc.time(elem['periodDescriptor']['number'],elem['timeInPeriod']),
            *Util.calc.position(elem['homeTeamDefendingSide'], elem['details']['xCoord'], elem['details']['yCoord'])
        )
        },
        'shot-on-goal': {
        'query': '''INSERT INTO shot_table(eventOwnerTeamId, shooterId, shotType, time, xPos, yPos)
                    VALUES(?, ?, ?, ?, ?, ?)''',
        'params': lambda elem: (
            elem['details'].get('eventOwnerTeamId'),
            elem['details'].get('shootingPlayerId'),
            elem['details'].get('shotType'),
            Util.calc.time(elem['periodDescriptor']['number'],elem['timeInPeriod']),
            *Util.calc.position(elem['homeTeamDefendingSide'], elem['details']['xCoord'], elem['details']['yCoord'])
        )
        },
        'missed-shot': {
        'query': '''INSERT INTO miss_table(eventOwnerTeamId, shooterId, shotType, miss_reason, time, xPos, yPos)
                    VALUES(?, ?, ?, ?, ?, ?, ?)''',
        'params': lambda elem: (
            elem['details'].get('eventOwnerTeamId'),
            elem['details'].get('shootingPlayerId'),
            elem['details'].get('shotType'),
            elem['details'].get('reason'),
            Util.calc.time(elem['periodDescriptor']['number'],elem['timeInPeriod']),
            *Util.calc.position(elem['homeTeamDefendingSide'], elem['details']['xCoord'], elem['details']['yCoord'])
        )
        },
        'blocked-shot': {
        'query': '''INSERT INTO block_table(eventOwnerTeamId, shooterId, reason, time, xPos, yPos)
                    VALUES(?, ?, ?, ?, ?, ?)''',
        'params': lambda elem: (
            elem['details'].get('eventOwnerTeamId'),
            elem['details'].get('shootingPlayerId'),
            elem['details'].get('reason'),
            Util.calc.time(elem['periodDescriptor']['number'],elem['timeInPeriod']),
            *Util.calc.position(elem['homeTeamDefendingSide'], elem['details']['xCoord'], elem['details']['yCoord']))
            }
        }

        for elem in Get.data.game_data(gameId):
            eventType = elem['typeDescKey']
            if eventType in mapping:
                query_info = mapping[eventType]
                cursor.execute(query_info['query'], query_info['params'](elem))
        conn.commit()
        conn.close()

class query:
    ''''
    In this, we have the SQL clauses which are being used to plot the functions
    Written as functions so we can call them with the teamId
    '''
    def kdePlot(teamId:int,gameId:str)->List[Tuple[int,int]]:
        '''
        Contains query for the KDE plots which calculate the density of shotpositions
        on the ice for a team.
        '''
        conn = sqlite3.connect(f'./db/{gameId}.sqlite')
        cursor = conn.cursor()
        c = cursor.execute('''SELECT xPos,yPos
                    FROM shot_table where eventOwnerTeamId=? 
                    UNION ALL 
                    SELECT xPos,yPos FROM miss_table WHERE eventOwnerTeamId=?
                    UNION ALL
                    SELECT xPos,yPos FROM goal_table WHERE eventOwnerTeamId=?
                    ;''',(teamId,teamId,teamId,)).fetchall()
        conn.close()
        return c
    
    def tablePlot(teamId:int,gameId:str) -> List[Tuple[int, str]]:
        '''' 
        Contains query for the table with numbers for a team
        goals,misses,hits on the post/crossbar,shots blocked by opponent or teammate
        '''
        conn = sqlite3.connect(f'./db/{gameId}.sqlite')
        cursor = conn.cursor()
        c= cursor.execute('''
                SELECT COUNT(*),'On goal' AS reason FROM shot_table WHERE eventOwnerTeamId = ? 
                UNION ALL SELECT COUNT(*), 'Goal' as reason FROM goal_table WHERE eventOwnerTeamId = ? 
                UNION ALL SELECT COUNT(*), 'miss' as reason FROM miss_table WHERE eventOwnerTeamId = ? AND miss_reason NOT LIKE '%post%' AND NOT miss_reason='hit-crossbar'
                UNION ALL SELECT COUNT(*), 'metal' as reason FROM miss_table WHERE eventOwnerTeamId = ? AND miss_reason LIKE '%post%' OR miss_reason='hit-crossbar'
                UNION ALL SELECT COUNT(*), 'OppBlock' as reason FROM block_table WHERE eventOwnerTeamId = ? AND reason='blocked'
                UNION ALL SELECT COUNT(*), 'TeamBlock' AS reason FROM block_table WHERE eventOwnerTeamId = ? AND reason!='blocked';
                ''',(teamId,teamId,teamId,teamId,teamId,teamId,)).fetchall()
        conn.close()
        return c
    
    def shotTypePlot(teamId:int,gameId:str)-> List[Tuple[str, int]]:
        '''
        Contains query for the plot of different shottypes (wristshot,slapshot,..)
        for a team
        '''
        conn = sqlite3.connect(f'./db/{gameId}.sqlite')
        cursor = conn.cursor()
        ''' Data for the shotTypePlot, shotsTypes per Team'''
        c = cursor.execute('''SELECT shotType,COUNT(shotType) 
                              FROM (SELECT shotType FROM miss_table WHERE eventOwnerTeamId=? 
                              UNION ALL SELECT shotType FROM shot_table WHERE eventOwnerTeamId=? 
                              UNION ALL SELECT shotType FROM goal_table WHERE eventOwnerTeamId=?) 
                              GROUP BY shotType ORDER BY shotType;''',(teamId,teamId,teamId,)).fetchall()
        conn.close()
        return c
    
    def targetByPeriod(teamId:int,gameId:str)-> List[Tuple[int, str, str]]:
        ''''
        Contains query which returns the different targets of shots
        grouped by period of the game for a team.
        Only for regular gametime, no OT implemented yet.
        '''
        conn = sqlite3.connect(f'./db/{gameId}.sqlite')
        cursor = conn.cursor()
        c=  cursor.execute('''SELECT 
        COUNT(*),CASE 
        WHEN time > 0 AND time <= 20 THEN 'P1'
        WHEN time > 20 AND time <= 40 THEN 'P2'
        WHEN time > 40 AND time <= 60 THEN 'P3' 
        END AS time_range,reason FROM (
        SELECT time, 'on goal' AS reason FROM shot_table WHERE eventOwnerTeamId = ? 
        UNION ALL 
        SELECT time, 'goal' AS reason FROM goal_table WHERE eventOwnerTeamId = ? 
        UNION ALL 
        SELECT time, 'miss' AS reason FROM miss_table WHERE eventOwnerTeamId = ? AND miss_reason NOT LIKE '%post%' AND miss_reason != 'hit-crossbar' 
        UNION ALL 
        SELECT time, 'metal' AS reason FROM miss_table WHERE eventOwnerTeamId = ? AND (miss_reason LIKE '%post%' OR miss_reason = 'hit-crossbar') 
        UNION ALL 
        SELECT time, 'blocked' AS reason FROM block_table WHERE eventOwnerTeamId = ? AND reason = 'blocked' 
        UNION ALL 
        SELECT time, 'teammate-blocked' AS reason FROM block_table WHERE eventOwnerTeamId = ? AND reason != 'blocked'
        ) AS data WHERE time > 0 AND time <= 60 GROUP BY time_range, reason;''',
        (teamId,teamId,teamId,teamId,teamId,teamId,)).fetchall()
        return c
    
    def targetByShooter(teamId:int,gameId:str)-> List[Tuple[int, str, int]]:
        '''
        Contains query that looks up the different shottargets(miss,goal,ongoal,..)
        for each shooter of a team.
        currently limited to the top 4 shooters.
        '''
        conn = sqlite3.connect(f'./db/{gameId}.sqlite')
        cursor = conn.cursor()
        '''getData9'''
        c = cursor.execute('''WITH reason_counts AS (
        SELECT shooterId, reason, COUNT(reason) AS reasonCount
        FROM (
        SELECT shooterId, time, 'on goal' as reason
        FROM shot_table
        WHERE eventOwnerTeamId = ?
        UNION ALL
        SELECT shooterId, time, 'goal' as reason
        FROM goal_table
        WHERE eventOwnerTeamId = ?
        UNION ALL
        SELECT shooterId, time,
            CASE
                WHEN miss_reason IN ('hit-crossbar', 'hit-post') THEN 'metal'
                ELSE 'miss'
            END as reason
        FROM miss_table
        WHERE eventOwnerTeamId = ?
        UNION ALL
        SELECT shooterId, time, reason
        FROM block_table
        WHERE eventOwnerTeamId = ?
        ) AS combined_results
        GROUP BY shooterId, reason
        ), shooter_totals AS (
        SELECT rc.shooterId, SUM(rc.reasonCount) AS totalReasonCount
        FROM reason_counts rc
        GROUP BY rc.shooterId
        ),ranked_shooters AS (
        SELECT rc.shooterId, rc.reason, rc.reasonCount,
            ROW_NUMBER() OVER (PARTITION BY rc.shooterId ORDER BY rc.reasonCount DESC) AS reasonRank,
            st.totalReasonCount,
            DENSE_RANK() OVER (ORDER BY st.totalReasonCount DESC) AS shooterRank
        FROM reason_counts rc
        JOIN shooter_totals st ON rc.shooterId = st.shooterId
        ),top_shooters AS (
            SELECT shooterId
            FROM ranked_shooters
            GROUP BY shooterId
            ORDER BY MIN(shooterRank)
            LIMIT 4)
        SELECT rs.shooterId, rs.reason, rs.reasonCount
        FROM ranked_shooters rs
        JOIN top_shooters ts ON rs.shooterId = ts.shooterId
        ORDER BY rs.totalReasonCount DESC, rs.shooterId, rs.reasonRank;''',(teamId,teamId,teamId,teamId)).fetchall()
        conn.close()
        return c
  