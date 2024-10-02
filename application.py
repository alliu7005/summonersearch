import os

import random2
import datapipelines
import PIL
from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from tempfile import mkdtemp
import random
import cassiopeia as cass
from cassiopeia import Summoner, Match, Patch
from cassiopeia.data import Season, Queue, Lane
from cassiopeia.core.match import Participant
from cassiopeia.core import MatchHistory
from collections import Counter
import datetime
from datetime import timedelta, datetime

import arrow
from arrow import Arrow

#cass settings
Settings = {
    
    "global": {
        "version_from_match": "patch",
        "default_region": None
        
    
    },
    
    "pipeline": {
        "Cache": {},

        "DDragon": {},
        
        

        "RiotAPI": {
            "api_key": "RGAPI-2a61992f-8ed3-4e59-a3ba-cb97ed6c201d"
        }

    }
}


cass.apply_settings(Settings)


try:
    db = SQL("sqlite:///matches.db")
    db.execute("DELETE FROM matchlist")
except:
    print("failure to load database")

# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

#riot api
cass.set_riot_api_key("RGAPI-2a61992f-8ed3-4e59-a3ba-cb97ed6c201d")


# Ensure responses aren't cached
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

def error(message, code=400):
    return render_template("error.html", message = message, code=code)
    
    
@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "GET":
        return render_template("index.html")
        
    else:
        try:
            name = request.form.get("name")
            region = request.form.get("region")
        except:
            
            return error("No name given")
            
        
        
        
        try:
            summoner = cass.get_summoner(name=name, region=region)
            level = summoner.level
                
        except:
            return error("Invalid summoner name")
                
        try:
            dates = db.execute("SELECT date FROM matchlist WHERE username = ?", name)
            if len(dates) != 0:
                enddate = arrow.get(dates[-1]["date"])
                
                begindate = enddate.shift(days= -7)
                match_history = cass.get_match_history(continent=summoner.region.continent, puuid=summoner.puuid, queue=Queue.ranked_solo_fives, begin_time = begindate, end_time = enddate)
                
            else:
                try:
                    enddate = arrow.get(datetime.now())
                    #dayshift = datetime.now.day - 7
                    #if dayshift <= 0:
                    begindate = enddate.shift(days= -7)
                    #else:
                        #begindate = arrow.Arrow(datetime.now.year, datetime.now.month, datetime.now.day-dayshift, datetime.now.hour, datetime.now.minute, 0)
                    
                except:
                    return error("date error")
                
                match_history = cass.get_match_history(continent=summoner.region.continent, puuid=summoner.puuid, queue=Queue.ranked_solo_fives, begin_time = begindate, end_time = enddate)
        except:
            pass
        
        try:    
            role = []
            champs = {}
            champs_played= []
            
            cs = 0
            kda = 0
            vision = 0
            
            kdalist = []
            visionlist = []
            cslist = []
            
            cssupp = 0
            kdasupp = 0
            visionsupp = 0
            
            kdalistsupp = []
            visionlistsupp = []
            cslistsupp= []
            
            results = []
            position = ""
            ids = db.execute("SELECT id FROM matchlist")
            if len(ids) != 0:
                highestid = ids[-1]["id"]
        
                counter = highestid
            else:
                counter = 0
            
            try:
    
                champs = {champion.id: champion.name for champion in cass.get_champions(region=region)}   
            except:
                pass
            
            for match in match_history:
                try:
                    champion_id = match.participants[summoner].champion.id
                    champ_name = champs[champion_id]
                    champs_played.append(champ_name)
                except:
                    pass
                
                
                try:
                    length = match.duration
                    duration = length.total_seconds()/60
                except:
                    return error("get stats error")
                
                try:
                    gamerole = match.participants[summoner].individual_position
                    gamekda = round(match.participants[summoner].stats.kda, 2)
                    gamevision = match.participants[summoner].stats.vision_score
                    gamecs = round((match.participants[summoner].stats.total_minions_killed + match.participants[summoner].stats.neutral_minions_killed)/duration, 2)
                    gamewon = match.participants[summoner].stats.win
                    time = match.start
                    timeformatted = time.datetime
                except:
                    return error("map stats error")
                if gamewon == True:
                    result = "Win"
                else:
                    result = "Loss"
                    
                results.append(result)
                
                role.append(gamerole)
                
                try:
                    if gamerole == Lane.utility:
                        kdalistsupp.append(gamekda)
                        visionlistsupp.append(gamevision)
                        cslistsupp.append(gamecs)
                    
                        kdasupp += gamekda
                        visionsupp += gamevision
                        cssupp += gamecs
                    
                        position = "Support"
                    
                    else:
                        kdalist.append(gamekda)
                        visionlist.append(gamevision)
                        cslist.append(gamecs)
                    
                        kda += gamekda
                        vision += gamevision
                        cs += gamecs
                        
                    if gamerole == Lane.bot_lane:
                        position = "Bottom"
                    elif gamerole == Lane.top_lane:
                        position = "Top"
                    elif gamerole == Lane.jungle:
                        position = "Jungle"
                    elif gamerole == Lane.mid_lane:
                        position = "Mid"
                except:
                    pass
                
                try:
                    doesexist = db.execute("SELECT * FROM matchlist WHERE kda = ? AND vision = ? AND cs = ? AND result = ? AND champion = ? AND username = ? AND role = ? AND date = ?", gamekda, gamevision, gamecs, result, champ_name, name, position, timeformatted)
                    if len(doesexist) == 0:
                        counter += 1
                        db.execute("INSERT INTO matchlist(id, kda, vision, cs, result, champion, username, role, date) VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?)", counter, gamekda, gamevision, gamecs, result, champ_name, name, position, timeformatted)
                    else:
                        pass
                except:
                    pass
                
            champ_counter = Counter(champs_played)
            champs_played_unique = []
            for champ in champs_played:
                if champ not in champs_played_unique:
                    champs_played_unique.append(champ)
            role_counter = Counter(role)
            result_counter = Counter(results)
            
            wongames = result_counter["Win"]
            lostgames = result_counter["Loss"]
            totalgames = wongames + lostgames
            winrate = round(float(wongames/totalgames), 2) * 100
                
            kda = round(kda/len(kdalist), 2)
            vision = round(vision/len(visionlist), 2)
            cs = round(cs/len(cslist), 2)
            
            
            if role_counter[Lane.utility] > 0:
                kdasupp = round(kdasupp/len(kdalistsupp), 2)
                visionsupp = round(visionsupp/len(visionlistsupp), 2)
                cssupp = round(cssupp/len(cslistsupp), 2)
            else:
                pass
            
        except:
            pass
        
        
        
        supp = 0
        other = 0
        gamecount = 0
        #for match in match_history:
                
                
                #champion_id = match.participants[summoner].champion.id
                #champ_name = champs[champion_id]
                #gamerole = match.participants[summoner].individual_position
                #stats = match.participants[name].stats
                #if gamerole == Lane.utility:
                    #gamekda = kdalistsupp[supp]
                    #gamevision = visionlistsupp[supp]
                    #gamecs = cslistsupp[supp]
                    
                    #supp += 1
                    #position = "Support"
                    
                #else:
                    #gamevision = visionlist[other]
                    #gamecs = cslist[other]
                    #gamekda = kdalist[other]
                    
                    #other += 1
                
                
                #time = match.start
                #timeformatted = time.datetime
                #gamewon = stats.win
                #if gamewon == True:
                    #result = "Win"
                #else:
                    #result = "Loss"
                
                #if gamerole == Lane.bot_lane:
                    #position = "Bottom"
                #elif gamerole == Lane.top_lane:
                    #position = "Top"
                #elif gamerole == Lane.jungle:
                    #position = "Jungle"
                #elif gamerole == Lane.mid_lane:
                    #position = "Mid"
                
                
                #NEED TO CHANGE TABLE TO ACCEPT FLOATS
                #doesexist = db.execute("SELECT * FROM matchlist WHERE kda = ? AND vision = ? AND cs = ? AND result = ? AND champion = ? AND username = ? AND role = ? AND date = ?", gamekda, gamevision, gamecs, result, champ_name, name, position, timeformatted)
                
                #if len(doesexist) == 0:
                    
                    #counter+=1
                    #print(counter)
                    #idtaken = db.execute("SELECT * FROM matchlist WHERE id = ?", counter)
                    #if len(idtaken) == 0:
                    #gamecount +=1
                    #db.execute("INSERT INTO matchlist(kda, vision, cs, result, champion, username, role, date) VALUES(?, ?, ?, ?, ?, ?, ?, ?)", gamekda, gamevision, gamecs, result, champ_name, name, position, timeformatted)
                    #else:
                    #    while True:
                    #        if len(idtaken) == 0:
                    #            break
                    #        idtaken = db.execute("SELECT * FROM matchlist WHERE id = ?", counter)
                    #        counter += 1
                #else:
                    #pass
                        
        try:
            
            
            print(champ_counter)
            print(champs_played)
            print(role)
            print(role_counter)
            
            
            print(kda)
            print(vision)
            print(cs)
            print(kdasupp)
            print(visionsupp)
            print(cssupp)
            
            
            print(kdalistsupp)
            print(visionlistsupp)
            print(cslistsupp)
            print(kdalist)
            print(visionlist)
            print(cslist)
            
            duration = round(length.total_seconds()/60, 2)
            print(duration)
            print(gamekda)
            print(gamevision)
            print(gamecs)
            print(winrate)
            
            print(highestid)
            print(timeformatted)
            print(position)
            print(enddate)
            print(begindate)
            print(len(dates))
            
        except:
            pass
        
        ids = db.execute("SELECT id FROM matchlist")
        if len(ids) != 0:
            highestid = ids[-1]["id"]
        
        else:
            highestid = 0
        
        champ_dict = {}
        for champ, games in champ_counter.items():
            champ_dict[champ] = games
            
        print(champ_dict)
        return render_template("summoner.html", name = name, region = region, level = level, matches = counter, winrate = winrate, champ_counter = champ_dict, champs_played_unique=champs_played_unique)
        
@app.route("/query", methods=["GET", "POST"])
def query():
    if request.method == "GET":
        return redirect("/")
    else:
        try:
            category = request.form.get("category")
            comparer = request.form.get("comparer")
            statvalue = request.form.get("statvalue")
        except:
            
            return error("Some field not given")
        
        try:
            if category == "kda" or category == "cs" or category == "vision":
                statvalue = float(statvalue)
            else:
                statvalue = str(statvalue)
        except:
            return error("invalid type")
        try:
            if comparer == ">":
                if category == "kda":
                    matches = db.execute("SELECT * FROM matchlist WHERE kda > ?", statvalue)
                elif category == "vision":
                    matches = db.execute("SELECT * FROM matchlist WHERE vision > ?", statvalue)
                elif category == "cs":
                    matches = db.execute("SELECT * FROM matchlist WHERE cs > ?", statvalue)
                    
            elif comparer == "=":
                if category == "kda":
                    matches = db.execute("SELECT * FROM matchlist WHERE kda = ?", statvalue)
                elif category == "vision":
                    matches = db.execute("SELECT * FROM matchlist WHERE vision = ?", statvalue)
                elif category == "cs":
                    matches = db.execute("SELECT * FROM matchlist WHERE cs = ?", statvalue)
                elif category == "result":
                    matches = db.execute("SELECT * FROM matchlist WHERE result = ?", statvalue)
                elif category == "champion":
                    matches = db.execute("SELECT * FROM matchlist WHERE champion = ?", statvalue)
                elif category == "username":
                    matches = db.execute("SELECT * FROM matchlist WHERE username = ?", statvalue)
                elif category == "role":
                    matches = db.execute("SELECT * FROM matchlist WHERE role = ?", statvalue)
                    
            elif comparer == "<":
                if category == "kda":
                    matches = db.execute("SELECT * FROM matchlist WHERE kda < ?", statvalue)
                elif category == "vision":
                    matches = db.execute("SELECT * FROM matchlist WHERE vision < ?", statvalue)
                elif category == "cs":
                    matches = db.execute("SELECT * FROM matchlist WHERE cs < ?", statvalue)
            else:
                return error("Invalid comparer")
        except:
            return error("Invalid fields given")
        print(matches)
        print(comparer)
        print(category)
        print(statvalue)
        return render_template("queried.html", matches = matches)
    
def errorhandler(e):
    """Handle error"""
    if not isinstance(e, HTTPException):
        e = InternalServerError()
    return error(e.name, e.code)


# Listen for errors
for code in default_exceptions:
    app.errorhandler(code)(errorhandler)