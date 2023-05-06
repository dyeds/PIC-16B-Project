1. Get Football Data from CFDB API to store in SQL database.
2. Create NN model to predict scores using betting lines.
3. Verify accuracy of model using existing bettings lines and new data.
4. Get Geographical Location data for each team and store in SQL database.
5. Run simulation of season using Swiss-like system
6. Geographically display results of simulation using pyplot (or other)


Function for Games --> Dataframe
Function for Betting Lines --> Dataframe
Function for Stats --> Dataframe

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
