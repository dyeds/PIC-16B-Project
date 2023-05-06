def get_fbs_games(api_instance,year):
    gameslist = api_instance.get_games(year=year,division='fbs')
    
    gameslist = [game for game in gameslist if (gameslist[i].home_division==gameslist[i].away_division=="fbs" 
                                                and gameslist[i].completed==True)]
    
    # i = 0
    # while i < len(gameslist):
    #     if(gameslist[i].home_division==gameslist[i].away_division=="fbs" 
    #        and gameslist[i].completed==True
    #        and gameslist[i].neutral_site==False):
    #         i+=1
    #         continue
    #     else:
    #         gameslist.remove(gameslist[i])
    return gameslist