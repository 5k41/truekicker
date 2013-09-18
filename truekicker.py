#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
    Create kicker rank statistics using Microsoft's TrueSkill
"""

import csv
import os
import trueskill
import IPython

def os_load_tsv(DIR, filename):
    """
        Load kicker data from tsv file (see examplestat.tsv).
    """
    csvfile = open(os.path.join(DIR, filename), 'r')
    readdata = csv.reader(csvfile, delimiter='\t')
    data = list()
    for row in readdata:
        if len(row) == 0 or len(str(row[0]).strip()) == 0:
            # Do nothing with empty/whitespace lines
            pass
        elif str(row[0])[0:1] != '#':
            # A,B C,D 2,1
            team1 = row[0].split(",")
            team2 = row[1].split(",")
            N1 = int(row[2].split(",")[0])  # team1 wins
            N2 = int(row[2].split(",")[1])  # team2 wins
            # The first team in the list is the winner
            for i in range(N1):
                data.append([team1, team2])
            for j in range(N2):
                data.append([team2, team1])
    return data

def math_eval_data(data):
    """
        Using TrueSkill, compute every players current skill and std.
    """
    # Iterate through data and make a dictionary of Players
    players = dict()
    for game in data:
        team1 = game[0]
        for player in team1:
            players[player] = trueskill.Rating(50,25)
        team2 = game[1]
        for player in team2:
            players[player] = trueskill.Rating(50,25)     
    # Compute true skill for each player
    for game in data:
        team1 = game[0]
        Rgroup1 = list()
        for player in team1:
            Rgroup1.append(players[player])
        team1 = game[0]
        Rgroup2 = list()
        for player in team2:
            Rgroup2.append(players[player])
        # Rate the groups
        # team1 won
        wing, loseg = trueskill.rate([Rgroup1, Rgroup2], ranks=[0,1])
        # Write back te rank to the players dictionary
        for i in range(len(team1)):
            player = team1[i]
            players[player] = wing[i] 
        for i in range(len(team2)):
            player = team2[i]
            players[player] = loseg[i]
    return players

DIR="./"
filename="examplestat.tsv"

data = os_load_tsv(DIR, filename)

players = math_eval_data(data)

IPython.embed()
