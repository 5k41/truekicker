#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
    Create kicker rank statistics using Microsoft's TrueSkill
"""

import csv
from matplotlib import cm
import matplotlib.pyplot as plt
import numpy as np
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
            # remove spaces:
            for i in range(len(team1)):
                team1[i] = team1[i].strip()
            for i in range(len(team2)):
                team2[i] = team2[i].strip()
            N1 = int(row[2].split(",")[0])  # team1 wins
            N2 = int(row[2].split(",")[1])  # team2 wins
            # The first team in the list is the winner
            # Find drawn games:
            for i in range(min(N1,N2)):
                data.append([team1, team2, [0,0]])
            for i in range(abs(N2-N1)):
                if N1 > N2:
                    ranks = [0,1]
                else:
                    ranks = [1,0]
                data.append([team1, team2, ranks])
            #for i in range(N1):
            #    data.append([team1, team2], [)
            ##for j in range(N2):
            #    data.append([team2, team1])
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
            players[player] = trueskill.Rating(0,25)
        team2 = game[1]
        for player in team2:
            players[player] = trueskill.Rating(0,25)     
    # Compute true skill for each player
    for game in data:
        team1 = game[0]
        Rgroup1 = list()
        for player in team1:
            Rgroup1.append(players[player])
        team2 = game[1]
        Rgroup2 = list()
        for player in team2:
            Rgroup2.append(players[player])
        # Rate the groups
        # team1 won
        wing, loseg = trueskill.rate([Rgroup1, Rgroup2], ranks=game[2])
        # Write back te rank to the players dictionary
        for i in range(len(team1)):
            player = team1[i]
            players[player] = wing[i]
        for i in range(len(team2)):
            player = team2[i]
            players[player] = loseg[i]
    return players


def math_get_timeline(data):
    """
        Get the player history for all players.
        Input: Data from os_load_tsv
        Returns: Time line (list) containing dictionaries of player stats.
                 e.g.: starting point of time line and mu/sigma of player A:
                 timeline[0]["A"].mu
                 timeline[0]["A"].sigma
    """
    timeline = list()
    newdata = list()
    for item in data:
        newdata += [item]
        players = math_eval_data(newdata)
        timeline.append(players)
    return timeline
    

def math_create_plot_data(timeline):
    """
        From a timeline (see math_get_timeline), get the plotting data for
        all players.
        Returns: - list of [arr(i), arr(mu), arr(sigma)] for plotting
                   with matplotlib where i goes from 1 to total number of games
                   played.
                 - labels (player names)
    """
    labels = timeline[-1].keys()
    labels.sort()

    # TODO:
    # sort labels according to timeline[-1][label].mu

    plotdata = list()
    for l in range(len(labels)):
        label = labels[l]
        labels[l] = "{} {:2.0f}".format(label, timeline[-1][label].mu)
        mu = list()
        sigma = list()
        for i in xrange(len(timeline)):
            if label in timeline[i].keys():
                mu.append(timeline[i][label].mu)
                sigma.append(timeline[i][label].sigma)
            else:
                mu.append(0)
                sigma.append(0)
        plotdata.append([np.arange(len(timeline))/2., np.array(mu), np.array(sigma)])
    return plotdata, labels
            


# Define directory and files
DIR="./"
filename="kicker1.txt"
# import data
data = os_load_tsv(DIR, filename)
# create timeline
timeline = math_get_timeline(data)
# get plotting information (Game,Skill,Skill_err)
plotdata, labels = math_create_plot_data(timeline)

# Plot data
splt = plt.subplot(111)
cmap = cm.get_cmap("hsv")
for k in xrange(len(labels)):
    color = cmap(1.*k/(len(labels)))
    plt.errorbar(plotdata[k][0], plotdata[k][1], yerr=plotdata[k][2], color=color)

splt.yaxis.set_label_position("right")
splt.yaxis.set_ticks_position("right")
plt.xticks(np.arange(len(timeline)/2)+.5, np.arange(len(timeline)/2)+1)
plt.ylabel('Skill',size='x-large')
plt.xlabel('Game',size='x-large')
plt.legend(labels, loc=3, fancybox=True)
plt.grid(linestyle='--', linewidth=1, color="gray")
plt.savefig('KickerScore.png')

