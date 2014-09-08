#!/usr/bin/env python
# -*- coding: utf-8 -*-
""" Create kicker rank statistics using Microsoft's TrueSkill
    
The scores are stored in .tsc files within the scripts directory.
Every file ending with .tsc will be considered. For each file a
separate plot will  be created. The .tsv files are sorted according
to their names and are consecutively processed. If a player has been
played before, he will inherit its score from previous .tsc files.

"""

from __future__ import division

import csv
from matplotlib import cm
import matplotlib.pyplot as plt
import numpy as np
import os
import trueskill
import IPython



def create_plot_data(timeline, length=None):
    """
        From a timeline (see get_timeline), get the plotting data for
        all players.
        Returns: - list of [arr(i), arr(mu), arr(sigma)] for plotting
                   with matplotlib where i goes from 1 to total number of games
                   played.
                 - labels (player names)
    """
    plotlabels = list()
    labels = timeline[-1].keys()
    labels.sort()
    plotdata = list()
    # add zero at beginning

    start = 0
    stop = len(timeline)
    if length is not None:
        start += stop - length -1

    for label in labels:
        mu = list()
        sigma = list()

        for i in range(stop):
            try:
                mu.append(timeline[i][label].mu)
                sigma.append(timeline[i][label].sigma)
            except KeyError:
                mu.append(0)
                sigma.append(0)
        
        plotdata.append([np.arange(stop-start)+start+1,
                         np.array(mu)[start:stop],
                         np.array(sigma)[start:stop]])
                         
        plotlabels.append(u"{}   {:.1f}".format(label,mu[stop-1]))
    
    return plotdata, plotlabels


def eval_data(data):
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


def eval_step(players, data):
    """
        Using TrueSkill, compute every players current skill and std.
    """
    # Iterate through data and make a dictionary of Players
    #players = dict()
    for game in data:
        team1 = game[0]
        for player in team1:
            if player not in list(players.keys()):
                players[player] = trueskill.Rating(0,25)
        team2 = game[1]
        for player in team2:
            if player not in list(players.keys()):
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




def get_timeline(data):
    """
        Get the player history for all players.
        Input: Data from load_tsv
        Returns: Time line (list) containing dictionaries of player stats.
                 e.g.: starting point of time line and mu/sigma of player A:
                 timeline[0]["A"].mu
                 timeline[0]["A"].sigma
    """
    timeline = list()
    newdata = list()
    players = dict()
    for item in data:
        newdata = [item]
        #players = eval_data(newdata)
        
        players = eval_step(players,newdata)
        timeline.append(players.copy())
        #import IPython
        #IPython.embed()
        ##
        ## here we need to check if we want to penalize
        timeline = penalize_timeline(timeline)
        players = timeline[-1].copy()
        #import IPython
        #IPython.embed()
        #print(item)
        
    return timeline


def import_folder(DIR):
    """ 
    Get all information from the current folder and return a timeline
    for each .tsv file.
    """
    files = os.listdir(DIR)
    files.sort()
    tsvfiles = list()
    for f in files:
        if f.endswith(".tsv"):
            tsvfiles.append(os.path.realpath(os.path.join(DIR,f)))
    
    data = list()
    timelinelist = list()
    
    for tf in tsvfiles:
        data += load_tsv(tf)
        timelinelist.append([tf, get_timeline(data)])
        
    return timelinelist


def load_tsv(filename):
    """
        Load kicker data from tsv file (see examplestat.tsv).
    """
    csvfile = open(filename, 'r')
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
            team1 = [pl.strip() for pl in team1]
            team2 = [pl.strip() for pl in team2]
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


def join_timelines(timelines):
    """ Returns one timeline from a list of timelines """
    timeline = list()
    for i in range(len(timelines)):
        timeline += timelines[i][1]
    return ["Full Timeline", timeline]



def separate_timeline(timeline, oldtimelines):
    """ Returns one timeline from a list of timelines """
    timelines = list()
    count = 0
    for i in range(len(oldtimelines)):
        add = len(oldtimelines[i][1])
        timelines += [[oldtimelines[i][0], timeline[1][count:count+add]]]
        count += add
    return timelines


def penalize_timeline(timeline, missed_games=10, penalty=.10):
    """ If a player hasn't played `missed_gamse`, then he will
        get a `penalty` towards zero that will be distributed between
        all other players that did play during that period.
        
        This introduces inflation.
    """
    games = timeline
    N = len(games)
    for i in range(missed_games+1, N):
        # each element from time line contains a dictionary whose
        # keys are the players and whose values are TS ratings.
        # r = trueskill.rating(mu=mu, sigma=sigma)
        
        # find players who haven't played:
        allplayers = games[i].keys()
        players = list()
        for p in list(allplayers):
            for j in range(1,missed_games):
                try:
                    if (games[i-j][p].mu - games[i][p].mu != 0):
                        players.append(p)
                except KeyError:
                    # player did not exist -> add as player.
                    players.append(p)
        
        a=np.array(allplayers)
        b=np.array(players)
        haters = list(np.lib.arraysetops.setdiff1d(a,b))
        for h in haters:
            sk = games[i][h]
            mudiff = sk.mu*(penalty)
            games[i][h] = trueskill.Rating(mu=sk.mu-mudiff,
                                           sigma=sk.sigma)
            lp = len(players)
            for p in players:
                psk = games[i][p]
                # Using abs here introduces inflation!
                games[i][p] = trueskill.Rating(mu=psk.mu+abs(mudiff/lp),
                                               sigma=psk.sigma)
    return games
            
        
            
# Define directory and files
#DIR="./"
#filename="examplestat.tsv"
## import data
#data = load_tsv(os.path.join(DIR, filename))
## create timeline
#timeline = get_timeline(data)
## get plotting information (Game,Skill,Skill_err)
#plotdata, labels = create_plot_data(timeline)

DIR = os.path.dirname(os.path.realpath(__file__))

timelines = import_folder(DIR)

## Add penalty
#timeline = join_timelines(timelines)
#timelinepen = penalize_timeline(timeline)
#timelines2 = separate_timeline(timeline, timelines)

#import IPython
#IPython.embed()

plots = list()

for i in range(len(timelines)):
    print(i)
    if i == 0:
        length = None
    else:
        length = len(timelines[i][1]) - len(timelines[i-1][1])
    plots.append([timelines[i][0], 
                  create_plot_data(timelines[i][1], length=length)])


for p in plots:
    # Plot data
    fig=plt.figure()

    plotdata, labels = p[1]
    splt = plt.subplot(111)
    cmap = cm.get_cmap("hsv")

    # Get thickness of lines
    thickness = np.zeros(len(labels))
    for k in xrange(len(labels)):
        thickness[k] = len(np.unique(plotdata[k][1]))
    thickness *= 4/thickness.max()

    for k in xrange(len(labels)):
        color = cmap(1.*k/(len(labels)))
        #plt.errorbar(plotdata[k][0], plotdata[k][1], yerr=plotdata[k][2], color=color)
        plt.plot(plotdata[k][0], plotdata[k][1], color=color,
                 label=labels[k], linewidth=thickness[k])

    splt.yaxis.set_label_position("right")
    splt.yaxis.set_ticks_position("right")
    #plt.xticks(np.arange(len(timeline)/2)+.5, np.arange(len(timeline)/2)+1)
    plt.ylabel('Skill',size='x-large')
    plt.xlabel('Game',size='x-large')
    #plt.legend(labels, loc=3, fancybox=True)
    box = splt.get_position()
    splt.set_position([box.x0 + box.width * 0.10, box.y0,
                     box.width* 0.90, box.height])
    plt.legend(loc='upper center', 
               bbox_to_anchor=(-0.18, 1.01),
               prop={'size':9})
    plt.grid(linestyle='--', linewidth=1, color="gray")
    #plt.tight_layout()
    splt.set_xlim((plotdata[k][0].min(), plotdata[k][0].max()))
    plt.savefig('{}_KickerScore.png'.format(p[0]))


