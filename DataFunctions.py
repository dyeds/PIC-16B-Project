import pandas as pd
import numpy as np
import networkx as nx
import tensorflow as tf
import cfbd
import sqlite3


def get_fbs_games(api_instance,year):
    gamelist = api_instance.get_games(year=year,division='fbs')
    
    gamelist = [game for game in gamelist if (game.home_division==game.away_division=="fbs" 
                                                and game.completed==True)]
    return gamelist

def df_from_games(gamelist):
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
    betting_info=api_instance.get_lines(year=year)
    
    betting_info=[game for game in betting_info if (game.away_conference in conferences
                                                    and game.home_conference in conferences)] 
    return betting_info

def df_betting_lines(betting_info):
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
        
    df = pd.DataFrame(betting_lines)[['id','av_spread','av_total']]
    return df

# not using this bc its 1 line of code
# def get_team_advstats(api_instance,year):
#     teamstats = api_instance.get_advanced_team_season_stats(year=year)
#     return teamstats

def word_adder(word,dict):
    word=word+"_"
    new_dict={}
    for key,value in dict.items():
        new_key = f"{word}{key}"
        new_dict[new_key] = value
    return new_dict

def word_adder2(dict):
    updaterkeys = []
    for key,value in dict.items():
        if type(value)==type(dict):
            updaterkeys.append([key,value])
    
    for i in range(len(updaterkeys)):
        dict.update(word_adder(word=updaterkeys[i][0],dict=updaterkeys[i][1]))
        dict.pop(updaterkeys[i][0])
    return dict

def df_team_advstats(teamstats):
    teamstats = [{**{'team':t.team,'season':t.season,'conference':t.conference},
                **word_adder(word="Offensive",dict=t.offense.to_dict()),
                **word_adder(word="Defensive",dict=t.defense.to_dict())} for t in teamstats]
    
    teamstats = [word_adder2(t) for t in teamstats]
    df = pd.DataFrame(teamstats)
    df = df.drop('Defensive_passing_plays_total_ppa',axis=1)
    #missing: which columns to work with
    return df

def df_stats_needed(df,col):
    df = df[col]
    return df

def get_team_locations(api_instance,conferences):
    team_info=api_instance.get_teams()
    team_info[0]
    team_info=[[team.school,team.id,team.location.latitude,
                team.location.longitude] for team in team_info if (team.conference in conferences)]
    locations=pd.DataFrame(team_info)
    locations=locations.rename(columns={0:'team',1:'id',2:'latitude',3:'longitude'})
    
    return locations


def prediction_to_score(pred_spread,pred_total,std_spread,std_total):
    
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
    team_id = team_id[team_id.team != "Hawai'i"
                      or team_id.team != "Jacksonville State"
                      or team_id.team != "Sam Houston State"]
    team_array = np.array(team_id["team"])
    
    print("Round:",(i+1))
    groups = [] 
    for j in range(i+1):
        groups.append([x[0].astype(int) for x in c if x[1]==j])
    
    #for ordering outside to inside
    vals = np.arange(i+1)
    vals2 = np.flip(vals)
    vals3 = []
    
    for h in range(i+1):
        if len(vals3)>=(i+1):break
        vals3.append(vals2[h])
        if len(vals3)>=(i+1):break
        vals3.append(vals[h])
    
    vals3 = np.array(vals3)
    matchings = []
    
    for j in vals3:
        if set(groups[j])==set():
            continue
        g_group = g.subgraph(groups[j])
        matching_group = nx.algorithms.matching.min_weight_matching(g_group)
        s = set(groups[j]) - set(np.array(list(matching_group)).flatten())
        if s!=set():
            for k in s:
                groups[j].remove(k)
                if j > vals3[-1]:
                    groups[j-1].append(k)
                elif j < vals3[-1]:
                    groups[j+1].append(k)
        
        matchings += matching_group
        del matching_group
    
    conn = sqlite3.connect("CollegeFootball.db")
    
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
        
        team0df = get_team_stats_from_sql(conn=conn,name=team0,year=y)
        team1df = get_team_stats_from_sql(conn=conn,name=team1,year=y)
        
        if homeval: gamedf = pd.concat([team1df,team0df])
        else: gamedf = pd.concat([team0df,team1df])
        
        gamedf=gamedf.reset_index(drop=True)
        gamedf=gamedf.loc[:, 'Offensive_ppa':]
        game_array = np.array(0)
        game_array = np.append(game_array,np.array(gamedf,dtype=np.float32))
        game_array = game_array.flatten()
        game_array = game_array.reshape(1,53)
        
        gamepred = prediction_model.predict(game_array)
        s = prediction_to_score(gamepred[0][0],gamepred[0][1],st_dev[0],st_dev[1])
        s = s.split(",")
        homepts = int(s[0].split(": ")[1])
        awaypts = int(s[1].split(": ")[1])
        
        if(homepts>awaypts):
            c[team[homeval]]+=1
        else:
            c[team[(1-homeval)]]+=1
        
        if homeval:
            register_simul_game(conn=conn,hometeam=team1,awayteam=team0,
                                homepts=homepts,awaypts=awaypts,round=(i+1),team_id = team_id)
        else:
            register_simul_game(conn=conn,hometeam=team0,awayteam=team1,
                                homepts=homepts,awaypts=awaypts,round=(i+1),team_id = team_id)
        
        g.remove_edge(u=team[0],v=team[1])
    
    conn.close()
    
    return   
     


def get_team_stats_from_sql(conn,name,year):
    cmd=\
    f"""
    SELECT *
    FROM stats S
    WHERE S.team='{name}' AND S.season={year}
    """
    df = pd.read_sql_query(cmd,conn)
    return df

def register_simul_game(conn,hometeam,awayteam,homepts,awaypts,round,team_id):
    df = pd.DataFrame({"Week":round,"Home Team":hometeam,"Home Points":homepts,
                       "Away Team": awayteam, "Away Points":awaypts,
                       "latitude":team_id[team_id["team"]==hometeam]["latitude"],
                       "longitude":team_id[team_id["team"]==hometeam]["longitude"]})
    df.to_sql("simul_games",conn=conn,if_exists="append",index=False)
    return