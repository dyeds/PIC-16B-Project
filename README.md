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

4. To make the pairings we first create a weighted graph where every team has a node and there exists an edge between every two distinct teams with weight equal to the driving distance between those teams. Run this code block to make this graph.

______________________________________________________________________________________

conn = sqlite3.connect("CollegeFootball.db")
distances = pd.read_sql_query("SELECT * FROM distances",conn)
conn.close()

m_dist = np.round(np.array(distances),decimals=3)
L = []
for k in range(126):
    for j in range(126):
        if k>j: L.append((k,j,m_dist[k,j]))
        
CollegeGraph = nx.Graph()
CollegeGraph.add_weighted_edges_from(L)
curr_data = np.zeros(shape=(126,3),dtype=int)
curr_data[:,0] = np.arange(126)

______________________________________________________________________________________

Now to simulate the season, we use the 'Simulate' function from our DataFunctions file using the following code. Notice that we can change the simulation year from 2022 to any other year between 2015-2022 by editing this parameter. We can also change the number of games each team plays by changing the 'i in range(12)' to 'i in range(weeks)' where 'weeks' is the number of weeks you want. The results of all simulated games for the entire season are then stored in the 'simul_games' table of our SQL database.

______________________________________________________________________________________

for i in range(12):
    DataFunctions.Simulate(g=CollegeGraph,
                           i=i,c=curr_data,
                           y=2022,st_dev=bestdiffstd)

______________________________________________________________________________________

Note that the simulation we ran will already be stored in the 'simul_games' table in SQL. If you want to clear this simulation and replace it with your own instance, you can run the follwing code.

______________________________________________________________________________________

conn = sqlite3.connect("CollegeFootball.db")
cursor = conn.cursor()
cursor.execute("DROP TABLE simul_games")
conn.commit()
conn.close()

______________________________________________________________________________________

5. Finally we can visualize the results of our simulation using various functions saved in the DataFunctions file. To see the standings after any week in the season, call the 'show_standings' function as 'show_standings(week)' with input parameter week which you choose. To see the final schedule and results of any one specific team, call 'team_results(team)' with your specified team. To visualize a plot of the location and distance all the opponents of a specified team, call the 'team_results(team)' function with the team of your choosing. See the documentation for more info about these functions. Finally, you are welcome to create your own tables and visualizations by querying from the SQL tables, namely the 'simul_games' table. 


