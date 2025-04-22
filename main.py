
import src.basedata as basedata
import src.prep as prep
import src.db as db
import src.plot as plot
import src.bluesky as bluesky
import src.Util as Util
import time
import logging


# ToDo
# add logging
# put into docker
# make runable


def main():
  
    gameIds=Util.do.scheduler()
    basedata.configure_logging()
    if len(gameIds)==0:
        logging.info('No Game today')
    else:
        for gameId in gameIds:
            prep.params(gameId)
            db.table.create(gameId)
            db.table.fill(gameId)
            data=prep.all(gameId)
            plot.plot.final(data)
            bluesky.Bluesky.post_game(gameId,data,post=True)
            Util.do.clean_up(gameId,dump_img=False,dump_db=False)
            logging.info(f'Finished run for {gameId}')
            time.sleep(5)
    logging.info('Finished execution')


if __name__=="__main__":
    main()
    

