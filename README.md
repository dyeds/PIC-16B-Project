Creating a simulation of a college football season from 2015-2022 based on team season statistics using a different pairing system. This new pairing system uses team win-loss record to group teams and then pairs teams within each group while minimizing the distances between paired teams. This file contains instructions for users to view or recreate our simulation. If you recreating the entire simulation, we suggest reading the Final Report writeup to find all the code to run.  

1. First import the DataFunctions.py file from the GitHub, as you will need these functions, and download the CollegeFootball.db database from the GitHub unless you are recreating the entire simulation for yourself. 

2. If you've downloaded the database from the GitHub, all the team season statistics data and betting lines data for the model is stored in this SQL database, as well as the team location coordinates and driving distances between teams. At this point, you need to run the following preprocessing code to get the dataframes 'parameters_df' and 'predict_betting_df', which are the predictor variables dataframe and target variables dataframe to use in the model. This code can also be found in more detail in the Final Report.

______________________________________________________________________________________

conn = sqlite3.connect("CollegeFootball.db")
games_df = pd.read_sql_query("SELECT * FROM games",conn)
betting_df = pd.read_sql_query("SELECT * FROM betting_lines",conn)

conn.close()

cols = ['team','season','conference','Offensive_ppa','Offensive_success_rate',
        'Offensive_explosiveness','Offensive_power_success',
        'Offensive_stuff_rate','Offensive_line_yards',
        'Defensive_ppa','Defensive_success_rate',
        'Defensive_explosiveness','Defensive_power_success',
        'Defensive_stuff_rate','Defensive_line_yards',
        'Offensive_havoc_total','Offensive_rushing_plays_ppa',
        'Offensive_rushing_plays_success_rate',
        'Offensive_rushing_plays_explosiveness',
        'Offensive_passing_plays_ppa',
        'Offensive_passing_plays_success_rate',
        'Offensive_passing_plays_explosiveness',
        'Defensive_havoc_total','Defensive_rushing_plays_ppa',
        'Defensive_rushing_plays_success_rate',
        'Defensive_rushing_plays_explosiveness',
        'Defensive_passing_plays_ppa',
        'Defensive_passing_plays_success_rate',
        'Defensive_passing_plays_explosiveness']

gcols = games_df.columns
gstr = ""
for c in gcols:
    gstr += "G."+str(c)+","

bcols = betting_df.columns
bstr = ""
for b in bcols:
    bstr += "B."+str(b)+","
bstr = bstr[5:]

s1 = ""
for c in cols:
   s1 += "S1." + str(c) +  " AS Home_" + str(c) + ", "
s1 = s1[:-1]

s2 = ""
for c in cols:
   s2 += "S2." + str(c) +  " AS Away_" + str(c) + ", "
s2 = s2[:-2]

cmd=\
f"""
SELECT {str(gstr)} {str(bstr)} {str(s1)} {str(s2)}
FROM games G
INNER JOIN betting_lines B ON G.id=B.id
INNER JOIN stats S1 ON S1.team=G.home_team
INNER JOIN stats S2 ON S2.team=G.away_team
WHERE (S2.season=G.season AND S1.season=G.season)
"""

conn=sqlite3.connect("CollegeFootball.db")
df_merged=pd.read_sql_query(cmd,conn)
conn.close() 

parameters_df=df_merged.drop(['id','season', 'home_id', 'home_team',
       'home_conference', 'home_points', 'away_id', 'away_team',
       'away_conference', 'away_points', 'game_spread', 'game_totalpts',
       'av_spread', 'av_total'], axis=1)

predict_betting_df=df_merged[['av_spread','av_total','id']]

______________________________________________________________________________________


Otherwise if you are recreating it yourself, refer to the code in the "Data Acquisition and Preprocessing" section of the Final Report. You can edit the API instances if you want to change the teams used in the simulation, say from 'FBS' teams to 'FCS' teams, or the years worth of data to collect.

3. If you want to use our tensorflow model for the simulation, you can find it as CFBprediction.h5 in the GitHub. Below is our code for the model, you may also choose to edit layers and experiment with your own version of it. If you choose to do this, refer to the "Predictive Model using Tensorflow" section of the Final Report to find all the necessary code to run with it. 

______________________________________________________________________________________

model = tf.keras.models.Sequential([
    layers.Dense(100,input_shape=(X_train.shape[1],),activation='relu'),
    layers.Dense(100,activation='relu'),
    layers.Dense(2)
])

______________________________________________________________________________________

4. 



