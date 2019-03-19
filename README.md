# ping-pong-ts
Automated system to track office ping pong using Google Sheets for the front end, Google Forms for game and player submission, Python for automation, and sublee's trueskill library for tracking player skill.

## Background
I was looking for a side project to occupy my downtime, and figured why not combine three of my favorite things: Ping Pong, coding, and competition!

## How it works

**1. ```History.py```, ```Player.py```, ```Game.py```, ```TournamentTeam.py```** - This classes are used to store information and make it easy to access. I use a History class as an interface for looking at the player and game databases (```roster.pkl``` and ```game_database.pkl```, respectively), adding players and games, and running tournaments.

Upon initialization, a new History class reads in ```roster.pkl``` and ```game_database.pkl```. ```roster.pkl``` is a dictionary of Player objects, with that player's playerID as a key. ```game_database.pkl``` is the same, except it is a dictionary of Game objects with the gameID as it's key.

**2. ```sheets_interface```** - This contains all the necessary functions to pull submission from Google Forms, reconcile them with the local database, and then update the front-facing Sheets document.

**3. ```refresh.py```** - This is file that brings it all together. It first creates a History class that loads in all the local data. Then it connects to Google sheets and pulls all of the new game and player submissions. It asks if everything looks ok, then automatically updates all the info on the front-facing Sheets document using the functions from sheets_inteface.

To read more about how TrueSkill works to rank players, here are a couple links that helped me:
http://www.moserware.com/2010/03/computing-your-skill.html
https://www.microsoft.com/en-us/research/project/trueskill-ranking-system/

To learn more about connecting to Google Sheets, here are the links that helped me:
https://developers.google.com/sheets/api/quickstart/python
https://pygsheets.readthedocs.io/en/stable/ and https://github.com/nithinmurali/pygsheets

## Built With
**libraries**   
* pygsheets
* pandas
* numpy
* trueskill

**PyCharm**  
* IDE and debugging  

## Authors
* **Project:** Andrew Walker  
* **TrueSkill Implementation:** https://github.com/sublee/trueskill
* **Original TrueSkill Paper:** https://www.microsoft.com/en-us/research/wp-content/uploads/2006/01/TR-2006-80.pdf
