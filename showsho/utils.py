# Showsho
# Copyright (C) 2015  Dino Duratović <dinomol@mail.com>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import datetime
import json
import urllib.request
import os

# used for urllib requests
HEADER = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:40.0)"}

# used to disable colored text on Windows
OS = os.name

class Color:
    GREEN = "\033[32m"
    RED = "\033[31m"
    L_GREEN = "\033[1;32m"
    L_BLUE = "\033[1;34m"
    L_RED = "\033[1;31m"

def colorize(text, color):
    # doesn't output colored text on Windows(tm)(c)
    if OS == "nt":
        return text
    else:
        return "{}{}\033[0m".format(color, text)

def getDateObject(date_string):
    # returns a date object for the given date string
    yyyy, mm, dd = date_string.split("-")
    date_object = datetime.date(int(yyyy), int(mm), int(dd))
    return date_object

def getDay(date_object):
    # returns the day's name of a date object: Monday, Tuesday, etc
    return date_object.strftime("%A")

def getPrettyDate(date_object):
    # returns a string from a date object in the format Day, MM-YYYY
        return date_object.strftime("%a, %d %b %Y")

def formatNumber(number):
    # adds a leading zero to the episode/season if necessary
    if len(str(number)) == 1:
        return "0{}".format(number)
    else:
        return str(number)

def verifyDate(date):
    # returns True if a date is in the valid format: YYYY-MM-DD
    try:
        getDateObject(date)
        return True
    except (TypeError, AttributeError, ValueError):
        return False

def validateNumber(length):
    # returns a number, with input validation for a range;
    while True:
        choice = input(">")
        if choice.isdigit() and int(choice) in range(length):
            return int(choice)
        print("Invalid choice, must enter a number, try again.")

def verifyData(season, date, episodes):
    # checks if a show's data (from the JSON file) is valid
    valid_season = False
    valid_date = False
    valid_episodes = False

    # season must be a number
    if str(season).isdigit():
        valid_season = True

    # the date must be in the proper format or None;
    # if a date is set, the episodes number must also be set
    if verifyDate(date) and str(episodes).isdigit():
        valid_date = True
        valid_episodes = True
    # unless they're both unknown (None), which is also acceptable
    elif (date == None) and (episodes == None):
        valid_date = True
        valid_episodes = True

    if valid_season and valid_date and valid_episodes:
        return True

def showInfo(show):
    # returns a string with the show's details for printing
    if show.status == "airing":
        info = "{}\nS{}E{} | {}".format(
            colorize(show.title, Color.L_GREEN),
            formatNumber(show.season),
            formatNumber(show.current_episode),
            getDay(show.premiere)
            )

    elif show.status == "airing_new":
        info = "{} {}\nS{}E{} | {}".format(
            colorize(show.title, Color.L_GREEN),
            colorize("New episode!", Color.L_BLUE),
            formatNumber(show.season),
            formatNumber(show.current_episode),
            getDay(show.premiere)
            )

    elif show.status == "airing_last":
        info = "{} {}\nS{}E{} | {}".format(
            colorize(show.title, Color.L_GREEN),
            colorize("Last episode!", Color.L_RED),
            formatNumber(show.season),
            formatNumber(show.current_episode),
            getDay(show.premiere)
            )

    elif show.status == "ended":
        info = "{}\nLast episode: S{}E{}".format(
            colorize(show.title, Color.RED),
            formatNumber(show.season),
            formatNumber(show.episodes),
            )

    elif show.status == "soon":
        info = "{}\nSeason {} premiere on {}".format(
            colorize(show.title, Color.GREEN),
            show.season,
            getPrettyDate(show.premiere)
            )

    elif show.status == "unknown":
        info = "{}\nSeason {} unknown premiere date".format(
            show.title,
            show.season
            )

    return info

def getTorrents(show):
    # returns a list with a dict for the top 5 torrents of a show
    source = "https://getstrike.net/api/v2/torrents/search/?phrase="
    search = "{}%20s{}e{}".format(
        show.title.replace(" ", "%20"),
        formatNumber(show.season),
        formatNumber(show.current_episode)
        )
    url = "{}{}".format(source, search)

    # modified request header, because it won't work with python's UA
    req = urllib.request.Request(url, headers=HEADER)

    try:
        # TODO: find out if it's possible to get JSON without converting
        #       it to a string first and then loading it
        site = urllib.request.urlopen(req).read()
        # removes the first 2 and last strings: b' and '
        JSON_string = str(site)[2:-1]
        JSON_data = json.loads(JSON_string)

        return JSON_data["torrents"][:5]
    # thrown when no torrents are found
    except urllib.error.HTTPError:
        print("\nNo torrents found for '{} S{}E{}'".format(
            show.title,
            formatNumber(show.season),
            formatNumber(show.current_episode))
            )
        return None

def chooseTorrent(torrents):
    # returns a torrent's hash and title; used for downloading

    # if no torrents are passed to the function;
    # happens when no torrents are found with getTorrents()
    if not torrents:
        return None, None

    print("Download file:")
    index = 0
    for torrent in torrents:
        print("[{}] seeds:{}\t{}".format(
            colorize(index, Color.L_GREEN),
            torrent["seeds"],
            torrent["torrent_title"])
            )
        index += 1
    choice = validateNumber(len(torrents))

    chosen_torrent = torrents[choice]
    return (chosen_torrent["torrent_hash"],
            chosen_torrent["torrent_title"]
            )

def downloadTorrent(torrent_hash, torrent_title):
    # downloads and saves a torrent file

    # if no torrent hash and title are passed to the function
    # happens when no torrent is chosen with chooseTorrent()
    if not (torrent_hash and torrent_title):
        return

    source = "https://getstrike.net/torrents/api/download/"
    url = "{}{}.torrent".format(source,torrent_hash)

    req = urllib.request.Request(url, headers=HEADER)
    torrent_data = urllib.request.urlopen(req)
    torrent_file = open("{}.torrent".format(torrent_title), "wb")
    torrent_file.write(torrent_data.read())
    torrent_file.close()
    print("Torrent file downloaded.")
