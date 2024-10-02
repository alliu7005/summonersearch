# summonersearch

NOTE: I made this project in 2021 but didn't upload it to my GitHub until now.


Summoner Search
Video Demo: https://youtu.be/q625R7HYhaQ

Description:
My project is a web application called Summoner Search. It uses the Cassiopeia framework to access the Riot API, obtaining stats from the popular multiplayer online battle arena (or MOBA) game League of Legends. It loads the last 20 games from any player's
match history from multiple regions across the world into a SQL database, allowing the user to query this data based on statistics such as the match result, the player's champion, their role, and more to create a table to express the matches in which the criteria
queried for is fulfilled.
My Python program is application.py. The web application involves two routes, / and /query. When the / route is obtained via "GET," the user is prompted to enter a player's username and the server they play on in index.html. Submitting this form loads that player's
match history and parses it for certain statistics, specifically, kill/death ratio, vision score, creep score, the match result, the champion played, the player's username, the player's role, and the date the match was played into the matchlist table within the database
matches.db. The form then uses the "POST" method of the / route, displaying a page (summoner.html) with the summoner's username, their level, their winrate, the total amount of matches loaded in the database, and a counter of champions played in the last 20 games. The
counter is there so that the user knows which champions were played, making querying for games with those specific champions simpler. The "Return" button returns the user to the load page, which they can also do by pushing the "Home" button in the navbar.
This page also allows the user to query that database based on all of the statistics mentioned above. The program converts the final field's input into a string or an int/float depending on what statistic the user queried for. I decided on the querying function to
give my application more of a unique spin. Several websites already exist which show a user's match history, so I wanted to expand upon that. This is also the reason that I implemented the ability to load multiple users into the database. Querying the database will
return queried.html, displaying a table with all matches that satisfy the query, along with the statistics of that user for each of the matches. The user can then return to the load page to load more matches using the "Return" button. If the values of the query are
invalid, the program will instead return error.html, which displays a message customized for the issue and a "Return" button. Error.html is implemented using "try" and "except," and it provides easier debugging and a better user experience.
All of the html files extend from layout.html and use the style sheet styles.css. Layout.html is a generally simple base for the web application. The navbar is assigned here, allowing the user to return to the load page at any time, and also displaying the title of the
application. Styles.css is also succint. It defines some margin spacings, the background color, the table styling, and allows some elements to be centered. Finally, requirements.txt is a list of all the requirements to run the file. It comprises of Cassiopeia's requirements
and the requirements for my Flask application.
