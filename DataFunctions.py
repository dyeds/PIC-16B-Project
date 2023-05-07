import pandas as pd
import numpy as np


def get_fbs_games(api_instance,year):
    gamelist = api_instance.get_games(year=year,division='fbs')
    
    gamelist = [game for game in gamelist if (game.home_division==game.away_division=="fbs" 
                                                and game.completed==True)]
    return gamelist

def df_from_games(gamelist):
    gamelist = [str(game).split("\n") for game in gamelist]
    gamelist = [[s[2:-1] for s in game] for game in gamelist]
    gamelist = [[s.replace("'","").split(": ") for s in game] for game in gamelist]
    gamelist = [{s[0]:s[1] for s in game} for game in gamelist]
    gamemetrics = ['away_conference','away_id','away_points','away_team',
                   'home_conference','home_id','home_points','home_team',
                   'id', 'season','neutral_site']
    gamelist = [{x:game[x] for x in game if x in gamemetrics} for game in gamelist]
    
    df = pd.DataFrame(gamelist)
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
            if game['lines'][i]['formatted_spread'][:away_length+2]==(game['away_team']+' -'):
                game_lines.append(float(game['lines'][i]['formatted_spread'][away_length+1:]))
            
            elif game['lines'][i]['formatted_spread'][:home_length+2]==(game['home_team']+' -'):
                game_lines.append(abs(float(game['lines'][i]['formatted_spread'][home_length+1:])))
        
            over_unders.append(game['lines'][i]['over_under'])
            
        game['av_spread']=np.mean(game_lines)
        game['av_total']=np.mean(over_unders)
        
    df = pd.DataFrame(betting_lines)[['id','av_spread','av_total']]
    return df

    
    


