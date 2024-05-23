Game data and scripts for the Baycats 2024 season.

# Folders

## raw_game_data
A folder containing the game files scraped without any pitch tracking. These files are named in the convention YYYYMMDDAAAHHHN.csv where YYYY is the year, MM is the month with a leading zero if necessary, DD is the day of the month with a leading zero if necessary, and N is the doubleheader identifier (one if the game was either not part of a doubleheader or was the first game of a doubleheader and two if the game was the second game of a doubleheader).

## pitches_tracked_game_data
A folder containing the game files with either partial or complete pitch tracking. These files are named identically to the corresponding game file in raw_game_data, except the game info is followed by "_pt" to indicate pitch tracking.

## raw_game_txt_files
A folder containing the .txt file of the scraped game info. These files show the list of lists of strings that the scraper parses and converts into raw game data. Each separated block of text would indicate one list of strings within the list. 

# Scripts

## pointstreak_scraper.py
A script to scrape the game data from Pointstreak. This script takes values specified at the top of the script before running, saves a .csv file in the raw_game_data folder, and outputs plate appearances with baserunning events and the box score to compare to the Pointstreak boxscore.

### How to use the script
1. Ensure all required libraries and packages at the top of the script have been installed.
2. Change all values within the chunk of code contained within the lines of dashes to correspond to the game being scraped. These values are the game date, the away and home teams, the doubleheader identifier, the away and home starting pitchers, and the away and home starting fielders.
3. Run the script.
4. Check the plate appearances with baserunning events output by the script. Manage baserunning events by manually editing the .csv file saved within the raw_game_data folder (in Excel or with another program) (more details on managing baserunning events below).
5. Check that the output box scores for the game match the Pointstreak boxscore. Note that RBIs are not reported in the output boxscore.

### Managing baserunning events
The output of the script is a list of all plate appearances by sv_id (plate appearance id) with baserunning events. Baserunning events currently tracked are: stolen bases, caught stealing, wild pitches, passed balls, pickoff attempts.
Open the raw game data in a program to edit the raw game data .csv file (Excel or another program) and navigate to the Pointstreak gamelive page on the web. For each sv_id output, find the plate appearance by the inning, batter and pitcher in the .csv file and in the gamelive page. Establish the baserunning event being identified and the pitch it occurred on (usually baserunning events will be listed after the pitch, but if the baserunning event occurred on the last pitch of the plate appearance it may be listed first (for example see the stolen base on a strikeout in the first inning of the May 16, 2024 Toronto-Barrie game)).
**TODO: Output more info (inning, batter, pitcher, outs) about the plate appearance in the script output.**

Case 1: The baserunning event occurred on a pitch that was not the first or last of the plate appearance and there was only a single baserunning event on the play.
1. Set the correct baserunning event in *events* (this column should be empty as the plate appearance didn't end).
2. Set the correct runners on base for the remainder of the plate appearance (beginning after the pitch with the baserunner event) (this should be correct beginning after the plate appearance in the data).
3. Set the correct value in *des*. For baserunning events occurring in a plate appearance, these should be appended before the results of the plate appearance (note in the last pitch of the at bat this should include all baserunning events, the value in this row can be copied and pasted into all pitches earlier in the plate appearance).
4. Set the correct value in *outs_when_up* if the baserunner was put out on the bases for the remainder of the plate appearance (this should be correct beginning after the plate appearance in the data).
5. Set the correct value in the score columns (*away_score*, *home_score*, *bat_score*, *post_away_score*, etc.) if any baserunners scored on the baserunning events.

Case 2: The baserunning event occurred on a plate appearance-ending pitch or there were multiple baserunning events on the pitch (for example a double steal).
1. If the baserunning event occurred on a plate appearance-ending pitch.
    1. Add a new row to the raw game data below the plate appearance-ending pitch.
    2. Copy all values except the values in *events* and *type* from the pitch the baserunning event occurred on (the row above) (for pitch count tracking within the plate appearance or pitcher appearance these will be repeat values).
    3. Set the *events* value to the correct baserunning event (see data-dictionary.xlsx for all possible values).
    4. Set the *type* value to "E" (for event, for calculating most non-baserunning tracking stats we can then filter out all rows with *type* E).
2. If there were multiple baserunning events on the pitch.
    1. Treat the leading baserunner as if it was a singular event on the pitch (treat it as in Case 1).
    2. Add a new row below the pitch the baserunner event occurred on.
    3. Copy all values except the values in the *events* and *type* columns from the pitch the baserunning event occurred on (the row above) (for pitch count tracking within the plate appearance or pitcher appearance these will be repeat values).
    4. Set the *events* value to the correct baserunning event (see data-dictionary.xlsx for all possible values).
    5. Set the *type* value to "E" (for event, for calculating most non-baserunning tracking stats we can then filter out all rows with *type* E).
  
## pitch_tracker.R
A script to track the pitch type, hit location, batted ball type, quality of contact, location in the strike zone, and location of the batted ball in the field. This script reads game data files in the raw_game_data or pitches_tracked_game_data folders and saves a .csv file with the pitches tracked in the pitches_tracked_game_data folder.

### How to use the script
1. Ensure all required libraries and packages at the top of the script have been installed.
2. Change all values within the chunk of code contained within the lines of dashes to correspond to the game being tracked. These values are the game id (in the same form as the file naming convention), and a partially tracked identifier. Set the partially tracked identifier to TRUE if the game is partially tracked and pitches already tracked will be loaded and won't have to be redone.
3. Run the app.
4. See the game situation for each pitch displayed in the tables, check that these values are correct in the game video being used to track the pitches.
**TODO: Display the runners on base in a table below the current game situation tables, but above the strike zone and field locations.**
6. Select the pitch type thrown on the pitch from the dropdown menu, or select "Unknown" if the pitch type on the pitch cannot be tracked. Click the location in the strike zone of the pitch, don't click on the location in the strike zone if the pitch location cannot be tracked. **The app will not let you continue to the next pitch without a selected pitch type value. The app will let you continue to the next pitch without a select pitch location.**
7. If the ball was put in play, select a value for the hit location (the position of the first fielder to touch the ball), the batted ball type and the quality of contact (launch/speed angle) (Barrel and Solid Contact indicate hard hit balls (by estimated exit velocity), Flare/Burner indicate medium hit balls, and all other possible values indicate weakly hit balls). If any of those values cannot be tracked, select "Unknown". **If the pitch resulted in a home run, do not put a hit location as no fielder fielded the ball. The app will not let you continue to the next pitch if the value of *type* on the pitch was "X" without a selected value in those columns. If the value on the pitch was not "X" then you can continue to the next pitch without selecting any values in those columns. If the pitch resulted in a strikeout, the hit location will be automatically set to the catcher (as they record a putout).**
8. Click the 'Next' button to continue to the next pitch. The 'Previous' button goes to the pitch before.
9. When you're done tracking (the game is fully tracked or you're partially done), click the 'Done' button and the game data file with the pitch tracking will be saved in the pitches_tracked_game_data folder. **The same restrictions for requiring values before clicking the 'Next' button pertain to clicking the 'Done' button.**

### Optional features
1. In 'Strike Zone' view, toggle between the catcher or pitcher's view of home plate depending on which view is easiest to track using the game footage (inverting the axis to record pitches from both views on the same scale is done automatically).
2. If you would like to skip to an inning (if the game has been partially tracked or you would only like to track pitches from select innings or from a select pitcher), set the inning, and top or bottom that you would like to skip to, click the 'Fast Forward' button, and tracking will begin at that half-inning. **There are no restrictions for requiring values when fast forwarding. Clicking 'Fast Forward' does not save any recorded values, if you would like to skip innings, ensure that you click 'Next' to continue past the pitch that you would like to track before clicking 'Fast Forward'.**
