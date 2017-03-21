#!/usr/bin/env python
import pdb
import requests
from requests.auth import HTTPBasicAuth
from bs4 import BeautifulSoup
from datetime import datetime
from collections import defaultdict
import cPickle as pickle
import sys
import os.path
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

colors = {"MissionRescue": "#ffaa00",
        "MissionSearch": "#aaff00",
        "IncidentRescue": "#00aaff",
        "IncidentSearch": "#00ffaa",
        "Rescue": "#aa00ff",
        "Other": "#aa99ff",
        "Incident": "#ff00aa"}

def load_year_data(year = 2017):
    year_datafile = "%s.p" % year

    if os.path.isfile(year_datafile):
        missions = pickle.load(open(year_datafile, "rb"))
    else:
        site_path="https://internal.rockymountainrescue.org/miscdb/buildsummary.cgi?tp=mission&tm=%s" % year
        user="cgruenwald"
        password="redacted"
        resp = requests.get(site_path, auth=HTTPBasicAuth(user, password))
        soup = BeautifulSoup(resp.text, 'html.parser')
        missions = [[d.text for d in tr.find_all("td")] for tr in soup.find_all("table")[1].find_all("tr")]
        pickle.dump(missions, open(year_datafile, "wb"))

    return missions

def aggregate_missions(missions):
    days = defaultdict(lambda: defaultdict(int))
    hours = defaultdict(list)
    for m in filter(lambda x: len(x) > 1, missions):
        [mission_id, mission_type, mission_time_str, synopsis, resolution] = m
        mission_time = datetime.strptime(mission_time_str, "%Y-%m-%d%H:%M:%S")
        days[mission_type][mission_time.weekday()] += 1
        hours[mission_time.weekday()] += [mission_time.hour]
    return days, hours

def plot_dow(missions):
    days, _ = aggregate_missions(missions)

    fig = plt.figure()
    ax = fig.add_axes([0.1, 0.1, 0.6, 0.75])
    x = np.arange(7)

    prev = None
    for mission_type in days.iterkeys():
        mission_count = np.array([days[mission_type].get(d, 0) for d in range(7)])

        if not prev is None:
            plt.bar(x, height=mission_count, bottom=prev, facecolor=colors[mission_type], edgecolor='white', label=mission_type)
            prev += mission_count
        else:
            plt.bar(x, height=mission_count, facecolor=colors[mission_type], edgecolor='white')
            prev = mission_count

    plt.xticks(x, ['M','Tu','W', 'Th', "F", 'Sa', 'Su'])
    plt.xlim(-0.75,7)

    fig.suptitle('2016 Mission Day-of-Week Stats', fontsize=14, fontweight='bold')
    fig.subplots_adjust(top=0.85)
    #ax.set_title('axes title')

    ax.set_xlabel('Day of Week')
    ax.set_ylabel('Mission Count')

    legend_patches = [mpatches.Patch(color=v, label=k) for k, v in colors.iteritems()]
    plt.legend(handles=legend_patches, bbox_to_anchor=(1.05, 1), loc=2, borderaxespad=0.)

    plt.savefig('dow.png', dpi=48)

def plot_hod(missions):
    _, hours = aggregate_missions(missions)

    fig, ax = plt.subplots(1)

    fig.suptitle('2016 Mission Time-of-Day Stats', fontsize=14, fontweight='bold')
    fig.subplots_adjust(top=0.85)
    #ax.set_title('axes title')

    ax.set_xlabel('Day of Week')
    ax.set_ylabel('Mission Time')

    day_range = range(len(hours.keys()))
    data = [hours[k] for k in day_range]

    plt.boxplot(data)
    plt.xticks([1,2,3,4,5,6,7],
            ['M','Tu','W', 'Th', "F", 'Sa', 'Su'])
    ytics, yvals = range(24), map(lambda x: "%2d:00" % x, range(24))
    plt.yticks(ytics, yvals)
    plt.savefig('hod.png', dpi=48)

if __name__ == "__main__":
    plot_dow(load_year_data(year = 2016))
    plot_hod(load_year_data(year = 2016))
