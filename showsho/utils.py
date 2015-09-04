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
    """Returns colorized text"""
    # doesn't output colored text on Windows(tm)(c)
    if OS == "nt":
        return text
    else:
        return "{}{}\033[0m".format(color, text)

def getDateObject(date_string):
    """Returns a date object for the given date string"""
    yyyy, mm, dd = date_string.split("-")
    date_object = datetime.date(int(yyyy), int(mm), int(dd))
    return date_object

def getDay(date_object):
    """Returns the day's name of a date object: Monday, Tuesday, etc"""
    return date_object.strftime("%A")

def getPrettyDate(date_object):
    """Returns a string from a date object in the format Day, MM-YYYY"""
    return date_object.strftime("%a, %d %b %Y")

def formatNumber(number):
    """Adds a leading zero to the episode/season if necessary"""
    if len(str(number)) == 1:
        return "0{}".format(number)
    else:
        return str(number)

def verifyDate(date):
    """Returns True if a date is in the valid format: YYYY-MM-DD"""
    try:
        getDateObject(date)
        return True
    except (TypeError, AttributeError, ValueError):
        return False

def getChoice(length):
    """Returns user's chosen number, with input validation for a range"""
    while True:
        choice = input(">")
        if choice.isdigit() and int(choice) in range(length):
            return int(choice)
        print("Invalid choice, must enter a number, try again.")

def verifyData(season, date, episodes):
    """Checks if a show's data (from the JSON file) is valid"""
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
    """Returns a string with the show's details for printing"""
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

def getJSON(url):
    """Returns a dictionary with parsed JSON data from an URL"""
    try:
        req = urllib.request.Request(url, headers=HEADER)
        response = urllib.request.urlopen(req).read().decode()
        json_data = json.loads(response)

        return json_data
    except urllib.error.HTTPError:
        # getstrike's API throws this when no torrents are found
        return {"torrents": {}}

def getTorrents(show):
    """Returns a list with torrent data"""
    # websites with torrent APIs
    website1 = "https://torrentproject.se/?s="
    website2 = "https://getstrike.net/api/v2/torrents/search/?phrase="

    # replaces spaces with %20
    search = "{}%20s{}e{}".format(
        show.title.replace(" ", "%20"),
        formatNumber(show.season),
        formatNumber(show.current_episode)
        )

    # dictionaries with all the torrent information
    web1_data = getJSON(website1 + search + "&out=json")
    web2_data = getJSON(website2 + search)
    # useless key, also messes with the filtering below if not removed
    del web1_data["total_found"]

    # goes through both dictionaries and filters out only the info we
    # need; appends it to our torrents list as tuples for each torrent
    torrents = []
    # torrent project's data
    for i in web1_data:
        title = web1_data[i]["title"]
        seeds = web1_data[i]["seeds"]
        torrent_hash = web1_data[i]["torrent_hash"]
        source = "torrentproject"
        torrents.append((title, seeds, torrent_hash, source))

    # getstrike's data
    for torrent in web2_data["torrents"]:
        title = torrent["torrent_title"]
        seeds = torrent["seeds"]
        torrent_hash = torrent["torrent_hash"]
        source = "getstrike"
        torrents.append((title, seeds, torrent_hash, source))

    # sorts the results by seeders
    torrents_sorted =sorted(torrents, key=lambda x: x[1], reverse=True)
    # returns the top 5 results
    return torrents_sorted[:5]

def chooseTorrent(torrents):
    """Prompts the user for a choice and returns torrent information"""
    index = 0
    for torr in torrents:
        # [0] RectifyS03.scene seeds: 515
        print("[{}] seeds:{}\t{}".format(
            colorize(index, Color.L_GREEN),
            torr[1],
            torr[0]
            ))
        index += 1

    choice = getChoice(len(torrents))

    # returns a (title, hash, source) tuple
    return torrents[choice][0], torrents[choice][2], torrents[choice][3]

def downloadTorrent(torrent_title, torrent_hash, source_website):
    """Downloads and saves a torrent file"""
    # download URL templates for getstrike and torrentproject
    torrentproject = "http://torrentproject.se/torrent/"
    getstrike = "https://getstrike.net/torrents/api/download/"

    if source_website == "torrentproject":
        source = torrentproject
    elif source_website == "getstrike":
        source = getstrike

    url = "{}{}.torrent".format(source, torrent_hash.upper())

    req = urllib.request.Request(url, headers=HEADER)
    torrent_data = urllib.request.urlopen(req)
    torrent_file = open("{}.torrent".format(torrent_title), "wb")
    torrent_file.write(torrent_data.read())
    torrent_file.close()
    print("Torrent file downloaded.")

