import networkx as nx
import numpy as np

#  Simulate(G,i,curr_data) has to:
# 1. Split in i groups, add them in a list. 
# 2. Do the pairings in order 0,-1,1,-2,2,...
# For each pairing: Run pairing, add the unpaired teams into the next group.
# 3. Add all pairings in a list and simulate games
# 4. Store results in db

def Simulate(g,i,c):
    groups = []
    for j in range(i+1):
        groups.append([x[0].astype(int) for x in c if x[1]==j])
    
    #for ordering outside to inside
    vals = np.arange(i+1)
    vals2 = np.arange(i+1)
    vals2 = np.flip(vals2)
    vals3 = []
    i = 0
    while len(vals3)<8:
        vals3.append(vals[i])
        vals3.append(vals2[i])
        i += 1
    
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
            
    for team in matchings:
        #home and away status
        #homeval=0 means that first team is home
        #homeval=1 means that second teams is home
        
        if c[team[0],2] == c[team[1],2]:
            homeval = np.random.randomint(2)
            c[team[homeval],2]+=1
        elif c[team[0],2] > c[team[1],2]:
            homeval = 1
            c[team[1],2]+=1
        else:
            homeval = 0
            c[team[0],2]+=1
        
        #simulating match
        if(np.random.randint(2)):
            c[team[0],1]+= 1
            print(team[0],"won",team[1],"lose")
        else: 
            c[team[1],1]+= 1
            print(team[0],"lose",team[1],"won")
        
        g.remove_edge(u=team[0],v=team[1])
    
    return