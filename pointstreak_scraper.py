# import libraries
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import numpy as np
import pandas as pd
from bs4 import BeautifulSoup
import re
import os

# ----------
# BEFORE RUNNING

# PASTE THE GAME ID IN THE POINTSTREAK URL IN QUOTATION MARKS

POINTSTREAK_GAMEID = "613983"

# PASTE THE POINSTREAK URL IN QUOTATION MARKS
# gl_url = "http://ibl_baseball2.wttbaseball.pointstreak.com/gamelive/?gameid=599064"
# gl_url = "http://ibl_baseball2.wttbaseball.pointstreak.com/gamelive/?gameid=599038"
gl_url = "http://ibl_baseball2.wttbaseball.pointstreak.com/gamelive/?gameid=" + POINTSTREAK_GAMEID


# ENTER THE FOLLOWING VALUES
# ENTER THE DATE IN THE FORM YYYY-MM-DD 
# YYYY is the year
# MM is the month
# DD is the date
# GAME_DATE = '2023-08-18'
GAME_DATE = '2024-05-18'
# ENTER THE GAME TYPE
# E is exhibition
# C is championship
# Q is quarterfinal
# R is regular season
# S is semifinal
GAME_TYPE = 'R'
# TEAM ABBREVIATIONS:
# BAR is Barrie
# BRA is Brantford
# CHA is Chatham-Kent
# GUE is Guelph
# HAM is Hamilton
# KIT is Kitchener
# LON is London
# TOR is Toronto
# WEL is Welland
# ENTER THE AWAY TEAM ABBREVIATION
# AWAY_TEAM = 'BAR'
AWAY_TEAM = 'BAR'
# ENTER THE HOME TEAM ABBREVIATION
# HOME_TEAM = 'LON'
HOME_TEAM = 'WEL'
# ENTER THE AWAY STARTING PITCHER IN FORM FIRSTNAME LASTNAME
# AWAY_STARTING_PITCHER = 'Juan Benitez'
AWAY_STARTING_PITCHER = 'Carlos Sano'
# ENTER THE HOME STARTING PITCHER IN FORM FIRSTNAME LASTNAME
# HOME_STARTING_PITCHER = 'Alex Springer'
HOME_STARTING_PITCHER = 'Ben Abram'
# ENTER THE DOUBLEHEADER IDENTIFIER
# 1 if the game is not the second game of a doubleheader
# 2 if the game is the second game of a doubleheader
DH_IDENTIFIER = 1
# ENTER THE AWAY STARTING FIELDERS AT THEIR POSITION IN FORM FIRSTNAME LASTNAME
# AWAY_STARTING_FIELDERS = {'C': 'Hayden Jaco',
#                           '1B': 'Domenico Morea',
#                           '2B': 'Royce Ando',
#                           '3B': 'Adam Odd',
#                           'SS': 'Carson Burns',
#                           'LF': 'Starlin Rodriguez',
#                           'CF': 'Canice Ejoh',
#                           'RF': 'Avery Tuck'}
AWAY_STARTING_FIELDERS = {'C': 'Hayden Jaco',
                          '1B': 'Nolan Machibroda',
                          '2B': 'Adam Odd',
                          '3B': 'Malik Williams',
                          'SS': 'Carson Burns',
                          'LF': 'Brad McQuinn',
                          'CF': 'Canice Ejoh',
                          'RF': 'Rick Phillips'}
# ENTER THE HOME STARTING FIELDERS AT THEIR POSITION IN FORM FIRSTNAME LASTNAME
# HOME_STARTING_FIELDERS = {'C': 'Brad Verhoeven',
#                           '1B': 'Kayne McGee',
#                           '2B': 'Brett Graham',
#                           '3B': 'Daniel Battel',
#                           'SS': 'Tommy Reyes-Cruz',
#                           'LF': 'Starling Joseph',
#                           'CF': 'Andrew Lawrence',
#                           'RF': 'Byron Reichstein'}
HOME_STARTING_FIELDERS = {'C': 'Robert Mullen',
                          '1B': 'Steven Moretto',
                          '2B': 'Dawson Tweet',
                          '3B': 'Ethan Hunt',
                          'SS': 'Tyler Dupuis',
                          'LF': 'Brandon Hupe',
                          'CF': 'Gianfranco Morello',
                          'RF': 'Matteo Porcellato'}
# ----------

# scrape the data

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))

# load the web page
driver.get(gl_url)
# set maximum time to load the web page in seconds
driver.implicitly_wait(10)

contents = driver.find_element("xpath", "/html/body/div[1]/div/div[1]/div[9]/div[8]/div[1]/div[2]/table").get_attribute('outerHTML')
soup = BeautifulSoup(contents, "html.parser")
entries = soup.find_all(class_="top-align")

space_string = " "
formatted_entries = []
for pa in entries:
    formatted_entry = pa.text
    formatted_entry = re.sub("[\s]{2,}", " ", formatted_entry)
    formatted_entry = re.sub("\n", "", formatted_entry)
    formatted_entries.append(formatted_entry)
gt = ""
for pa in formatted_entries:
    gt = gt + pa
    gt = gt + "\n"

# f = open("scraper_example_18-08-23.txt", "w")
# f.write(output_text)
# f.close()

# format the data

def convert_google_sheet_url(url):
    # regular expression to match and capture the necessary part of the URL
    pattern = r'https://docs\.google\.com/spreadsheets/d/([a-zA-Z0-9-_]+)(/edit#gid=(\d+)|/edit.*)?'

    # replace function to construct the new URL for CSV export
    # if gid is present in the URL, it includes it in the export URL, otherwise, it's omitted
    replacement = lambda m: f'https://docs.google.com/spreadsheets/d/{m.group(1)}/export?' + (f'gid={m.group(3)}&' if m.group(3) else '') + 'format=csv'

    # replace using regex
    new_url = re.sub(pattern, replacement, url)

    return new_url

def get_full_name(abbrev):
    return players_df[players_df['gl_id'] == abbrev]['player'].values[0]

def get_pitcher_throws(pitcher):
    return players_df[players_df['player'] == pitcher]['throws'].values[0]

def get_batter_stand(batter):
    return players_df[players_df['player'] == batter]['bats'].values[0]

# define a function to concatenate the columns
def get_gl_id(player):
   return '#' + str(int(player['number'])) + ' ' + player['abbreviation']

players_url = 'https://docs.google.com/spreadsheets/d/1F8GBPtLhugdO0pqrJe3O9fMPOYv3AqVRq8ouUZWZxIY/edit#gid=897408437'

new_players_url = convert_google_sheet_url(players_url)

players_df = pd.read_csv(new_players_url)

players_df = players_df.fillna(0)

players_df['gl_id'] = ''

# Apply the function to each row of the DataFrame
players_df['gl_id'] = players_df.apply(get_gl_id, axis=1)

# f = open("scraper_example_18-08-23.txt", "r")
# gt = f.read()
# f.close()

# append description with ! prefix and suffix
gt = re.sub("Called Strike", "CalledStrike", gt)
gt = re.sub("Swinging Strike", "SwingingStrike", gt)
gt = re.sub("Ball", "!Ball!", gt)
gt = re.sub("CalledStrike", "!CalledStrike!", gt)
gt = re.sub("Foul", "!Foul!", gt)
gt = re.sub("SwingingStrike", "!SwingingStrike!", gt)

# split by \n to get each plate appearance
gt = re.split("\n", gt)

# remove whitespace
# create list of plate appearances with no whitespace
nw_gt = []
# iterate over plate appearances
for pa in gt:
    # remove whitespace
    nw_pa = re.sub("\s\Z", "", pa)
    # add reformatted plate appearance to list
    nw_gt.append(nw_pa)

# create list of lists split by each pitch
pbp_gt = []
# iterate over plate appearances
for nw_pa in nw_gt:
    # split by !
    pbp_pa = re.split("!", nw_pa)
    # add list of split plate appearances to list of lists
    pbp_gt.append(pbp_pa)

# remove last [''] in list
pbp_gt = pbp_gt[0:(len(pbp_gt) - 1)]

# iterate over plate appearances
for pbp_pa in pbp_gt:
    # iterate over each pitch
    for pitch in pbp_pa:
        # remove commas seperating pitches
        if pitch == ", ":
            pbp_pa.remove(pitch)
    # remove whitespace after hitter's name
    # if the first pitch (the batter) ends in a whitespace
    if (pbp_pa[0][(len(pbp_pa[0]) - 1)] == " "):
        # substring to not include the last character
        pbp_pa[0] = pbp_pa[0][0:(len(pbp_pa[0]) - 1)]
    # remove comma before plate appearance result
    # if the first character of the last pitch (the result) is a comma
    if (pbp_pa[len(pbp_pa) - 1][0] == ','):
        # substring to remove the first two characters
        pbp_pa[len(pbp_pa) - 1] = pbp_pa[len(pbp_pa) - 1][2:len(pbp_pa[len(pbp_pa) - 1])]

# split one pitch plate appearances
# split plate appearances with more than two whitespaces
for pbp_pa in pbp_gt:
    # counter for the white spaces in the first entry
    count_spaces = 0
    # iterate over first entry
    for i in range(len(pbp_pa[0])):
        # if a whitespace
        if (pbp_pa[0][i] == " "):
            # add one to counter
            count_spaces += 1
            # once five has been reached
            if (count_spaces == 5):
                if (pbp_pa[0][0:i] in list(players_df[['gl_id']].values)):    
                    # add a second element to the list starting after the fifth whitespace
                    pbp_pa.insert(1, pbp_pa[0][(i + 1):len(pbp_pa[0])])
                    # subset the first element to be only up to the fifth whitespace
                    pbp_pa[0] = pbp_pa[0][0:i]
                    # terminate the loop
                    break
            # once four has been reached
            if (count_spaces == 4):
                if (pbp_pa[0][0:i] in list(players_df[['gl_id']].values)):
                    # add a second element to the list starting after the fourth whitespace
                    pbp_pa.insert(1, pbp_pa[0][(i + 1):len(pbp_pa[0])])
                    # subset the first element to be only up to the fourth whitespace
                    pbp_pa[0] = pbp_pa[0][0:i]
                    # terminate the loop
                    break
            # once three has been reached
            if (count_spaces == 3):
                if (pbp_pa[0][0:i] in list(players_df[['gl_id']].values)):
                    # add a second element to the list starting after the third whitespace
                    pbp_pa.insert(1, pbp_pa[0][(i + 1):len(pbp_pa[0])])
                    # subset the first element to be only up to the third whitespace
                    pbp_pa[0] = pbp_pa[0][0:i]
                    # terminate the loop
                    break
                if ((re.search("Pitching Substitution|Offensive Substitution|Defensive Substitution", pbp_pa[0]) != None)):
                    # add a second element to the list starting after the third whitespace
                    pbp_pa.insert(1, pbp_pa[0][(i + 1):len(pbp_pa[0])])
                    # subset the first element to be only up to the third whitespace
                    pbp_pa[0] = pbp_pa[0][0:i]
                    # terminate the loop
                    break

# replace Game Live id in form #XX F. LastName with FirstName LastName
# iterate over plate appearances
for pbp_pa in pbp_gt:
    # if the first character of the first entry is #
    if (pbp_pa[0][0] == "#"):
        # search players database and replace with full name
        pbp_pa[0] = get_full_name(pbp_pa[0])

# create list of lists to hold reformatted data
pbp_gt_nn = []

# iterate over plate appearances
for pbp_pa in pbp_gt:
    # create list to hold reformatted plate appearances
    pbp_pa_nn = []
    # iterate over entries in plate appearance
    for pitch in pbp_pa:
        # remove any numbers and their trailing whitespace at the start of strings
        pitch = re.sub(r"\A[0-9][0-9]\s|\A[0-9]\s", "", pitch)
        # remove any numbers and their trailing whitespace after a comma and a whitespace
        pitch = re.sub(r"(?<=,\s)[0-9][0-9]\s|(?<=,\s)[0-9]\s", "", pitch)
        # remove any batter numbers who advanced runners
        # this will not remove any numbers of unassisted putouts
        pitch = re.sub(r"(?<!putout)\s\([0-9][0-9]\)|(?<!putout)\s\([0-9]\)", "", pitch)
        # remove numbers after substitution
        pitch = re.sub(r"(?<=Substitution)\s[0-9][0-9]|(?<=Substitution\s[0-9])", "", pitch)
        pbp_pa_nn.append(pitch)
    pbp_gt_nn.append(pbp_pa_nn)

GAME_YEAR = int(GAME_DATE[0:4])
GAME_PK = GAME_DATE[0:4] + GAME_DATE[5:7] + GAME_DATE[8:len(GAME_DATE)] + AWAY_TEAM + HOME_TEAM + str(DH_IDENTIFIER)


output_txt_file_string = os.path.join(os.path.abspath(os.getcwd()), 'baycats/raw_game_txt_files/gametext_' + GAME_PK + '.txt')
f = open(output_txt_file_string, 'w')
for pbp_pa in pbp_gt_nn:
    for pitch in pbp_pa:
        f.write(pitch)
        f.write("\n")
    f.write("\n")
f.close()

# game level
lineup_positions = ['C', '1B', '2B', '3B', 'SS', 'LF', 'CF', 'RF']
home_pitcher = HOME_STARTING_PITCHER
home_fielders = ['Placeholder0', 'Placeholder1']
for position in lineup_positions:
    home_fielders.append(HOME_STARTING_FIELDERS[position])

away_pitcher = AWAY_STARTING_PITCHER
away_fielders = ['Placeholder0', 'Placeholder1']
for position in lineup_positions:
    away_fielders.append(AWAY_STARTING_FIELDERS[position])

home_pitcher_throws = get_pitcher_throws(home_pitcher)
away_pitcher_throws = get_pitcher_throws(away_pitcher)
if ((home_pitcher_throws == 'S') | (away_pitcher_throws == 'S')):
    if ((home_pitcher_throws == 'S') & (away_pitcher_throws == 'S')):
        home_pitcher_switch_pitcher = True
        away_pitcher_switch_pitcher = True
    elif (home_pitcher_throws == 'S'):
        home_pitcher_switch_pitcher = True
        away_pitcher_switch_pitcher = False
    elif (away_pitcher_throws == 'S'):
        home_pitcher_switch_pitcher = False
        away_pitcher_switch_pitcher = True
else:
    home_pitcher_switch_pitcher = False
    away_pitcher_switch_pitcher = False

game_dict = {'game_date': [], 
           'batter': [], 
           'pitcher': [], 
           'events': [], 
           'description': [], 
           'des': [], 
           'stand': [], 
           'p_throws': [], 
           'game_type': [], 
           'home_team': [], 
           'away_team': [], 
           'type': [], 
           'balls': [], 
           'strikes': [], 
           'game_year': [], 
           'on_3b': [], 
           'on_2b': [],  
           'on_1b': [], 
           'outs_when_up': [], 
           'inning': [], 
           'inning_topbot': [], 
           'sv_id': [], 
           'game_pk': [],
           'fielder_2': [],
           'fielder_3': [],
           'fielder_4': [], 
           'fielder_5': [], 
           'fielder_6': [], 
           'fielder_7': [], 
           'fielder_8': [], 
           'fielder_9': [], 
           'at_bat_number': [], 
           'pitch_number': [], 
           'home_score': [], 
           'away_score': [], 
           'bat_score': [], 
           'fld_score': [], 
           'post_away_score': [], 
           'post_home_score': [], 
           'post_bat_score': [], 
           'post_fld_score': [],
           'baserunner_event': []}
game_df = pd.DataFrame(data=game_dict)

# game level
inning_tr = 1
inning_topbot_tr = 'Top'

at_bat_number_tr = 1
home_score_tr = 0
away_score_tr = 0

batter_stand_dict = {}

# inning level
on_3b_tr = None
on_2b_tr = None
on_1b_tr = None
outs_tr = 0

# pbp_pa = pbp_gt_nn[0]

# pa level
for pa in range(len(pbp_gt_nn)):
    pbp_pa = pbp_gt_nn[pa]
    
    balls_tr = 0
    strikes_tr = 0

    game_date_l = []
    batter_l = []
    pitcher_l = []
    events_l = []
    description_l = []
    des_l = []
    stand_l = []
    p_throws_l = []
    game_type_l = []
    home_team_l = []
    away_team_l = []
    type_l = []
    balls_l = []
    strikes_l = []
    game_year_l = []
    on_3b_l = []
    on_2b_l = []
    on_1b_l = []
    outs_when_up_l = []
    inning_l = []
    inning_topbot_l = []
    sv_id_l = []
    game_pk_l = []
    fielder_2_l = []
    fielder_3_l = []
    fielder_4_l = []
    fielder_5_l = []
    fielder_6_l = []
    fielder_7_l = []
    fielder_8_l = []
    fielder_9_l = []
    at_bat_number_l = []
    pitch_number_l = []
    home_score_l = []
    away_score_l = []
    bat_score_l = []
    fld_score_l = []
    post_away_score_l = []
    post_home_score_l = []
    post_bat_score_l = []
    post_fld_score_l = []
    baserunner_event_l = []

    # if is a plate appearance
    # check if first entry is a batter name
    if (pbp_pa[0] in players_df['player'].to_list()):
        batter = pbp_pa[0]
        
        # check if batter has already had a plate appearance in the game
        if (batter in list(batter_stand_dict.keys())):
            # get their stored handedness
            batter_stand = batter_stand_dict[batter]
            # if the batter a switch hitter
            if (batter_stand == 'S'):
                if (inning_topbot_tr == 'Top'):
                    if (home_pitcher_throws == 'L'):
                        batter_stand = 'R'
                    elif (home_pitcher_throws == 'R'): 
                        batter_stand = 'L'
                    # if the pitcher a switch pitcher
                    # assume the pitcher will throw right
                    elif (home_pitcher_throws == 'S'):
                        batter_stand = 'L'
                    # if an error set to U
                    else: batter_stand = 'U'
                else:
                    if (away_pitcher_throws == 'L'):
                        batter_stand = 'R'
                    elif (away_pitcher_throws == 'R'): 
                        batter_stand = 'L'
                    # if the pitcher a switch pitcher
                    # assume the pitcher will throw right
                    elif (away_pitcher_throws == 'S'):
                        batter_stand = 'L'
                    # if an error set to U
                    else: batter_stand = 'U'
        # else read their handedness from the database and store it
        else:
            batter_stand = get_batter_stand(batter)
            batter_stand_dict[batter] = batter_stand
            # if the batter a switch hitter
            if (batter_stand == 'S'):
                if (inning_topbot_tr == 'Top'):
                    if (home_pitcher_throws == 'L'):
                        batter_stand = 'R'
                    elif (home_pitcher_throws == 'R'): 
                        batter_stand = 'L'
                    # if the pitcher a switch pitcher
                    # assume the pitcher will throw right
                    elif (home_pitcher_throws == 'S'):
                        batter_stand = 'L'
                    # if an error set to U
                    else: batter_stand = 'U'
                else:
                    if (away_pitcher_throws == 'L'):
                        batter_stand = 'R'
                    elif (away_pitcher_throws == 'R'): 
                        batter_stand = 'L'
                    # if the pitcher a switch pitcher
                    # assume the pitcher will throw right
                    elif (away_pitcher_throws == 'S'):
                        batter_stand = 'L'
                    # if an error set to U
                    else: batter_stand = 'U'
        
        if ((inning_topbot_tr == 'Top') & (home_pitcher_switch_pitcher == True)):
            if (batter_stand_dict[batter] == 'L'):
                home_pitcher_throws_temp = 'L'
            elif (batter_stand_dict[batter] == 'R'):
                home_pitcher_throws_temp = 'R'
            # if the batter a switch hitter
            # assume the pitcher will throw right
            elif (batter_stand_dict[batter] == 'S'):
                home_pitcher_throws_temp = 'R'
            # if an error set to U
            else: home_pitcher_throws_temp = 'U'
        else: home_pitcher_throws_temp = home_pitcher_throws
        if ((inning_topbot_tr == 'Bot') & (away_pitcher_switch_pitcher == False)):
            if (batter_stand_dict[batter] == 'L'):
                away_pitcher_throws_temp = 'L'
            elif (batter_stand_dict[batter] == 'R'):
                away_pitcher_throws_temp = 'R'
            # if the batter a switch hitter
            # assume the pitcher will throw right
            elif (batter_stand_dict[batter] == 'S'):
                away_pitcher_throws_temp = 'R'
            # if an error set to U
            else: away_pitcher_throws_temp = 'U'
        else: away_pitcher_throws_temp = away_pitcher_throws
            
        # count runs scored in plate appearance
        pa_runs = 0
        for pitch in pbp_pa:
            pa_runs += pitch.count('Scores Earned')
            pa_runs += pitch.count('Scores Unearned')

        baserunner_event_tr = 0
        # check for baserunner event
        for pitch in pbp_pa:
            if (re.search(r"stolen base|wild pitch|caught stealing|passed ball|pass ball|Pickoff attempt", pitch)):
                baserunner_event_tr = 1

        if (len(pbp_pa) > 2):
            for i in range(1, (len(pbp_pa)-1)):
                if (re.search(r"stolen base|wild pitch|caught stealing|passed ball|pass ball|Pickoff attempt", pbp_pa[i])):
                    # if baserunner events in the form ", EVENT, "
                    if (pbp_pa[i][0:2] == ', '):
                        # append baserunner event starting from after first comma
                        pbp_pa[len(pbp_pa) - 1] = pbp_pa[i][2:len(pbp_pa[i])] + pbp_pa[len(pbp_pa) - 1]
                        continue
                    else:
                        # append baserunner event
                        pbp_pa[len(pbp_pa) - 1] = pbp_pa[i][0:len(pbp_pa[i])] + pbp_pa[len(pbp_pa) - 1]
                        continue

                game_date_l.append(GAME_DATE)
                batter_l.append(batter)
                if (inning_topbot_tr == 'Top'):
                    pitcher_l.append(home_pitcher)
                else: pitcher_l.append(away_pitcher)
                events_l.append(None)
                if (pbp_pa[i] == 'Ball'):
                    description_l.append('ball')
                elif (pbp_pa[i] == 'CalledStrike'):
                    description_l.append('called_strike')
                elif (pbp_pa[i] == 'Foul'):
                    description_l.append('foul')
                elif (pbp_pa[i] == 'SwingingStrike'):
                    description_l.append('swinging_strike')
                else: description_l.append(None)
                des_l.append(pbp_pa[len(pbp_pa) - 1])
                stand_l.append(batter_stand)
                if (inning_topbot_tr == 'Top'):
                    if (home_pitcher_switch_pitcher == False):
                        p_throws_l.append(home_pitcher_throws)
                    else: p_throws_l.append(home_pitcher_throws_temp)
                elif (inning_topbot_tr == 'Bot'):
                    if (away_pitcher_switch_pitcher == False):
                        p_throws_l.append(away_pitcher_throws)
                    else: p_throws_l.append(away_pitcher_throws_temp)
                else: p_throws_l.append('U')
                game_type_l.append(GAME_TYPE)
                home_team_l.append(HOME_TEAM)
                away_team_l.append(AWAY_TEAM)
                if (pbp_pa[i] == 'Ball'):
                    type_l.append('B')
                elif ((pbp_pa[i] == 'CalledStrike') | (pbp_pa[i] == 'Foul') | (pbp_pa[i] == 'SwingingStrike')):
                    type_l.append('S')
                else: type_l.append('U')
                balls_l.append(balls_tr)
                if (pbp_pa[i] == 'Ball'):
                    balls_tr += 1
                strikes_l.append(strikes_tr)
                if ((pbp_pa[i] == 'CalledStrike') | (pbp_pa[i] == 'SwingingStrike') | ((pbp_pa[i] == 'Foul') & (strikes_tr < 2))):
                    strikes_tr += 1
                game_year_l.append(GAME_YEAR)
                on_3b_l.append(on_3b_tr)
                on_2b_l.append(on_2b_tr)
                on_1b_l.append(on_1b_tr)
                outs_when_up_l.append(outs_tr)
                inning_l.append(inning_tr)
                inning_topbot_l.append(inning_topbot_tr)
                if (at_bat_number_tr < 10):
                    sv_id_l.append(GAME_PK + '-' + str(0) + str(at_bat_number_tr))
                else: sv_id_l.append(GAME_PK + '-' + str(at_bat_number_tr))
                game_pk_l.append(GAME_PK)
                if (inning_topbot_tr == 'Top'):
                    fielder_2_l.append(home_fielders[2])
                    fielder_3_l.append(home_fielders[3])
                    fielder_4_l.append(home_fielders[4])
                    fielder_5_l.append(home_fielders[5])
                    fielder_6_l.append(home_fielders[6])
                    fielder_7_l.append(home_fielders[7])
                    fielder_8_l.append(home_fielders[8])
                    fielder_9_l.append(home_fielders[9])
                else:
                    fielder_2_l.append(away_fielders[2])
                    fielder_3_l.append(away_fielders[3])
                    fielder_4_l.append(away_fielders[4])
                    fielder_5_l.append(away_fielders[5])
                    fielder_6_l.append(away_fielders[6])
                    fielder_7_l.append(away_fielders[7])
                    fielder_8_l.append(away_fielders[8])
                    fielder_9_l.append(away_fielders[9])
                at_bat_number_l.append(at_bat_number_tr)
                pitch_number_l.append(i)
                home_score_l.append(home_score_tr)
                away_score_l.append(away_score_tr)
                if (inning_topbot_tr == 'Top'):
                    bat_score_l.append(away_score_tr)
                    fld_score_l.append(home_score_tr)
                    post_away_score_l.append((away_score_tr + pa_runs))
                    post_home_score_l.append(home_score_tr)
                    post_bat_score_l.append((away_score_tr + pa_runs))
                    post_fld_score_l.append(home_score_tr)
                else: 
                    bat_score_l.append(home_score_tr)
                    fld_score_l.append(away_score_tr)
                    post_away_score_l.append(away_score_tr)
                    post_home_score_l.append((home_score_tr + pa_runs))
                    post_bat_score_l.append((home_score_tr + pa_runs))
                    post_fld_score_l.append(away_score_tr)
                baserunner_event_l.append(baserunner_event_tr)
                
            game_date_l.append(GAME_DATE)
            batter_l.append(batter)
            if (inning_topbot_tr == 'Top'):
                pitcher_l.append(home_pitcher)
            else: pitcher_l.append(away_pitcher)

            if (re.search("single", pbp_pa[len(pbp_pa) - 1]) != None):
                events_l.append('single')
            elif (re.search("double", pbp_pa[len(pbp_pa) - 1]) != None):
                events_l.append('double')
            elif (re.search("triple", pbp_pa[len(pbp_pa) - 1]) != None):
                events_l.append('triple')
            elif (re.search("home run", pbp_pa[len(pbp_pa) - 1]) != None):
                events_l.append('home_run')
            elif (re.search("walk", pbp_pa[len(pbp_pa) - 1]) != None):
                events_l.append('walk')
            elif (re.search("hit by pitch", pbp_pa[len(pbp_pa) - 1]) != None):
                events_l.append('hit_by_pitch')
            # search for strikeout
            elif ((re.search("strike out", pbp_pa[len(pbp_pa) - 1]) != None) | (re.search("dropped 3rd strike", pbp_pa[len(pbp_pa) - 1]) != None)):
                events_l.append('strikeout')
            # search for ground into double play
            # search for infielder position followed by hyphen and "DP"
            elif ((re.search(r"\([1-6]-", pbp_pa[len(pbp_pa) - 1]) != None) & (re.search("DP", pbp_pa[len(pbp_pa) - 1]) != None)):
                events_l.append('grounded_into_double_play')
            elif (re.search("DP", pbp_pa[len(pbp_pa) - 1]) != None):
                events_l.append('double_play')
            # search for reached on error
            elif (re.search(r"advances to 1st \(error", pbp_pa[len(pbp_pa) - 1]) != None):
                events_l.append('field_error')
            elif (re.search(r"fielder's choice", pbp_pa[len(pbp_pa) - 1]) != None):
                events_l.append('fielders_choice')
            # search for field out
            # use that GIDP is previously checked for
            elif (re.search("fly out", pbp_pa[len(pbp_pa) - 1]) != None):
                events_l.append('field_out')
            elif (re.search(r"\([1-6]-", pbp_pa[len(pbp_pa) - 1]) != None):
                events_l.append('field_out')
            elif (re.search(r"\([1-6]\)|\(P[1-6]\)", pbp_pa[len(pbp_pa) - 1]) != None):
                events_l.append('field_out')
            elif (re.search(r"sacrifice fly", pbp_pa[len(pbp_pa) - 1]) != None):
                events_l.append('sac_fly')
            else: events_l.append('unrecognized')

            if (re.search("intentional walk", pbp_pa[len(pbp_pa) - 1]) != None):
                description_l.append('intentional_walk')
            # use that intentional walk is previously checked for
            elif (events_l[len(events_l) - 1] == 'walk'):
                description_l.append('ball')
            elif (events_l[len(events_l) - 1] == 'hit_by_pitch'):
                description_l.append('hit_by_pitch')
            elif ((re.search("strike out swinging", pbp_pa[len(pbp_pa) - 1]) != None) | (re.search("dropped 3rd strike: KS", pbp_pa[len(pbp_pa) - 1]) != None)):
                description_l.append('swinging_strike')
            # use that strike out swinging is previously checked for
            elif ((re.search("strike out", pbp_pa[len(pbp_pa) - 1]) != None) | (re.search("dropped 3rd strike: KC", pbp_pa[len(pbp_pa) - 1]) != None)):
                description_l.append('called_strike')
            elif ((events_l[len(events_l) - 1] == 'single') | 
                  (events_l[len(events_l) - 1] == 'double') | 
                  (events_l[len(events_l) - 1] == 'triple') | 
                  (events_l[len(events_l) - 1] == 'home_run') | 
                  (events_l[len(events_l) - 1] == 'grounded_into_double_play') | 
                  (events_l[len(events_l) - 1] == 'double_play') | 
                  (events_l[len(events_l) - 1] == 'field_error') | 
                  (events_l[len(events_l) - 1] == 'fielders_choice') |
                  (events_l[len(events_l) - 1] == 'field_out') |
                  (events_l[len(events_l) - 1] == 'sac_fly')):
                description_l.append('hit_into_play')
            else: description_l.append('unrecognized')

            des_l.append(pbp_pa[len(pbp_pa) - 1])
            stand_l.append(batter_stand)
            if (inning_topbot_tr == 'Top'):
                if (home_pitcher_switch_pitcher == False):
                        p_throws_l.append(home_pitcher_throws)
                else: p_throws_l.append(home_pitcher_throws_temp)
            elif (inning_topbot_tr == 'Bot'):
                if (away_pitcher_switch_pitcher == False):
                        p_throws_l.append(away_pitcher_throws)
                else: p_throws_l.append(away_pitcher_throws_temp)
            else: p_throws_l.append('U')
            game_type_l.append(GAME_TYPE)
            home_team_l.append(HOME_TEAM)
            away_team_l.append(AWAY_TEAM)

            if (description_l[len(description_l) - 1] == 'intentional_walk'):
                type_l.append(None)
            elif ((description_l[len(description_l) - 1] == 'ball') | (description_l[len(description_l) - 1] == 'hit_by_pitch')):
                type_l.append('B')
            elif ((description_l[len(description_l) - 1] == 'called_strike') | (description_l[len(description_l) - 1] == 'swinging_strike')):
                type_l.append('S')
            elif ((description_l[len(description_l) - 1] == 'hit_into_play')):
                type_l.append('X')
            else: type_l.append('U')

            balls_l.append(balls_tr)
            strikes_l.append(strikes_tr)
            game_year_l.append(GAME_YEAR)
            on_3b_l.append(on_3b_tr)
            on_2b_l.append(on_2b_tr)
            on_1b_l.append(on_1b_tr)
            outs_when_up_l.append(outs_tr)
            inning_l.append(inning_tr)
            inning_topbot_l.append(inning_topbot_tr)
            if (at_bat_number_tr < 10):
                sv_id_l.append(GAME_PK + '-' + str(0) + str(at_bat_number_tr))
            else: sv_id_l.append(GAME_PK + '-' + str(at_bat_number_tr))
            game_pk_l.append(GAME_PK)
            if (inning_topbot_tr == 'Top'):
                fielder_2_l.append(home_fielders[2])
                fielder_3_l.append(home_fielders[3])
                fielder_4_l.append(home_fielders[4])
                fielder_5_l.append(home_fielders[5])
                fielder_6_l.append(home_fielders[6])
                fielder_7_l.append(home_fielders[7])
                fielder_8_l.append(home_fielders[8])
                fielder_9_l.append(home_fielders[9])
            else:
                fielder_2_l.append(away_fielders[2])
                fielder_3_l.append(away_fielders[3])
                fielder_4_l.append(away_fielders[4])
                fielder_5_l.append(away_fielders[5])
                fielder_6_l.append(away_fielders[6])
                fielder_7_l.append(away_fielders[7])
                fielder_8_l.append(away_fielders[8])
                fielder_9_l.append(away_fielders[9])
            at_bat_number_l.append(at_bat_number_tr)
            at_bat_number_tr += 1
            if (description_l[len(description_l) - 1] == 'intentional_walk'):
                pitch_number_l.append(np.nan)
            else: pitch_number_l.append(len(pbp_pa) - 1)
            home_score_l.append(home_score_tr)
            away_score_l.append(away_score_tr)
            if (inning_topbot_tr == 'Top'):
                bat_score_l.append(away_score_tr)
                fld_score_l.append(home_score_tr)
                post_away_score_l.append((away_score_tr + pa_runs))
                post_home_score_l.append(home_score_tr)
                post_bat_score_l.append((away_score_tr + pa_runs))
                post_fld_score_l.append(home_score_tr)
            else: 
                bat_score_l.append(home_score_tr)
                fld_score_l.append(away_score_tr)
                post_away_score_l.append(away_score_tr)
                post_home_score_l.append((home_score_tr + pa_runs))
                post_bat_score_l.append((home_score_tr + pa_runs))
                post_fld_score_l.append(away_score_tr)
            baserunner_event_l.append(baserunner_event_tr)

        else:
            game_date_l.append(GAME_DATE)
            batter_l.append(batter)
            if (inning_topbot_tr == 'Top'):
                pitcher_l.append(home_pitcher)
            else: pitcher_l.append(away_pitcher)

            if (re.search("single", pbp_pa[len(pbp_pa) - 1]) != None):
                events_l.append('single')
            elif (re.search("double", pbp_pa[len(pbp_pa) - 1]) != None):
                events_l.append('double')
            elif (re.search("triple", pbp_pa[len(pbp_pa) - 1]) != None):
                events_l.append('triple')
            elif (re.search("home run", pbp_pa[len(pbp_pa) - 1]) != None):
                events_l.append('home_run')
            elif (re.search("walk", pbp_pa[len(pbp_pa) - 1]) != None):
                events_l.append('walk')
            elif (re.search("hit by pitch", pbp_pa[len(pbp_pa) - 1]) != None):
                events_l.append('hit_by_pitch')
            # search for strikeout
            elif ((re.search("strike out", pbp_pa[len(pbp_pa) - 1]) != None) | (re.search("dropped 3rd strike", pbp_pa[len(pbp_pa) - 1]) != None)):
                events_l.append('strikeout')
            # search for ground into double play
            # search for infielder position followed by hyphen and "DP"
            elif ((re.search(r"\([1-6]-", pbp_pa[len(pbp_pa) - 1]) != None) & (re.search("DP", pbp_pa[len(pbp_pa) - 1]) != None)):
                events_l.append('grounded_into_double_play')
            elif (re.search("DP", pbp_pa[len(pbp_pa) - 1]) != None):
                events_l.append('double_play')
            # search for reached on error
            elif (re.search(r"advances to 1st \(error", pbp_pa[len(pbp_pa) - 1]) != None):
                events_l.append('field_error')
            elif (re.search(r"fielder's choice", pbp_pa[len(pbp_pa) - 1]) != None):
                events_l.append('fielders_choice')
            # search for field out
            # use that GIDP is previously checked for
            elif (re.search("fly out", pbp_pa[len(pbp_pa) - 1]) != None):
                events_l.append('field_out')
            elif (re.search(r"\([1-6]-", pbp_pa[len(pbp_pa) - 1]) != None):
                events_l.append('field_out')
            elif (re.search(r"\([1-6]\)|\(P[1-6]\)", pbp_pa[len(pbp_pa) - 1]) != None):
                events_l.append('field_out')
            elif (re.search(r"sacrifice fly", pbp_pa[len(pbp_pa) - 1]) != None):
                events_l.append('sac_fly')
            else: events_l.append('unrecognized')

            if (re.search("intentional walk", pbp_pa[len(pbp_pa) - 1]) != None):
                description_l.append('intentional_walk')
            # use that intentional walk is previously checked for
            elif (events_l[len(events_l) - 1] == 'walk'):
                description_l.append('ball')
            elif (events_l[len(events_l) - 1] == 'hit_by_pitch'):
                description_l.append('hit_by_pitch')
            elif ((re.search("strike out swinging", pbp_pa[len(pbp_pa) - 1]) != None) | (re.search("dropped 3rd strike: KS", pbp_pa[len(pbp_pa) - 1]) != None)):
                description_l.append('swinging_strike')
            # use that strike out swinging is previously checked for
            elif ((re.search("strike out", pbp_pa[len(pbp_pa) - 1]) != None) | (re.search("dropped 3rd strike: KC", pbp_pa[len(pbp_pa) - 1]) != None)):
                description_l.append('called_strike')
            elif ((events_l[len(events_l) - 1] == 'single') | 
                  (events_l[len(events_l) - 1] == 'double') | 
                  (events_l[len(events_l) - 1] == 'triple') | 
                  (events_l[len(events_l) - 1] == 'home_run') | 
                  (events_l[len(events_l) - 1] == 'grounded_into_double_play') | 
                  (events_l[len(events_l) - 1] == 'double_play') | 
                  (events_l[len(events_l) - 1] == 'field_error') | 
                  (events_l[len(events_l) - 1] == 'fielders_choice') |
                  (events_l[len(events_l) - 1] == 'field_out') |
                  (events_l[len(events_l) - 1] == 'sac_fly')):
                description_l.append('hit_into_play')
            else: description_l.append('unrecognized')

            des_l.append(pbp_pa[len(pbp_pa) - 1])
            stand_l.append(batter_stand)
            if (inning_topbot_tr == 'Top'):
                if (home_pitcher_switch_pitcher == False):
                        p_throws_l.append(home_pitcher_throws)
                else: p_throws_l.append(home_pitcher_throws_temp)
            elif (inning_topbot_tr == 'Bot'):
                if (away_pitcher_switch_pitcher == False):
                        p_throws_l.append(away_pitcher_throws)
                else: p_throws_l.append(away_pitcher_throws_temp)
            else: p_throws_l.append('U')
            game_type_l.append(GAME_TYPE)
            home_team_l.append(HOME_TEAM)
            away_team_l.append(AWAY_TEAM)

            if (description_l[len(description_l) - 1] == 'intentional_walk'):
                type_l.append(None)
            elif ((description_l[len(description_l) - 1] == 'ball') | (description_l[len(description_l) - 1] == 'hit_by_pitch')):
                type_l.append('B')
            elif ((description_l[len(description_l) - 1] == 'called_strike') | (description_l[len(description_l) - 1] == 'swinging_strike')):
                type_l.append('S')
            elif ((description_l[len(description_l) - 1] == 'hit_into_play')):
                type_l.append('X')
            else: type_l.append('U')

            balls_l.append(balls_tr)
            strikes_l.append(strikes_tr)
            game_year_l.append(GAME_YEAR)
            on_3b_l.append(on_3b_tr)
            on_2b_l.append(on_2b_tr)
            on_1b_l.append(on_1b_tr)
            outs_when_up_l.append(outs_tr)
            inning_l.append(inning_tr)
            inning_topbot_l.append(inning_topbot_tr)
            if (at_bat_number_tr < 10):
                sv_id_l.append(GAME_PK + '-' + str(0) + str(at_bat_number_tr))
            else: sv_id_l.append(GAME_PK + '-' + str(at_bat_number_tr))
            game_pk_l.append(GAME_PK)
            if (inning_topbot_tr == 'Top'):
                fielder_2_l.append(home_fielders[2])
                fielder_3_l.append(home_fielders[3])
                fielder_4_l.append(home_fielders[4])
                fielder_5_l.append(home_fielders[5])
                fielder_6_l.append(home_fielders[6])
                fielder_7_l.append(home_fielders[7])
                fielder_8_l.append(home_fielders[8])
                fielder_9_l.append(home_fielders[9])
            else:
                fielder_2_l.append(away_fielders[2])
                fielder_3_l.append(away_fielders[3])
                fielder_4_l.append(away_fielders[4])
                fielder_5_l.append(away_fielders[5])
                fielder_6_l.append(away_fielders[6])
                fielder_7_l.append(away_fielders[7])
                fielder_8_l.append(away_fielders[8])
                fielder_9_l.append(away_fielders[9])
            at_bat_number_l.append(at_bat_number_tr)
            at_bat_number_tr += 1
            if (description_l[len(description_l) - 1] == 'intentional_walk'):
                pitch_number_l.append(np.nan)
            else: pitch_number_l.append(1)
            home_score_l.append(home_score_tr)
            away_score_l.append(away_score_tr)
            if (inning_topbot_tr == 'Top'):
                bat_score_l.append(away_score_tr)
                fld_score_l.append(home_score_tr)
                post_away_score_l.append((away_score_tr + pa_runs))
                post_home_score_l.append(home_score_tr)
                post_bat_score_l.append((away_score_tr + pa_runs))
                post_fld_score_l.append(home_score_tr)
            else: 
                bat_score_l.append(home_score_tr)
                fld_score_l.append(away_score_tr)
                post_away_score_l.append(away_score_tr)
                post_home_score_l.append((home_score_tr + pa_runs))
                post_bat_score_l.append((home_score_tr + pa_runs))
                post_fld_score_l.append(away_score_tr)
            baserunner_event_l.append(baserunner_event_tr)

        if (inning_topbot_tr == 'Top'):
            away_score_tr = away_score_tr + pa_runs
        else: home_score_tr = home_score_tr + pa_runs
    
        if ((re.search(f"{on_3b_tr} Scores Earned", pbp_pa[len(pbp_pa) - 1]) != None)|(re.search(f"{on_3b_tr} Scores Unearned", pbp_pa[len(pbp_pa) - 1]) != None)):
            on_3b_tr = None
        elif (re.search(f"{on_3b_tr} putout", pbp_pa[len(pbp_pa) - 1]) != None):
            on_3b_tr = None
        if ((re.search(f"{on_2b_tr} Scores Earned", pbp_pa[len(pbp_pa) - 1]) != None)|(re.search(f"{on_2b_tr} Scores Unearned", pbp_pa[len(pbp_pa) - 1]) != None)):
            on_2b_tr = None
        elif (re.search(f"{on_2b_tr} advances to 3rd", pbp_pa[len(pbp_pa) - 1]) != None):
            on_3b_tr = on_2b_tr
            on_2b_tr = None
        elif (re.search(f"{on_2b_tr} putout", pbp_pa[len(pbp_pa) - 1]) != None):
            on_2b_tr = None
        if ((re.search(f"{on_1b_tr} Scores Earned", pbp_pa[len(pbp_pa) - 1]) != None)|(re.search(f"{on_1b_tr} Scores Unearned", pbp_pa[len(pbp_pa) - 1]) != None)):
            on_1b_tr = None
        elif (re.search(f"{on_1b_tr} advances to 3rd", pbp_pa[len(pbp_pa) - 1]) != None):
            on_3b_tr = on_1b_tr
            on_1b_tr = None
        elif (re.search(f"{on_1b_tr} advances to 2nd", pbp_pa[len(pbp_pa) - 1]) != None):
            on_2b_tr = on_1b_tr
            on_1b_tr = None
        elif (re.search(f"{on_1b_tr} putout", pbp_pa[len(pbp_pa) - 1]) != None):
            on_1b_tr = None
        if (re.search(f"{batter} advances to 3rd", pbp_pa[len(pbp_pa) - 1]) != None):
            on_3b_tr = batter
        elif (re.search(f"{batter} advances to 2nd", pbp_pa[len(pbp_pa) - 1]) != None):
            on_2b_tr = batter
        elif (re.search(f"{batter} advances to 1st", pbp_pa[len(pbp_pa) - 1]) != None):
            on_1b_tr = batter
        
        if (re.search("for out number 3", pbp_pa[len(pbp_pa) - 1]) != None):
            outs_tr = 0
            on_3b_tr = None
            on_2b_tr = None
            on_1b_tr = None
            if (inning_topbot_tr == 'Top'):
                inning_topbot_tr = 'Bot'
            else:
                inning_topbot_tr = 'Top'
                inning_tr += 1
        elif (re.search("for out number 2", pbp_pa[len(pbp_pa) - 1]) != None):
            outs_tr = 2
        elif (re.search("for out number 1", pbp_pa[len(pbp_pa) - 1]) != None):
            outs_tr = 1
                
        pa_dict = {'game_date': game_date_l, 
                   'batter': batter_l, 
                   'pitcher': pitcher_l, 
                   'events': events_l, 
                   'description': description_l, 
                   'des': des_l, 
                   'stand': stand_l, 
                   'p_throws': p_throws_l, 
                   'game_type': game_type_l, 
                   'home_team': home_team_l, 
                   'away_team': away_team_l, 
                   'type': type_l, 
                   'balls': balls_l, 
                   'strikes': strikes_l, 
                   'game_year': game_year_l, 
                   'on_3b': on_3b_l, 
                   'on_2b': on_2b_l,  
                   'on_1b': on_1b_l, 
                   'outs_when_up': outs_when_up_l, 
                   'inning': inning_l, 
                   'inning_topbot': inning_topbot_l, 
                   'sv_id': sv_id_l, 
                   'game_pk': game_pk_l,
                   'fielder_2': fielder_2_l,
                   'fielder_3': fielder_3_l,
                   'fielder_4': fielder_4_l, 
                   'fielder_5': fielder_5_l, 
                   'fielder_6': fielder_6_l, 
                   'fielder_7': fielder_7_l, 
                   'fielder_8': fielder_8_l, 
                   'fielder_9': fielder_9_l, 
                   'at_bat_number': at_bat_number_l, 
                   'pitch_number': pitch_number_l, 
                   'home_score': home_score_l, 
                   'away_score': away_score_l, 
                   'bat_score': bat_score_l, 
                   'fld_score': fld_score_l, 
                   'post_away_score': post_away_score_l, 
                   'post_home_score': post_home_score_l, 
                   'post_bat_score': post_bat_score_l, 
                   'post_fld_score': post_fld_score_l,
                   'baserunner_event': baserunner_event_l}
        pa_df = pd.DataFrame(data=pa_dict)

        game_df = pd.concat([game_df, pa_df], ignore_index=True)
    
    else:
        if (pbp_pa[0] == 'Pitching Substitution'):
            if (inning_topbot_tr == 'Top'):
                home_pitcher = re.search(r"\w+\s\w+(?=\ssubs)", pbp_pa[1]).group(0)
                home_pitcher_throws = get_pitcher_throws(home_pitcher)
                if (home_pitcher_throws == 'S'):
                    home_pitcher_switch_pitcher = True
                else: home_pitcher_switch_pitcher = False
            else: 
                away_pitcher = re.search(r"\w+\s\w+(?=\ssubs)", pbp_pa[1]).group(0)
                away_pitcher_throws = get_pitcher_throws(away_pitcher)
                if (away_pitcher_throws == 'S'):
                    away_pitcher_switch_pitcher = True
                else: away_pitcher_switch_pitcher = False
        elif (pbp_pa[0] == 'Offensive Substitution'):
            # if the substitution is undefined
            if (re.search(r"(?<=for\s)\w+\s\w+", pbp_pa[1]) == None):
                pass
            elif ((re.search(r"(?<=for\s)\w+\s\w+", pbp_pa[1]).group(0) == away_fielders[2])|(re.search(r"(?<=for\s)\w+\s\w+", pbp_pa[1]).group(0) == home_fielders[2])):
                if (inning_topbot_tr == 'Top'):
                    away_fielders[2] = re.search(r"\w+\s\w+(?=\ssubs)", pbp_pa[1]).group(0)
                else: home_fielders[2] = re.search(r"\w+\s\w+(?=\ssubs)", pbp_pa[1]).group(0)
            elif ((re.search(r"(?<=for\s)\w+\s\w+", pbp_pa[1]).group(0) == away_fielders[3])|(re.search(r"(?<=for\s)\w+\s\w+", pbp_pa[1]).group(0) == home_fielders[3])):
                if (inning_topbot_tr == 'Top'):
                    away_fielders[3] = re.search(r"\w+\s\w+(?=\ssubs)", pbp_pa[1]).group(0)
                else: home_fielders[3] = re.search(r"\w+\s\w+(?=\ssubs)", pbp_pa[1]).group(0)
            elif ((re.search(r"(?<=for\s)\w+\s\w+", pbp_pa[1]).group(0) == away_fielders[4])|(re.search(r"(?<=for\s)\w+\s\w+", pbp_pa[1]).group(0) == home_fielders[4])):
                if (inning_topbot_tr == 'Top'):
                    away_fielders[4] = re.search(r"\w+\s\w+(?=\ssubs)", pbp_pa[1]).group(0)
                else: home_fielders[4] = re.search(r"\w+\s\w+(?=\ssubs)", pbp_pa[1]).group(0)
            elif ((re.search(r"(?<=for\s)\w+\s\w+", pbp_pa[1]).group(0) == away_fielders[5])|(re.search(r"(?<=for\s)\w+\s\w+", pbp_pa[1]).group(0) == home_fielders[5])):
                if (inning_topbot_tr == 'Top'):
                    away_fielders[5] = re.search(r"\w+\s\w+(?=\ssubs)", pbp_pa[1]).group(0)
                else: home_fielders[5] = re.search(r"\w+\s\w+(?=\ssubs)", pbp_pa[1]).group(0)
            elif ((re.search(r"(?<=for\s)\w+\s\w+", pbp_pa[1]).group(0) == away_fielders[6])|(re.search(r"(?<=for\s)\w+\s\w+", pbp_pa[1]).group(0) == home_fielders[6])):
                if (inning_topbot_tr == 'Top'):
                    away_fielders[6] = re.search(r"\w+\s\w+(?=\ssubs)", pbp_pa[1]).group(0)
                else: home_fielders[6] = re.search(r"\w+\s\w+(?=\ssubs)", pbp_pa[1]).group(0)
            elif ((re.search(r"(?<=for\s)\w+\s\w+", pbp_pa[1]).group(0) == away_fielders[7])|(re.search(r"(?<=for\s)\w+\s\w+", pbp_pa[1]).group(0) == home_fielders[7])):
                if (inning_topbot_tr == 'Top'):
                    away_fielders[7] = re.search(r"\w+\s\w+(?=\ssubs)", pbp_pa[1]).group(0)
                else: home_fielders[7] = re.search(r"\w+\s\w+(?=\ssubs)", pbp_pa[1]).group(0)
            elif ((re.search(r"(?<=for\s)\w+\s\w+", pbp_pa[1]).group(0) == away_fielders[8])|(re.search(r"(?<=for\s)\w+\s\w+", pbp_pa[1]).group(0) == home_fielders[8])):
                if (inning_topbot_tr == 'Top'):
                    away_fielders[8] = re.search(r"\w+\s\w+(?=\ssubs)", pbp_pa[1]).group(0)
                else: home_fielders[8] = re.search(r"\w+\s\w+(?=\ssubs)", pbp_pa[1]).group(0)
            elif ((re.search(r"(?<=for\s)\w+\s\w+", pbp_pa[1]).group(0) == away_fielders[9])|(re.search(r"(?<=for\s)\w+\s\w+", pbp_pa[1]).group(0) == home_fielders[9])):
                if (inning_topbot_tr == 'Bot'):
                    away_fielders[9] = re.search(r"\w+\s\w+(?=\ssubs)", pbp_pa[1]).group(0)
                else: home_fielders[9] = re.search(r"\w+\s\w+(?=\ssubs)", pbp_pa[1]).group(0)
        elif (pbp_pa[0] == 'Defensive Substitution'):
            if (re.search("subs", pbp_pa[1]) != None):
                # if the sub is for a DH
                if (re.search(r"(?<=at\s)\w+\s\w+|(?<=at\s)\w+", pbp_pa[1]) == None):
                    pass
                elif (re.search(r"(?<=at\s)\w+\s\w+|(?<=at\s)\w+", pbp_pa[1]).group(0) == 'Catcher'):
                    if (inning_topbot_tr == 'Top'):
                        home_fielders[2] = re.search(r"\w+\s\w+(?=\ssubs)", pbp_pa[1]).group(0)
                    else: away_fielders[2] = re.search(r"\w+\s\w+(?=\ssubs)", pbp_pa[1]).group(0)
                elif (re.search(r"(?<=at\s)\w+\s\w+|(?<=at\s)\w+", pbp_pa[1]).group(0) == 'First Base'):
                    if (inning_topbot_tr == 'Top'):
                        home_fielders[3] = re.search(r"\w+\s\w+(?=\ssubs)", pbp_pa[1]).group(0)
                    else: away_fielders[3] = re.search(r"\w+\s\w+(?=\ssubs)", pbp_pa[1]).group(0)
                elif (re.search(r"(?<=at\s)\w+\s\w+|(?<=at\s)\w+", pbp_pa[1]).group(0) == 'Second Base'):
                    if (inning_topbot_tr == 'Top'):
                        home_fielders[4] = re.search(r"\w+\s\w+(?=\ssubs)", pbp_pa[1]).group(0)
                    else: away_fielders[4] = re.search(r"\w+\s\w+(?=\ssubs)", pbp_pa[1]).group(0)
                elif (re.search(r"(?<=at\s)\w+\s\w+|(?<=at\s)\w+", pbp_pa[1]).group(0) == 'Third Base'):
                    if (inning_topbot_tr == 'Top'):
                        home_fielders[5] = re.search(r"\w+\s\w+(?=\ssubs)", pbp_pa[1]).group(0)
                    else: away_fielders[5] = re.search(r"\w+\s\w+(?=\ssubs)", pbp_pa[1]).group(0)
                elif (re.search(r"(?<=at\s)\w+\s\w+|(?<=at\s)\w+", pbp_pa[1]).group(0) == 'Shortstop'):
                    if (inning_topbot_tr == 'Top'):
                        home_fielders[6] = re.search(r"\w+\s\w+(?=\ssubs)", pbp_pa[1]).group(0)
                    else: away_fielders[6] = re.search(r"\w+\s\w+(?=\ssubs)", pbp_pa[1]).group(0)
                elif (re.search(r"(?<=at\s)\w+\s\w+|(?<=at\s)\w+", pbp_pa[1]).group(0) == 'Left Field'):
                    if (inning_topbot_tr == 'Top'):
                        home_fielders[7] = re.search(r"\w+\s\w+(?=\ssubs)", pbp_pa[1]).group(0)
                    else: away_fielders[7] = re.search(r"\w+\s\w+(?=\ssubs)", pbp_pa[1]).group(0)
                elif (re.search(r"(?<=at\s)\w+\s\w+|(?<=at\s)\w+", pbp_pa[1]).group(0) == 'Center Field'):
                    if (inning_topbot_tr == 'Top'):
                        home_fielders[8] = re.search(r"\w+\s\w+(?=\ssubs)", pbp_pa[1]).group(0)
                    else: away_fielders[8] = re.search(r"\w+\s\w+(?=\ssubs)", pbp_pa[1]).group(0)
                elif (re.search(r"(?<=at\s)\w+\s\w+|(?<=at\s)\w+", pbp_pa[1]).group(0) == 'Right Field'):
                    if (inning_topbot_tr == 'Bot'):
                        home_fielders[9] = re.search(r"\w+\s\w+(?=\ssubs)", pbp_pa[1]).group(0)
                    else: away_fielders[9] = re.search(r"\w+\s\w+(?=\ssubs)", pbp_pa[1]).group(0)
            elif (re.search("moves", pbp_pa[1]) != None):
                if (re.search(r"(?<=to\s)\w+\s\w+|(?<=to\s)\w+", pbp_pa[1]).group(0) == 'Catcher'):
                    if ((re.search(r"\w+\s\w+(?=\smoves)", pbp_pa[1]) != home_fielders[2]) & (re.search(r"\w+\s\w+(?=\smoves)", pbp_pa[1]) != away_fielders[2])):
                        if (inning_topbot_tr == 'Top'):
                            home_fielders[0] = home_fielders[2]
                            home_fielders[2] = re.search(r"\w+\s\w+(?=\smoves)", pbp_pa[1]).group(0)
                            for i in range(2, 10):
                                if (i == 2): continue
                                if (home_fielders[i] == re.search(r"\w+\s\w+(?=\smoves)", pbp_pa[1]).group(0)):
                                    home_fielders[i] = home_fielders[0]
                                    home_fielders[0] = 'Placeholder0'
                                    break
                        else: 
                            away_fielders[0] = away_fielders[2]
                            away_fielders[2] = re.search(r"\w+\s\w+(?=\smoves)", pbp_pa[1]).group(0)
                            for i in range(2, 10):
                                if (i == 2): continue
                                if (away_fielders[i] == re.search(r"\w+\s\w+(?=\smoves)", pbp_pa[1]).group(0)):
                                    away_fielders[i] = away_fielders[0]
                                    away_fielders[0] = 'Placeholder0'
                                    break
                elif (re.search(r"(?<=to\s)\w+\s\w+|(?<=to\s)\w+", pbp_pa[1]).group(0) == 'First Base'):
                    if ((re.search(r"\w+\s\w+(?=\smoves)", pbp_pa[1]) != home_fielders[3]) & (re.search(r"\w+\s\w+(?=\smoves)", pbp_pa[1]) != away_fielders[3])):
                        if (inning_topbot_tr == 'Top'):
                            home_fielders[0] = home_fielders[3]
                            home_fielders[3] = re.search(r"\w+\s\w+(?=\smoves)", pbp_pa[1]).group(0)
                            for i in range(2, 10):
                                if (i == 3): continue
                                if (home_fielders[i] == re.search(r"\w+\s\w+(?=\smoves)", pbp_pa[1]).group(0)):
                                    home_fielders[i] = home_fielders[0]
                                    home_fielders[0] = 'Placeholder0'
                                    break
                        else: 
                            away_fielders[0] = away_fielders[3]
                            away_fielders[3] = re.search(r"\w+\s\w+(?=\smoves)", pbp_pa[1]).group(0)
                            for i in range(2, 10):
                                if (i == 3): continue
                                if (away_fielders[i] == re.search(r"\w+\s\w+(?=\smoves)", pbp_pa[1]).group(0)):
                                    away_fielders[i] = away_fielders[0]
                                    away_fielders[0] = 'Placeholder0'
                                    break
                elif (re.search(r"(?<=to\s)\w+\s\w+|(?<=to\s)\w+", pbp_pa[1]).group(0) == 'Second Base'):
                    if ((re.search(r"\w+\s\w+(?=\smoves)", pbp_pa[1]) != home_fielders[4]) & (re.search(r"\w+\s\w+(?=\smoves)", pbp_pa[1]) != away_fielders[4])):
                        if (inning_topbot_tr == 'Top'):
                            home_fielders[0] = home_fielders[4]
                            home_fielders[4] = re.search(r"\w+\s\w+(?=\smoves)", pbp_pa[1]).group(0)
                            for i in range(2, 10):
                                if (i == 4): continue
                                if (home_fielders[i] == re.search(r"\w+\s\w+(?=\smoves)", pbp_pa[1]).group(0)):
                                    home_fielders[i] = home_fielders[0]
                                    home_fielders[0] = 'Placeholder0'
                                    break
                        else: 
                            away_fielders[0] = away_fielders[4]
                            away_fielders[4] = re.search(r"\w+\s\w+(?=\smoves)", pbp_pa[1]).group(0)
                            for i in range(2, 10):
                                if (i == 4): continue
                                if (away_fielders[i] == re.search(r"\w+\s\w+(?=\smoves)", pbp_pa[1]).group(0)):
                                    away_fielders[i] = away_fielders[0]
                                    away_fielders[0] = 'Placeholder0'
                                    break
                elif (re.search(r"(?<=to\s)\w+\s\w+|(?<=to\s)\w+", pbp_pa[1]).group(0) == 'Third Base'):
                    if ((re.search(r"\w+\s\w+(?=\smoves)", pbp_pa[1]) != home_fielders[5]) & (re.search(r"\w+\s\w+(?=\smoves)", pbp_pa[1]) != away_fielders[5])):
                        if (inning_topbot_tr == 'Top'):
                            home_fielders[0] = home_fielders[5]
                            home_fielders[5] = re.search(r"\w+\s\w+(?=\smoves)", pbp_pa[1]).group(0)
                            for i in range(2, 10):
                                if (i == 5): continue
                                if (home_fielders[i] == re.search(r"\w+\s\w+(?=\smoves)", pbp_pa[1]).group(0)):
                                    home_fielders[i] = home_fielders[0]
                                    home_fielders[0] = 'Placeholder0'
                                    break
                        else: 
                            away_fielders[0] = away_fielders[5]
                            away_fielders[5] = re.search(r"\w+\s\w+(?=\smoves)", pbp_pa[1]).group(0)
                            for i in range(2, 10):
                                if (i == 5): continue
                                if (away_fielders[i] == re.search(r"\w+\s\w+(?=\smoves)", pbp_pa[1]).group(0)):
                                    away_fielders[i] = away_fielders[0]
                                    away_fielders[0] = 'Placeholder0'
                                    break
                elif (re.search(r"(?<=to\s)\w+\s\w+|(?<=to\s)\w+", pbp_pa[1]).group(0) == 'Shortstop'):
                    if ((re.search(r"\w+\s\w+(?=\smoves)", pbp_pa[1]) != home_fielders[6]) & (re.search(r"\w+\s\w+(?=\smoves)", pbp_pa[1]) != away_fielders[6])):
                        if (inning_topbot_tr == 'Top'):
                            home_fielders[0] = home_fielders[6]
                            home_fielders[6] = re.search(r"\w+\s\w+(?=\smoves)", pbp_pa[1]).group(0)
                            for i in range(2, 10):
                                if (i == 6): continue
                                if (home_fielders[i] == re.search(r"\w+\s\w+(?=\smoves)", pbp_pa[1]).group(0)):
                                    home_fielders[i] = home_fielders[0]
                                    home_fielders[0] = 'Placeholder0'
                                    break
                        else: 
                            away_fielders[0] = away_fielders[6]
                            away_fielders[6] = re.search(r"\w+\s\w+(?=\smoves)", pbp_pa[1]).group(0)
                            for i in range(2, 10):
                                if (i == 6): continue
                                if (away_fielders[i] == re.search(r"\w+\s\w+(?=\smoves)", pbp_pa[1]).group(0)):
                                    away_fielders[i] = away_fielders[0]
                                    away_fielders[0] = 'Placeholder0'
                                    break
                elif (re.search(r"(?<=to\s)\w+\s\w+|(?<=to\s)\w+", pbp_pa[1]).group(0) == 'Left Field'):
                    if ((re.search(r"\w+\s\w+(?=\smoves)", pbp_pa[1]) != home_fielders[7]) & (re.search(r"\w+\s\w+(?=\smoves)", pbp_pa[1]) != away_fielders[7])):
                        if (inning_topbot_tr == 'Top'):
                            home_fielders[0] = home_fielders[7]
                            home_fielders[7] = re.search(r"\w+\s\w+(?=\smoves)", pbp_pa[1]).group(0)
                            for i in range(2, 10):
                                if (i == 7): continue
                                if (home_fielders[i] == re.search(r"\w+\s\w+(?=\smoves)", pbp_pa[1]).group(0)):
                                    home_fielders[i] = home_fielders[0]
                                    home_fielders[0] = 'Placeholder0'
                                    break
                        else: 
                            away_fielders[0] = away_fielders[7]
                            away_fielders[7] = re.search(r"\w+\s\w+(?=\smoves)", pbp_pa[1]).group(0)
                            for i in range(2, 10):
                                if (i == 7): continue
                                if (away_fielders[i] == re.search(r"\w+\s\w+(?=\smoves)", pbp_pa[1]).group(0)):
                                    away_fielders[i] = away_fielders[0]
                                    away_fielders[0] = 'Placeholder0'
                                    break
                elif (re.search(r"(?<=to\s)\w+\s\w+|(?<=to\s)\w+", pbp_pa[1]).group(0) == 'Center Field'):
                    if ((re.search(r"\w+\s\w+(?=\smoves)", pbp_pa[1]) != home_fielders[8]) & (re.search(r"\w+\s\w+(?=\smoves)", pbp_pa[1]) != away_fielders[8])):
                        if (inning_topbot_tr == 'Top'):
                            home_fielders[0] = home_fielders[8]
                            home_fielders[8] = re.search(r"\w+\s\w+(?=\smoves)", pbp_pa[1]).group(0)
                            for i in range(2, 10):
                                if (i == 8): continue
                                if (home_fielders[i] == re.search(r"\w+\s\w+(?=\smoves)", pbp_pa[1]).group(0)):
                                    home_fielders[i] = home_fielders[0]
                                    home_fielders[0] = 'Placeholder0'
                                    break
                        else: 
                            away_fielders[0] = away_fielders[8]
                            away_fielders[8] = re.search(r"\w+\s\w+(?=\smoves)", pbp_pa[1]).group(0)
                            for i in range(2, 10):
                                if (i == 8): continue
                                if (away_fielders[i] == re.search(r"\w+\s\w+(?=\smoves)", pbp_pa[1]).group(0)):
                                    away_fielders[i] = away_fielders[0]
                                    away_fielders[0] = 'Placeholder0'
                                    break
                elif (re.search(r"(?<=to\s)\w+\s\w+|(?<=to\s)\w+", pbp_pa[1]).group(0) == 'Right Field'):
                    if ((re.search(r"\w+\s\w+(?=\smoves)", pbp_pa[1]) != home_fielders[9]) & (re.search(r"\w+\s\w+(?=\smoves)", pbp_pa[1]) != away_fielders[9])):
                        if (inning_topbot_tr == 'Top'):
                            home_fielders[0] = home_fielders[9]
                            home_fielders[9] = re.search(r"\w+\s\w+(?=\smoves)", pbp_pa[1]).group(0)
                            for i in range(2, 10):
                                if (i == 9): continue
                                if (home_fielders[i] == re.search(r"\w+\s\w+(?=\smoves)", pbp_pa[1]).group(0)):
                                    home_fielders[i] = home_fielders[0]
                                    home_fielders[0] = 'Placeholder0'
                                    break
                        else: 
                            away_fielders[0] = away_fielders[9]
                            away_fielders[9] = re.search(r"\w+\s\w+(?=\smoves)", pbp_pa[1]).group(0)
                            for i in range(2, 10):
                                if (i == 9): continue
                                if (away_fielders[i] == re.search(r"\w+\s\w+(?=\smoves)", pbp_pa[1]).group(0)):
                                    away_fielders[i] = away_fielders[0]
                                    away_fielders[0] = 'Placeholder0'
                                    break

game_df['balls'] = game_df['balls'].astype(int)
game_df['strikes'] = game_df['strikes'].astype(int)
game_df['game_year'] = game_df['game_year'].astype(int)
game_df['outs_when_up'] = game_df['outs_when_up'].astype(int)
game_df['inning'] = game_df['inning'].astype(int)
game_df['at_bat_number'] = game_df['at_bat_number'].astype(int)
# game_df['pitch_number'] = game_df['pitch_number'].astype(int)
game_df['home_score'] = game_df['home_score'].astype(int)
game_df['away_score'] = game_df['away_score'].astype(int)
game_df['bat_score'] = game_df['bat_score'].astype(int)
game_df['fld_score'] = game_df['fld_score'].astype(int)
game_df['post_away_score'] = game_df['post_away_score'].astype(int)
game_df['post_home_score'] = game_df['post_home_score'].astype(int)
game_df['post_bat_score'] = game_df['post_bat_score'].astype(int)
game_df['post_fld_score'] = game_df['post_fld_score'].astype(int)

game_df['hit_location'] = np.nan
game_df['bb_type'] = None
game_df['pitch_type'] = None
game_df['plate_x'] = np.nan
game_df['plate_z'] = np.nan
game_df['zone'] = np.nan
game_df['hc_x'] = np.nan
game_df['hc_y'] = np.nan
game_df['hit_distance_sc'] = np.nan
game_df['launch_speed_angle'] = np.nan
game_df['pitch_name'] = None
game_df['woba_value'] = np.nan
game_df['woba_denom'] = np.nan
game_df['babip_value'] = np.nan
game_df['iso_value'] = np.nan
# game_df['role_key'] = 'RP'
game_df['pitch_number_appearance'] = np.nan
# game_df['pitcher_at_bat_number'] = np.nan
# game_df['times_faced'] = np.nan

game_df.loc[(pd.isna(game_df['pitch_number'])) == False, 'pitch_number_appearance'] = game_df[pd.isna(game_df['pitch_number']) == False].groupby('pitcher').cumcount() + 1

game_df['role_key'] = 'RP'
game_df.loc[((game_df['pitcher'] == HOME_STARTING_PITCHER) | (game_df['pitcher'] == AWAY_STARTING_PITCHER)), 'role_key'] = 'SP'

pitcher_at_bat_number_df = game_df.groupby(['pitcher', 'sv_id']).size().reset_index().rename(columns={0:'num_pitches'})
pitcher_at_bat_number_df['pitcher_at_bat_number'] = pitcher_at_bat_number_df.groupby('pitcher').cumcount() + 1
pitcher_at_bat_number_df = pitcher_at_bat_number_df[['pitcher', 'sv_id', 'pitcher_at_bat_number']]
game_df = pd.merge(game_df, pitcher_at_bat_number_df, on=['pitcher', 'sv_id'], how='left')

times_faced_df = game_df.groupby(['pitcher', 'batter', 'sv_id']).size().reset_index().rename(columns={0:'num_pitches'})
times_faced_df['times_faced'] = times_faced_df.groupby(['pitcher', 'batter']).cumcount() + 1
times_faced_df = times_faced_df[['pitcher', 'batter', 'sv_id', 'times_faced']]
game_df = pd.merge(game_df, times_faced_df, on=['pitcher', 'batter', 'sv_id'], how='left')

# print PAs with a baserunner event
baserunner_event_sv_ids = game_df[game_df['baserunner_event'] == 1]['sv_id'].unique().tolist()

game_df = game_df[['game_date', 'game_pk', 'away_team', 'home_team', 
                   'game_type', 'game_year', 'sv_id', 'batter',
                   'pitcher', 'stand', 'p_throws', 'events',
                   'des', 'description', 'type', 'hit_location', 
                   'bb_type', 'balls', 'strikes', 'outs_when_up',
                   'inning', 'inning_topbot', 'pitch_type', 'plate_x',
                   'plate_z', 'zone', 'hc_x', 'hc_y',
                   'hit_distance_sc', 'launch_speed_angle', 'pitch_name', 'on_3b',
                   'on_2b', 'on_1b', 'fielder_2', 'fielder_3',
                   'fielder_4', 'fielder_5', 'fielder_6', 'fielder_7',
                   'fielder_8', 'fielder_9', 'at_bat_number', 'pitch_number',
                   'away_score', 'home_score', 'bat_score', 'fld_score',
                   'post_away_score', 'post_home_score', 'post_bat_score', 'post_fld_score',
                   'woba_value', 'woba_denom', 'babip_value', 'iso_value',
                   'role_key', 'pitch_number_appearance', 'pitcher_at_bat_number', 'times_faced']]

output_csv_file_string = '~/baycats/raw_game_data/' + GAME_PK + '.csv'
game_df.to_csv(output_csv_file_string, index=False)

# print box score stats

# list of events that end an at-bat
ab_events = ['double', 'double_play', 'field_error', 'field_out', 'fielders_choice', 'fielders_choice_out', 'force_out', 'grounded_into_double_play', 'home_run', 'other_out', 'single', 'strikeout', 'strikeout_double_play', 'triple', 'triple_play']

away_df = game_df.loc[game_df['inning_topbot'] == 'Top', :]

away_df.loc[:, 'AB'] = 0
away_df.loc[away_df['events'].isin(ab_events), 'AB'] = 1
away_df.loc[:, 'H'] = 0
away_df.loc[away_df['events'].isin(['single', 'double', 'triple', 'home_run']), 'H'] = 1
away_df.loc[:, 'BB'] = 0
away_df.loc[away_df['events'].isin(['walk', 'intentional_walk']), 'BB'] = 1
away_df.loc[:, 'SO'] = 0
away_df.loc[away_df['events'].isin(['strikeout', 'strikeout_double_play']), 'SO'] = 1

away_boxscore = away_df.groupby('game_pk')[['AB', 'H', 'BB', 'SO']].sum()
away_boxscore['R'] = game_df.loc[(len(game_df.index) - 1), 'post_away_score']
away_boxscore = away_boxscore[['AB', 'R', 'H', 'BB', 'SO']].reset_index()

home_df = game_df.loc[game_df['inning_topbot'] == 'Bot', :]

home_df.loc[:, 'AB'] = 0
home_df.loc[home_df['events'].isin(ab_events), 'AB'] = 1
home_df.loc[:, 'H'] = 0
home_df.loc[home_df['events'].isin(['single', 'double', 'triple', 'home_run']), 'H'] = 1
home_df.loc[:, 'BB'] = 0
home_df.loc[home_df['events'].isin(['walk', 'intentional_walk']), 'BB'] = 1
home_df.loc[:, 'SO'] = 0
home_df.loc[home_df['events'].isin(['strikeout', 'strikeout_double_play']), 'SO'] = 1

home_boxscore = home_df.groupby('game_pk')[['AB', 'H', 'BB', 'SO']].sum()
home_boxscore['R'] = game_df.loc[(len(game_df.index) - 1), 'post_home_score']
home_boxscore = home_boxscore[['AB', 'R', 'H', 'BB', 'SO']].reset_index()

print(f"PAS WITH BASERUNNER EVENTS: {baserunner_event_sv_ids}")
print(f"{game_df.loc[(len(game_df.index) - 1), 'away_team']}: {away_boxscore.loc[0, 'AB']} AB, {away_boxscore.loc[0, 'R']} R, {away_boxscore.loc[0, 'H']} H, {away_boxscore.loc[0, 'BB']} BB, {away_boxscore.loc[0, 'SO']} SO")
print(f"{game_df.loc[(len(game_df.index) - 1), 'home_team']}: {home_boxscore.loc[0, 'AB']} AB, {home_boxscore.loc[0, 'R']} R, {home_boxscore.loc[0, 'H']} H, {home_boxscore.loc[0, 'BB']} BB, {home_boxscore.loc[0, 'SO']} SO")