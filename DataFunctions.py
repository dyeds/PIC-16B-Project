import pandas as pd
import numpy as np
import networkx as nx
import tensorflow as tf
import cfbd
import sqlite3
from plotly import express as px
import plotly.graph_objects as go


def get_fbs_games(api_instance,year):
    """Extracts all D1 FBS games info for a fixed year.
    It uses an cfbd API instance and returns a list of game objects.

    Args:
        api_instance: Instance of the GamesApi class.
        year (int): Season year.

    Returns:
        list: List of game objects.
    """
    # obtains all fbs games in a list
    gamelist = api_instance.get_games(year=year,division='fbs')
    
    # selects only games between fbs teams, no fcs vs fbs games.
    gamelist = [game for game in gamelist if (game.home_division==game.away_division=="fbs" 
                                                and game.completed==True)]
    return gamelist

def df_from_games(gamelist):
    """Transforms a list of games into a pandas dataframe

    Args:
        gamelist (list): List of games.

    Returns:
        DataFrame: Includes all the games in a dataframe format
    """
    gamelist = [game.to_dict() for game in gamelist]
    gamemetrics = ['away_conference','away_id','away_points','away_team',
                   'home_conference','home_id','home_points','home_team',
                   'id', 'season','neutral_site']
    gamelist = [{x:game[x] for x in game if x in gamemetrics} for game in gamelist]
    
    df = pd.DataFrame(gamelist)
    df['game_spread'] = df['home_points'] - df['away_points']
    df['game_totalpts'] = df['home_points'] + df['away_points']
    return df

def get_fbs_betting(api_instance, year, conferences):
    """Extracts all D1 FBS games betting lines for a fixed year.
    It uses an cfbd API instance and returns a list of betting lines objects.

    Args:
        api_instance: Instance of the BettingApi class.
        year (int): Season year.
        conferences (list): List with all the FBS conferences.

    Returns:
        list: List of betting-line objects.
    """
    betting_info=api_instance.get_lines(year=year)
    
    betting_info=[game for game in betting_info if (game.away_conference in conferences
                                                    and game.home_conference in conferences)] 
    return betting_info

def df_betting_lines(betting_info):
    """Transforms a list of betting-lines into a pandas dataframe

    Args:
        gamelist (list): List of betting-lines.

    Returns:
        DataFrame: Includes all the betting-lines in a dataframe format
    """
    # for each betting-line object, create a dictionary with all values
    betting_lines=[game.to_dict() for game in betting_info]
    
    for game in betting_lines:
        away_length=len(game['away_team'])
        home_length=len(game['home_team'])
        game_lines=[]
        over_unders=[]
    
        for i in range(len(game['lines'])):
            if (game['lines'][i]['formatted_spread'][:away_length+2]==(game['away_team']+' -') 
                and game['lines'][i]['formatted_spread'][away_length+2:]!='null'):
                game_lines.append(float(game['lines'][i]['formatted_spread'][away_length+1:]))
            
            elif (game['lines'][i]['formatted_spread'][:home_length+2]==(game['home_team']+' -')
                  and game['lines'][i]['formatted_spread'][home_length+2:]!='null'):
                game_lines.append(abs(float(game['lines'][i]['formatted_spread'][home_length+1:])))
        
            if (game['lines'][i]['over_under']!=None):
                over_unders.append(game['lines'][i]['over_under'])
            
        if len(game_lines)!=0:   
            game['av_spread']=np.mean(game_lines)
        if len(over_unders)!=0:
            game['av_total']=np.mean(over_unders)
    
    # creating a dataframe with the average spread and total points per game.
    # note: averages are used as there are multiple lines for some games.
    df = pd.DataFrame(betting_lines)[['id','av_spread','av_total']]
    return df

# not using this bc its 1 line of code
# def get_team_advstats(api_instance,year):
#     teamstats = api_instance.get_advanced_team_season_stats(year=year)
#     return teamstats

def word_adder(word,dict):
    """Function strictly used for formatting on df_team_stats function.
    Needed because dictionary for team stats has dictionaries as values.

    Args:
        word (str): Word to add.
        dict (dict): Dictionary to update.

    Returns:
        dict: New dictionary with word added.
    """
    word=word+"_"
    new_dict={}
    for key,value in dict.items():
        new_key = f"{word}{key}"
        new_dict[new_key] = value
    return new_dict

def word_adder2(dict):
    """Function strictly used for formatting on df_team_stats function.
    Needed because dictionary for team stats has dictionaries as values.
    Args:
        dict (dict): Dictionary to update.
    
    Returns:
        dict: Dictionary with updated keys
    """
    updaterkeys = []
    for key,value in dict.items():
        if type(value)==type(dict):
            updaterkeys.append([key,value])
    
    for i in range(len(updaterkeys)):
        dict.update(word_adder(word=updaterkeys[i][0],dict=updaterkeys[i][1]))
        dict.pop(updaterkeys[i][0])
    return dict

def df_team_advstats(teamstats):
    """Transforms a list of team statistics into a pandas dataframe.

    Args:
        teamstats (list): List of Team Statistic Objects.

    Returns:
       DataFrame: Has all team statistics for given year.
    """
    teamstats = [{**{'team':t.team,'season':t.season,'conference':t.conference},
                **word_adder(word="Offensive",dict=t.offense.to_dict()),
                **word_adder(word="Defensive",dict=t.defense.to_dict())} for t in teamstats]
    
    teamstats = [word_adder2(t) for t in teamstats]
    df = pd.DataFrame(teamstats)
    df = df.drop('Defensive_passing_plays_total_ppa',axis=1)
    return df

def df_stats_needed(df,col):
    """Returns a dataframe with selected columns metrics. Used for Team Stats.

    Args:
        df (DataFrame): DataFrame with Team Statistics needed.
        col (list): Metrics to use in DataFrame.

    Returns:
        DataFrame: Selected team statistics.
    """
    df = df[col]
    return df

def get_team_locations(api_instance,conferences):
    """Obtains Team Locations using the API and stores 

    Args:
        api_instance: Instance of the TeamsApi class
        conferences (list): List of FBS conferences

    Returns:
        DataFrame: Displays latitude and longitude for all teams.
    """
    team_info=api_instance.get_teams()
    team_info[0]
    team_info=[[team.school,team.id,team.location.latitude,
                team.location.longitude] for team in team_info if (team.conference in conferences)]
    locations=pd.DataFrame(team_info)
    locations=locations.rename(columns={0:'team',1:'id',2:'latitude',3:'longitude'})
    
    return locations


def prediction_to_score(pred_spread,pred_total,std_spread,std_total):
    """Transforms a predicted spread and over/under to an actual score,
    using a random normal distribution that has as mean the model predictions,
    and as standard deviation the standard error of the model.

    Args:
        pred_spread (float): Model predicted spread.
        pred_total (float): Model predicted total points.
        std_spread (float): Standard deviation on spread.
        std_total (float): Standard deviation on total points.

    Returns:
        str: String for of result with Away and Home points.
    """
    adjusted_spread=np.random.normal(pred_spread,std_spread)
    adjusted_total=np.random.normal(pred_total,std_total)
    adjusted_home_points=(adjusted_spread+adjusted_total)/2
    adjusted_away_points=adjusted_total-adjusted_home_points
    adjusted_home_points=int(np.rint(adjusted_home_points))
    adjusted_away_points=int(np.rint(adjusted_away_points))
    
    if (adjusted_home_points==adjusted_away_points) or (
        adjusted_home_points<0) or (
        adjusted_home_points==1) or (
        adjusted_away_points<0) or (
        adjusted_away_points==1):
                
                return (prediction_to_score(pred_spread, pred_total, std_spread, std_total))
    
    else:
        return f'Away Points: {adjusted_away_points}, Home_Points: {adjusted_home_points}'




#added here to avoid issues with calling functions.
def Simulate(g,i,c,y,st_dev):
    """Simulates a single week college season using the principles of Swiss-like
    pairing with Minimum Weight Matching Algorithm. Function make pairings,
    simulate games and insert those games on CollegeFootball.db database.

    Args:
        g (Networkx Graph): Graph with the teams as vertices and time distances as edges.
        i (int): Round number.
        c (np.array): Current data with #-wins and #-home_games.
        y (int): Year of the simulation.
        st_dev ([float,float]): Standard Deviation of both spread and totalpts
    """
    #loading machine learning model:
    prediction_model  = tf.keras.models.load_model("CFBprediction.h5")
    
    #associating teams by number
    config = cfbd.Configuration()
    config.api_key['Authorization'] = '3WCU5V2X05Rvh60ZxUG8FarJN4s2D1lcd2c2r6Kz/qL1Y3tVBJtWsuNATnzHRV2h'
    config.api_key_prefix['Authorization'] = 'Bearer'
    api_instance_simul= cfbd.TeamsApi(cfbd.ApiClient(config))
    conf = {'ACC','American Athletic','Big 12','Big Ten','Conference USA',
    'FBS Independents','Mid-American','Mountain West','Pac-12','SEC','Sun Belt'}
    team_id = get_team_locations(api_instance=api_instance_simul,conferences=conf)
    team_id = team_id[team_id.team != "Hawai'i"]
    team_id = team_id[team_id.team != "Jacksonville State"]
    team_id = team_id[team_id.team != "Sam Houston State"]
    team_id = team_id[team_id.team != "James Madison"]
    team_id = team_id[team_id.team != "Liberty"]
    team_id = team_id[team_id.team != "Coastal Carolina"]
    team_id = team_id[team_id.team != "Charlotte"]
    team_array = np.array(team_id["team"])
    
    #create groups based on #-wins
    print("Round:",(i+1))
    groups = [] 
    for j in range(i+1):
        groups.append([x[0].astype(int) for x in c if x[1]==j])
    
    #create matchings from outside groups to inside groups.
    matchings = []
    gnum = 0
    gcount = 0
    while gcount < (i+1):
        g_group = g.subgraph(groups[gnum])
        matching_group = nx.algorithms.matching.min_weight_matching(g_group)
        s = set(groups[gnum]) - set(np.array(list(matching_group)).flatten())
        if len(s) > 0:
            for k in s:
                groups[gnum].remove(k)
                groups[(gnum+1)].append(k)
        matchings += matching_group
        gcount += 1
        
        if gcount >= (i+1):break
        
        gnum2 = i - gnum
        g_group = g.subgraph(groups[gnum2])
        matching_group = nx.algorithms.matching.min_weight_matching(g_group)
        s = set(groups[gnum2]) - set(np.array(list(matching_group)).flatten())
        if len(s) > 0:
            for k in s:
                groups[gnum2].remove(k)
                groups[(gnum2-1)].append(k)
        matchings += matching_group
        gcount += 1
        gnum += 1
        
    conn = sqlite3.connect("CollegeFootball.db")
    print(matchings)
    print(len(matchings))
    
    #for each match, run simulation and store.
    for team in matchings:
        #home and away status
        #homeval=0 means that first team is home
        #homeval=1 means that second teams is home
        
        if c[team[0],2] == c[team[1],2]:
            homeval = np.random.randint(2)
            c[team[homeval],2]+=1
        elif c[team[0],2] > c[team[1],2]:
            homeval = 1
            c[team[1],2]+=1
        else:
            homeval = 0
            c[team[0],2]+=1
        
        team0 = team_array[team[0]]
        team1 = team_array[team[1]]
        
        #obtaining data for home and away team.
        team0df = get_team_stats_from_sql(conn=conn,name=team0,year=y)
        team1df = get_team_stats_from_sql(conn=conn,name=team1,year=y)
        
        #concatenate home team first and away team second. 
        if homeval: gamedf = pd.concat([team1df,team0df])
        else: gamedf = pd.concat([team0df,team1df])
        
        #data preprocessing before model prediction
        gamedf=gamedf.reset_index(drop=True)
        gamedf=gamedf.loc[:, 'Offensive_ppa':]
        game_array = np.array(0)
        game_array = np.append(game_array,np.array(gamedf,dtype=np.float32))
        game_array = game_array.flatten()
        game_array = game_array.reshape(1,53)
        
        # simulates game score.
        gamepred = prediction_model.predict(game_array,verbose=0)
        s = prediction_to_score(gamepred[0][0],gamepred[0][1],st_dev[0],st_dev[1])
        s = s.split(",")
        homepts = int(s[1].split(": ")[1])
        awaypts = int(s[0].split(": ")[1])
        
        # registering wins on current data
        if(homepts>awaypts):
            c[team[homeval],1]+=1
        else:
            c[team[(1-homeval)],1]+=1
        
        # registering simulated game on SQL database.
        if homeval:
            register_simul_game(conn=conn,hometeam=team1,awayteam=team0,
                                homepts=homepts,awaypts=awaypts,round=(i+1),team_id = team_id)
        else:
            register_simul_game(conn=conn,hometeam=team0,awayteam=team1,
                                homepts=homepts,awaypts=awaypts,round=(i+1),team_id = team_id)
        
        # remove edge as teams can only play once with each other.
        g.remove_edges_from([(int(team[0]),int(team[1]))])
    
    conn.close()
    return


def get_team_stats_from_sql(conn,name,year):
    """_summary_

    Args:
        conn (_type_): _description_
        name (_type_): _description_
        year (_type_): _description_

    Returns:
        _type_: _description_
    """
    
    cmd=\
    f"""
    SELECT *
    FROM stats S
    WHERE S.team='{name}' AND S.season={year}
    """
    df = pd.read_sql_query(cmd,conn)
    return df

def register_simul_game(conn,hometeam,awayteam,homepts,awaypts,round,team_id):
    """Adds simulated game result to the simul_games table on SQL database.

    Args:
        conn: SQL connection to CollegeFootball.db database
        hometeam (str): Home team name
        awayteam (str): Away team name
        homepts (int): Points by home team
        awaypts (int): Points by away team
        round (int): Round number
        team_id (int): Team ID number
    """
    #creates 1-row DataFrame with result and location data.
    df = pd.DataFrame({"Week":round,"Home Team":hometeam,"Home Points":homepts,
                       "Away Team": awayteam, "Away Points":awaypts,
                       "latitude":team_id[team_id["team"]==hometeam]["latitude"],
                       "longitude":team_id[team_id["team"]==hometeam]["longitude"]})
    
    #appends DataFrame to simul_games table.
    df.to_sql("simul_games",conn,if_exists="append",index=False)
    return


def plot_teams_games(team):
    cmd=\
        f"""
        SELECT S.'Week',S.'Home Team', S.'Home Points', C.latitude, C.longitude
        FROM simul_games S
        INNER JOIN coordinates C ON S.'Home Team'=C.team
        WHERE S.'Home Team'='{team}' OR S.'Away Team'='{team}'
        """

    conn=sqlite3.connect("CollegeFootball.db")
    home_info=pd.read_sql_query(cmd,conn)
    conn.close()
    
    home_info=home_info.rename(columns={'latitude':'home_latitude','longitude':'home_longitude'})
    
    cmd=\
        f"""
        SELECT S.'Away Team', S.'Away Points', C.latitude, C.longitude
        FROM simul_games S
        INNER JOIN coordinates C ON S.'Away Team'=C.team
        WHERE S.'Home Team'='{team}' OR S.'Away Team'='{team}'
        """

    conn=sqlite3.connect("CollegeFootball.db")
    away_info=pd.read_sql_query(cmd,conn)
    conn.close()
    
    away_info=away_info.rename(columns={'latitude':'away_latitude','longitude':'away_longitude'})
    
    game_info=home_info.merge(away_info,left_index=True,right_index=True)
    
    team_loc=game_info[(game_info['Home Team']==team)][['home_latitude','home_longitude']]
    if (team_loc.empty):
        team_loc=game_info[(game_info['Away Team']== team)][['away_latitude','away_longitude']]
        
    fig=go.Figure()

    conn = sqlite3.connect("CollegeFootball.db")
    team_locations = pd.read_sql_query("SELECT * FROM coordinates",conn)
    conn.close()

    conn = sqlite3.connect("CollegeFootball.db")
    distances = pd.read_sql_query("SELECT * FROM distances",conn)
    conn.close()

    centers=[]

    home_hover_texts = []
    away_hover_texts = [] 
    for index, row in game_info[game_info['Home Team'] != team].iterrows():
        hover_text = f"Week: {row['Week']}<br>{row['Away Team']}: {row['Away Points']} AT {row['Home Team']}: {row['Home Points']}"
        home_hover_texts.append(hover_text)
        fig.add_trace(
            go.Scattergeo(
                locationmode = 'USA-states',
                lon = [row['home_longitude'], row['away_longitude']],
                lat = [row['home_latitude'], row['away_latitude']],
                mode = 'lines',
                line = dict(width = 1,color = 'red'),
                opacity=0.5,
                showlegend=False,
                hoverinfo='skip'
            
                )   
            )
        index1=team_locations[team_locations['team']==row['Home Team']].index
        index2=team_locations[team_locations['team']==row['Away Team']].index
        distance=(round(distances.iloc[index1,index2],2))
    
        fig.add_trace(go.Scattergeo(
            locationmode='USA-states',
            lon=[row['home_longitude']],
            lat=[row['home_latitude']+0.5],
            mode='text',
            text=distance,
            showlegend=False,
            hoverinfo='skip',
            textfont=dict(size=10, color='black')
            )
    
            )
    
    for index, row in game_info[game_info['Away Team'] != team].iterrows():
        hover_text = f"Week: {row['Week']}<br>{row['Away Team']}: {row['Away Points']} AT {row['Home Team']}: {row['Home Points']}"
        away_hover_texts.append(hover_text)
        fig.add_trace(
            go.Scattergeo(
                locationmode = 'USA-states',
                lon = [row['home_longitude'], row['away_longitude']],
                lat = [row['home_latitude'], row['away_latitude']],
                mode = 'lines',
                line = dict(width = 1,color = 'blue'),
                opacity=0.5,
                hoverinfo='skip',
                showlegend=False,
            
            )
            )
        index1=team_locations[team_locations['team']==row['Home Team']].index
        index2=team_locations[team_locations['team']==row['Away Team']].index
        distance=round(distances.iloc[index1,index2],2)
    
        fig.add_trace(go.Scattergeo(
            locationmode='USA-states',
            lon=[row['away_longitude']],
            lat=[row['away_latitude']+0.5],
            mode='text',
            text=distance,
            showlegend=False,
            hoverinfo='skip',
            textfont=dict(size=10, color='black')
            )
    
            )
    
    
    fig.add_trace(go.Scattergeo(
        locationmode = 'USA-states',
        lon = [team_loc.iloc[0]['home_longitude']],
        lat = [team_loc.iloc[0]['home_latitude']],
        hovertemplate=team,
        mode='markers',
        name=team,
        marker=dict(
            symbol='star',
            color='gold',
            size=20,
            )
        ))

    fig.add_trace(go.Scattergeo(
        locationmode = 'USA-states',
        lon=game_info[game_info['Home Team'] != team]['home_longitude'],
        lat=game_info[game_info['Home Team'] != team]['home_latitude'],
        hovertemplate="%{text}",
        text=home_hover_texts,
        mode='markers',
        name='Away Game',
        marker=dict(
            color='red',
            size=8
            )   
        ))

    fig.add_trace(go.Scattergeo(
        locationmode = 'USA-states',
        lon=game_info[game_info['Away Team'] != team]['away_longitude'],
        lat=game_info[game_info['Away Team'] != team]['away_latitude'],
        hovertemplate="%{text}",
        text=away_hover_texts,
        mode='markers',
        name='Home Game',
        marker=dict(
            color='blue',
            size=8
            )
        ))

    lats = pd.concat([game_info['home_latitude'], game_info['away_latitude']])
    lons = pd.concat([game_info['home_longitude'], game_info['away_longitude']])


    fig.update_geos(
        lonaxis_range=[lons.min()-3, lons.max()+3],  
        lataxis_range=[lats.min()-3, lats.max()+3],

    )


    fig.update_layout(
        title_text=f'{team} Results for Simulated Season with Driving Distances between Teams (hr)'

    )
    
    return fig
    

def show_standings(week):
    """_summary_

    Args:
        week (_type_): _description_

    Raises:
        ValueError: _description_

    Returns:
        _type_: _description_
    """
    conn = sqlite3.connect("CollegeFootball.db")
    simulation = pd.read_sql_query("SELECT * FROM simul_games",conn)

    conn.close()

    conn = sqlite3.connect("CollegeFootball.db")
    team_locations = pd.read_sql_query("SELECT * FROM coordinates",conn)

    conn.close()
    
    standings=np.zeros((len(team_locations),3),dtype=int)

    for i in range(len(simulation[simulation['Week']<=week])):
        if (simulation.loc[i]['Home Points']>simulation.loc[i]['Away Points']):
            standings[team_locations[team_locations['team']==simulation.loc[i]['Home Team']].index[0]][1]+=1
            standings[team_locations[team_locations['team']==simulation.loc[i]['Away Team']].index[0]][2]+=1
    
        elif (simulation.loc[i]['Home Points']<simulation.loc[i]['Away Points']):
            standings[team_locations[team_locations['team']==simulation.loc[i]['Away Team']].index[0]][1]+=1
            standings[team_locations[team_locations['team']==simulation.loc[i]['Home Team']].index[0]][2]+=1
    
        else:
            raise ValueError('Home Points = Away Points')
    

    standings=pd.DataFrame(standings)
    standings=standings.rename(columns={0:'Team',1:'Wins',2:'Losses'})
    standings['Team']=team_locations['team']
    standings=standings.sort_values(by=['Wins'],ascending=False)
    standings=standings.reset_index(drop=True)
    
    return standings

def team_results(team):
    """_summary_

    Args:
        team (_type_): _description_

    Returns:
        _type_: _description_
    """
    
    cmd=\
    """
    SELECT S.'Week', S.'Home Team', S.'Home Points', S.'Away Team', S.'Away Points'
    FROM simul_games S
    """
    conn = sqlite3.connect("CollegeFootball.db")

    simulation = pd.read_sql_query(cmd,conn)

    conn.close()
    
    
    team_results=simulation[(simulation['Home Team']==team) | (simulation['Away Team']==team)]
    team_results=team_results.reset_index(drop=True)
    
    for i in range(0,len(team_results)):
        s=show_standings(week=i+1)
        team_results.loc[i,'Home Team']=team_results.loc[i,'Home Team']+' ('+str(s.loc[s['Team']==team_results.loc[i,'Home Team'],'Wins'].item())+'-'+str(s.loc[s['Team']==team_results.loc[i,'Home Team'],'Losses'].item())+')'
        team_results.loc[i,'Away Team']=team_results.loc[i,'Away Team']+' ('+str(s.loc[s['Team']==team_results.loc[i,'Away Team'],'Wins'].item())+'-'+str(s.loc[s['Team']==team_results.loc[i,'Away Team'],'Losses'].item())+')'
        

    return team_results