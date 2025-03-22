
import src.prep as prep
import src.db as db
import src.plot as plot
import src.bluesky as bluesky
import src.Util as Util
import time


# ToDo
# add bash file
# put in cloud?


def main():
  
    gameIds=Util.do.scheduler()
    if len(gameIds)==0:
        print("No games today, kind of sad.")
    else:
        for gameId in gameIds:
            prep.params(gameId)
            db.table.create(gameId)
            db.table.fill(gameId)
            data=prep.all(gameId)
            plot.plot.final(data)
            bluesky.Bluesky.post_game(gameId,data,post=True)
            Util.do.clean_up(gameId,dump_img=True,dump_db=True)
            time.sleep(5)


if __name__=="__main__":
    main()
    

