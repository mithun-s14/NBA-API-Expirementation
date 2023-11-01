from re import L
from matplotlib import patches
import numpy as np
import pandas as pd
import requests
from bs4 import BeautifulSoup

# NBA_API
from nba_api.stats.static import players
from nba_api.stats.endpoints import shotchartdetail
from nba_api.stats.endpoints import playercareerstats
from nba_api.stats.endpoints import playergamelog
from nba_api.stats.library.parameters import SeasonAll

# matplotlib
import matplotlib.pyplot as plt
import seaborn as sns

from matplotlib import cm
from matplotlib.patches import Circle, Rectangle, Arc, ConnectionPatch
from matplotlib.patches import Polygon
from matplotlib.collections import PatchCollection
from matplotlib.colors import LinearSegmentedColormap, ListedColormap, BoundaryNorm
from matplotlib.path import Path
from matplotlib.patches import PathPatch
from sqlalchemy import except_all


# get_player_stats: player_name, season_id, --> STATS

def get_player_stats(player_name, season_id):
    # Player dictionary
    nba_players = players.get_players()
    
    # Verifying if player given exists
    try:
        player_dict = [player for player in nba_players if player['full_name'] == player_name][0]
    except IndexError:
        print("Player given does not exist in database.")
        return None, None

    # Career stats table
    career = playercareerstats.PlayerCareerStats(player_id=player_dict['id'])
    career_df = career.get_data_frames()[0]

    # Team ID during the season
    team_id = career_df[career_df['SEASON_ID'] == season_id]['TEAM_ID']
    
    # Check to see if year given was entered correctly
    try:
        team_id = int(team_id)
    except TypeError:
        print("Year given was entered incorrectly.")
        return None, None   

# get_player_shotchartdetail: player_name, season_id, --> player_shotchart_df, league_avg

def get_player_shotchartdetail(player_name, season_id):

    # Player dictionary
    nba_players = players.get_players()
    
    # Verifying if player given exists
    try:
        player_dict = [player for player in nba_players if player['full_name'] == player_name][0]
    except IndexError:
        print("Player given does not exist in database.")
        return None, None

    # Career stats table
    career = playercareerstats.PlayerCareerStats(player_id=player_dict['id'])
    career_df = career.get_data_frames()[0]

    # Team ID during the season
    team_id = career_df[career_df['SEASON_ID'] == season_id]['TEAM_ID']
    
    # Check to see if year given was entered correctly
    try:
        team_id = int(team_id)
    except TypeError:
        print("Year given was entered incorrectly.")
        return None, None

    # shotchartdetail endpoints
    shotchartlist = shotchartdetail.ShotChartDetail(team_id = int(team_id),
                                                    player_id = int(player_dict['id']),
                                                    season_type_all_star = 'Regular Season',
                                                    season_nullable = season_id,
                                                    context_measure_simple = "FGA").get_data_frames()
    return shotchartlist[0], shotchartlist[1]

#draw shot chart

def draw_court(ax = None, color = "blue", lw = 1, outer_lines=False):
    if ax is None:
        ax = plt.gca()
    
    # Hoop
    hoop = Circle((0,0), radius = 7.5, linewidth = lw, color = color, fill = False)
    
    # Backboard
    backboard = Rectangle((-30, -12.5), 60, 0, linewidth=lw, color = color)

    # The paint
    outer_box = Rectangle((-80, -47.5), 160, 190, linewidth=lw, color = color, fill = False)
    inner_box = Rectangle((-60, -47.5), 120, 190, linewidth=lw, color = color, fill = False)

    # Free throw top arc
    top_free_throw = Arc((0, 142.5), 120, 120, theta1 = 0, theta2 = 180, linewidth=lw, color = color, fill = False)

    # Free bottom top arc
    bottom_free_throw = Arc((0, 0), 80, 80, theta1 = 0, theta2 = 180, linewidth=lw, color = color)

    # Restricted Zone
    restricted = Arc((0, 0), 80, 80, theta1 = 0, theta2 = 180, linewidth=lw, color = color)

    # 3pt Line
    corner_three_a = Rectangle((-220, -47.5), 0, 140, linewidth = lw, color = color)
    corner_three_b = Rectangle((220, -47.5), 0, 140, linewidth = lw, color = color)
    three_arc = Arc((0,0), 475, 475, theta1 =22, theta2 = 158, linewidth = lw, color = color)

    # Center Court
    center_outer_arc = Arc((0,422.5), 120, 120, theta1 =180, theta2 = 0, linewidth = lw, color = color)
    center_inner_arc = Arc((0,422.5), 40, 40, theta1 =180, theta2 = 0, linewidth = lw, color = color)
    
    court_elements = [hoop, backboard, outer_box, inner_box, top_free_throw, bottom_free_throw, restricted, corner_three_a, corner_three_b, three_arc, center_outer_arc, center_inner_arc]

    if outer_lines:
        outer_lines = Rectangle((-250, -47.5), 500, 470, linewidth = lw, color = color, fill = False)

    for element in court_elements:
        ax.add_patch(element)

# Shot Chart Function
def shot_chart(data, title = "", color = "b", xlim = (-250, 250), ylim = (422.5, -47.5), line_color = "blue",
             court_color = "white", court_lw = 2, outer_lines = False, flip_court = False, gridsize = None,
             ax = None, despine = False):

    if (ax is None):
        ax = plt.gca()
    
    if not flip_court:
        ax.set_xlim(xlim)
        ax.set_ylim(ylim)
    else:
        ax.set_xlim(xlim[::-1])
        ax.set_ylim(ylim[::-1])
    
    ax.tick_params(labelbottom = "off", labelleft = "off")
    ax.set_title(title, fontsize = 18)

    # draws the court using the draw_court()
    draw_court(ax, color = line_color, lw = court_lw, outer_lines = outer_lines)

    # seperate color by make or miss
    x_missed = data[data['EVENT_TYPE'] == 'Missed Shot']['LOC_X']
    y_missed = data[data['EVENT_TYPE'] == 'Missed Shot']['LOC_Y']

    x_made = data[data['EVENT_TYPE'] == 'Made Shot']['LOC_X']
    y_made = data[data['EVENT_TYPE'] == 'Made Shot']['LOC_Y']

    # Plot missed shots
    ax.scatter(x_missed, y_missed, c ='r', marker = 'x', s = 300, linewidths=3)
    
    # Plot made shots
    ax.scatter(x_made, y_made, facecolors = 'none', edgecolors='g', marker = 'o', s = 100, linewidths=3)

    # Set the spines to match the rest of court lines, makes outer_lines
    for spine in ax.spines:
        ax.spines[spine].set_lw(court_lw)
        ax.spines[spine].set_color(line_color)
    
    if despine:
        ax.spines["top"].set_visible(False)
        ax.spines["bottom"].set_visible(False)
        ax.right["top"].set_visible(False)
        ax.left["bottom"].set_visible(False)

    return ax

# Method to get a player's stats for the season
def get_season_stats(player, year):

    # Scraping and saving data
    url = 'https://www.basketball-reference.com/leagues/NBA_{}_per_game.html'.format(year)
   
    r = requests.get(url)
    r_html = r.text # Get's seasons stats for year and turns into .text
    soup = BeautifulSoup(r_html,'html.parser') # Parsing with Beautiful Soup object
    table=soup.find_all(class_="full_table")
    
    # Extracting List of column names
    head=soup.find(class_="thead")
    
    column_names_raw=[head.text for item in head][0]
    
    column_names_polished=column_names_raw.replace("\n",",").split(",")[2:-1]
    
    # Extracting full list of player_data
    players=[]
    
    for i in range(len(table)):
        player_=[]
        
        for td in table[i].find_all("td"):
            player_.append(td.text)
    
        players.append(player_)
    df=pd.DataFrame(players, columns=column_names_polished).set_index("Player")
    
    # Cleaning the player's name from occasional special characters
    df.index=df.index.str.replace('*', '')

    print(df.loc[player])

# Uses nba_api to retrieve a given player's last 10 game stats
def get_last_10(player):
    player_id = next((x for x in players.get_players() if x.get("full_name") == player), None).get("id") # Find player_id
    gamelog = pd.concat(playergamelog.PlayerGameLog(player_id, season=SeasonAll.all).get_data_frames()) # Get player's gamelog
    gamelog["GAME_DATE"] = pd.to_datetime(gamelog["GAME_DATE"], format="%b %d, %Y") # Convert date formatting
    gamelog = gamelog.query("GAME_DATE.dt.year in [2023, 2024]") # Only search in most recent season
    gamelog_last_10 = gamelog.head(10) # Get last 10 games
    gamelog_last_10 = gamelog_last_10.drop(['Player_ID', 'Game_ID', 'SEASON_ID','FG_PCT', 'FG3_PCT', 'VIDEO_AVAILABLE'], axis=1) # Remove unwanted columns
    print(gamelog_last_10) 



if __name__ == "__main__":
    print("Menu\n1. Player Shot Chart Generator\n")
    print("2. Display season stats\n")
    print("3. Display season game log")
    option = input("Enter option: ")

    if(option.strip() == "1"):
        pName = input("\nEnter player's name (e.g. LeBron James): ")
        year = input("\nEnter year (e.g. 2019-20): ")

        if(get_player_shotchartdetail(pName, year) != None, None):

            player_shotchart_df, league_avg = get_player_shotchartdetail(pName, year)

            shot_chart(player_shotchart_df, title = pName + " Shot Chart " + year)

            plt.rcParams['figure.figsize'] = (12, 11)
            plt.show()

    elif (option.strip() == "2"):
        pName = input("\nEnter player's name (e.g. LeBron James): ")
        year = input("\nEnter year (e.g. 2019-20): ")
        get_season_stats(pName, year)
    
    elif (option.strip() == "3"):
        pName = input("\nEnter player's name (e.g. LeBron James): ")
        get_last_10(pName)

    