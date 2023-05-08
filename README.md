1. Get Football Data from CFDB API to store in SQL database.
2. Create NN model to predict scores using betting lines.
3. Verify accuracy of model using existing bettings lines and new data.
4. Get Geographical Location data for each team and store in SQL database.
5. Run simulation of season using Swiss-like system
6. Geographically display results of simulation using pyplot (or other)


Function for Games --> Dataframe

Function for Betting Lines --> Dataframe:
-- Negative betting line: away team favored
-- Want columns for Game ID, spread, over-under both averaged across all lines

Function for Stats --> Dataframe



Season stats we may want:  (May have to average)


-- ['Offensive ppa','Offensive success_rate','Offensive explosiveness','Offensive power_success','Offensive stuff_rate','Offensive line_yards','Defensive ppa','Defensive success_rate','Defensive explosiveness','Defensive power_success','Defensive stuff_rate',
'Defensive line_yards','Offensive havoc total','Offensive rushing_plays ppa','Offensive rushing_plays success_rate','Offensive rushing_plays explosiveness','Offensive passing_plays ppa', 'Offensive passing_plays success_rate','Offensive passing_plays explosiveness','Defensive havoc total','Defensive rushing_plays ppa','Defensive rushing_plays success_rate','Defensive rushing_plays explosiveness','Defensive passing_plays ppa','Defensive passing_plays success_rate','Defensive passing_plays explosiveness']


Note: we need to add some sort of strength of schedule component
we can do it using Team Record and adding up the team record of the opponents

Offensive:
Points scored per game
PPA
Havoc (against)
Yards per game



Defensive:
Points allowed per game
Havoc
Yards allowed per game
PPA

[
  {
    "season": 0,
    "team": "string",
    "conference": "string",
    "offense": {
      "plays": 0,
      "drives": 0,
      "ppa": 0,
      "totalPPA": 0,
      "successRate": 0,
      "explosiveness": 0,
      "powerSuccess": 0,
      "stuffRate": 0,
      "lineYards": 0,
      "lineYardsTotal": 0,
      "secondLevelYards": 0,
      "secondLevelYardsTotal": 0,
      "openFieldYards": 0,
      "openFieldYardsTotal": 0,
      "totalOpportunies": 0,
      "pointsPerOpportunity": 0,
      "fieldPosition": {
        "averageStart": 0,
        "averagePredictedPoints": 0
      },
      "havoc": {
        "total": 0,
        "frontSeven": 0,
        "db": 0
      },
      "standardDowns": {
        "rate": 0,
        "ppa": 0,
        "successRate": 0,
        "explosiveness": 0
      },
      "passingDowns": {
        "rate": 0,
        "ppa": 0,
        "successRate": 0,
        "explosiveness": 0
      },
      "rushingPlays": {
        "rate": 0,
        "ppa": 0,
        "totalPPA": 0,
        "successRate": 0,
        "explosiveness": 0
      },
      "passingPlays": {
        "rate": 0,
        "ppa": 0,
        "totalPPA": 0,
        "successRate": 0,
        "explosiveness": 0
      }
    },
    "defense": {
      "plays": 0,
      "drives": 0,
      "ppa": 0,
      "totalPPA": 0,
      "successRate": 0,
      "explosiveness": 0,
      "powerSuccess": 0,
      "stuffRate": 0,
      "lineYards": 0,
      "lineYardsTotal": 0,
      "secondLevelYards": 0,
      "secondLevelYardsTotal": 0,
      "openFieldYards": 0,
      "openFieldYardsTotal": 0,
      "totalOpportunies": 0,
      "pointsPerOpportunity": 0,
      "fieldPosition": {
        "averageStart": 0,
        "averagePredictedPoints": 0
      },
      "havoc": {
        "total": 0,
        "frontSeven": 0,
        "db": 0
      },
      "standardDowns": {
        "rate": 0,
        "ppa": 0,
        "successRate": 0,
        "explosiveness": 0
      },
      "passingDowns": {
        "rate": 0,
        "ppa": 0,
        "successRate": 0,
        "explosiveness": 0
      },
      "rushingPlays": {
        "rate": 0,
        "ppa": 0,
        "totalPPA": 0,
        "successRate": 0,
        "explosiveness": 0
      },
      "passingPlays": {
        "rate": 0,
        "ppa": 0,
        "totalPPA": 0,
        "successRate": 0,
        "explosiveness": 0
      }
    }
  }
]
