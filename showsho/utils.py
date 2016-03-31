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
import sys

# used for urllib requests
HEADER = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:40.0)"}
# used to disable colored text on Windows
OS = os.name
TODAY = datetime.date.today()

class Color:
    GREEN = "\033[32m"
    RED = "\033[31m"
    L_GREEN = "\033[1;32m"
    L_BLUE = "\033[1;34m"
    L_RED = "\033[1;31m"

class Show:
    """Class containing a show's info.

    Has attributes for the show's title and current season.
    If a premiere date and number of episodes are given, it will calculate
    the show's status (airing, ended, etc), its latest episode and
    the date when the show's last episode is airing. All those attributes
    are used for printing the show's information."""
    # used to adjust the airing dates for different timezones
    delay = datetime.timedelta(days=0)
    # used to align the shows for pretty printing
    padding = 0

    def __init__(self, title, season, premiere, episodes):
        self.title = title
        self.season = season
        self.premiere = premiere
        self.episodes = episodes

        if len(self.title) > Show.padding:
            Show.padding = len(self.title)

        if self.premiere and self.episodes:
            self.premiere = getDateObject(premiere) + Show.delay
            self.getLastEpisodeDate()
            self.getStatus()
            if self.status.startswith("airing"):
                self.getCurrentEpisode()
        else:
            self.status = "unknown"

    def getLastEpisodeDate(self):
        """Gets the airing date of the season's last episode"""
        # premiere date + number of weeks/episodes the season has;
        # need to subtract 1 from the episodes number, because it counts
        # from the premiere up and which is already taken into account
        self.last_episode_date = (
            self.premiere + datetime.timedelta(weeks=self.episodes - 1)
            )

    def getCurrentEpisode(self):
        """Calculates the current/latest episode of a show"""
        # number of days since the premiere
        difference = TODAY - self.premiere
        # days // 7 days = weeks (episodes) passed,
        # adding 1 because episodes are indexed from 1, not 0
        self.current_episode = ((difference.days // 7) + 1)

    def getStatus(self):
        """Sets the show's status: if it's airing, ended, etc"""
        if self.premiere <= TODAY <= self.last_episode_date:
            if self.last_episode_date == TODAY:
                self.status = "airing_last"
            elif getDay(TODAY) == getDay(self.premiere):
                self.status = "airing_new"
            else:
                self.status = "airing"

        elif self.last_episode_date < TODAY:
            self.status = "ended"

        elif self.premiere > TODAY:
            self.status = "soon"

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
    return "{:0>2}".format(number)

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

def loadShowData(path):
    """Returns a dictionary with JSON data from a given file path"""
    try:
        show_file = open(path, "r")
        json_data = json.load(show_file)
        return json_data
    except FileNotFoundError:
        print("No such file: '{}'".format(path))
        sys.exit(2)
    except ValueError:
        print("Bad JSON file. Check the formatting and try again.")
        sys.exit(2)

def getShows(file_path):
    """Returns a list with Show() objects from a given dictionary"""
    show_data = loadShowData(file_path)

    shows = []
    for title, data in show_data.items():
        # makes sure that the show's data is valid
        if verifyData(data[0], data[1], data[2]):
            # if it is, creates a Show() object for each show and
            # appends it to the shows list
            shows.append(Show(title, data[0], data[1], data[2]))
        else:
            print("Error in the show file; check show: '{}'".format(title))
            sys.exit(2)

    return shows

def showInfo(show, padding):
    """Returns a string with the show's details for printing"""
    if show.status == "airing":
        info = "{:<{}} | S{}E{} | {}".format(
            colorize(show.title, Color.L_GREEN),
            # adding 11 to compensate for the color escape codes
            # which Pyton "prints" too
            padding + 11,
            formatNumber(show.season),
            formatNumber(show.current_episode),
            getDay(show.premiere)
            )

    elif show.status == "airing_new":
        info = "{:<{}} | S{}E{} | {} {}".format(
            colorize(show.title, Color.L_GREEN),
            padding + 11,
            formatNumber(show.season),
            formatNumber(show.current_episode),
            getDay(show.premiere),
            colorize("New episode!", Color.L_BLUE)
            )

    elif show.status == "airing_last":
        info = "{:<{}} | S{}E{} | {} {}".format(
            colorize(show.title, Color.L_GREEN),
            padding,
            formatNumber(show.season),
            formatNumber(show.current_episode),
            getDay(show.premiere),
            colorize("Last episode!", Color.L_RED)
            )

    elif show.status == "ended":
        info = "{:<{}} | Last episode: S{}E{}".format(
            colorize(show.title, Color.RED),
            padding + 9,
            formatNumber(show.season),
            formatNumber(show.episodes)
            )

    elif show.status == "soon":
        info = "{:<{}} | Season {} premiere on {}".format(
            colorize(show.title, Color.GREEN),
            padding + 9,
            show.season,
            getPrettyDate(show.premiere)
            )

    elif show.status == "unknown":
        info = "{:<{}} | Season {} unknown premiere date".format(
            show.title,
            padding,
            show.season
            )

    return info

def getJSON(url):
    """Returns a dictionary with parsed JSON data from an URL"""
    req = urllib.request.Request(url, headers=HEADER)
    response = urllib.request.urlopen(req).read().decode()
    json_data = json.loads(response)

    return json_data

def getTorrents(show):
    """Returns a list with torrent data"""
    # websites with torrent APIs
    website1 = "https://torrentproject.se/?s="

    # replaces spaces with %20
    search = "{}%20s{}e{}".format(
        show.title.replace(" ", "%20"),
        formatNumber(show.season),
        formatNumber(show.current_episode)
        )

    # dictionary with torrent information
    web1_data = getJSON(website1 + search + "&out=json")
    # if torrentproject is in maintenence mode, do nothing
    if web1_data == "api maintenance":
        return
    # useless key, also messes with the filtering below if not removed
    del web1_data["total_found"]

    # goes through the dictionary and filters out only the info we
    # need; appends it to our torrents list as tuples for each torrent
    torrents = []
    # torrent project's data
    for i in web1_data:
        title = web1_data[i]["title"]
        seeds = web1_data[i]["seeds"]
        torrent_hash = web1_data[i]["torrent_hash"]
        source = "torrentproject"
        torrents.append((title, seeds, torrent_hash, source))

    # sorts the results by seeders
    torrents_sorted =sorted(torrents, key=lambda x: x[1], reverse=True)
    # returns the top 5 results
    return torrents_sorted[:5]

def chooseTorrent(torrents):
    """Prompts the user for a choice and returns torrent information"""
    print("\nDownload file:")

    index = 0
    for torr in torrents:
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
    # download URL template for torrentproject
    source = "http://torrentproject.se/torrent/"

    url = "{}{}.torrent".format(source, torrent_hash.upper())

    req = urllib.request.Request(url, headers=HEADER)
    torrent_data = urllib.request.urlopen(req)
    torrent_file = open("{}.torrent".format(torrent_title), "wb")
    torrent_file.write(torrent_data.read())
    torrent_file.close()
    print("Torrent file downloaded.")
