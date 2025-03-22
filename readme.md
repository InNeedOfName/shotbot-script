# What is is this?

This is a small script, that will:

- Check if any NHL games happened yesterday
- Add the gameIds into a cue
- For each gameId
  - Create a sqlite database
  - Query the NHL API and fill the database
  - Query the database for different information
  - create a plot out of it and save it as img
  - post the img on bluesky
  
## How do I use it?

run

````=python
pip install -r requirements
python3 main.py
````

to install the requirements and run the script.

If you want the imgs posted, observe the Bluesky part Afterwards, you can just run the main.py.

## Bluesky part

If you want the script to post on your account, set the post argument to True.
You have to create a .env file for your bluesky account with your handle and password in the form:

````=python
BLUESKY_USERNAME="your_handle"
BLUESKY_PASSWORD="your_password"
````

the .env file should be located at ./src

## DBs & imgs

If you want to keep the created databases and imgs for your own experiments/analysis, just set

````=python
Util.do.clean_up(gameId,dump_img=False,dump_db=False)
````

It is set by default to False.

## misc

### Can I do it for single games?

Sure, get the game Id of the game that you'd like to take a look at and replace

````=python
gameIds=functions.Util.scheduler()
````

with

````=python
gameIds= the-gameId-you-want-to-look-at
````

The can get the gameId of a game from the NHL website, for example:

````=python
https://www.nhl.com/gamecenter/fla-vs-mtl/2025/03/15/2024021060
````

the gameId for this game is 2024021060, which consists of:

````=bash
2024 = Starting year of the season
02 = regular season game
1060 = number of the game
````

If you want to do it properly, just write
the gameId into the main() and watch out for the indents.

### Your rink looks bad

That's not a question.

### What is anyone supposed to do with that kind of analysis?

I just extracted,transformed,loaded and visualised data.
You can draw the conclusion that you want from it, it's just statistics afterall.
If you want a more in depth analysis of the shots, send me a message.
