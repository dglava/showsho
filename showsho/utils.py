# Showsho
# Copyright (C) 2015  Dino Duratović <dinomol at mail dot com>
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
import urllib.request
import os
import sys
import re
import json

# used to disable colored text on Windows
OS = os.name
TODAY = datetime.date.today()
# used to prevent an 403 error forbidden when parsing the search website
HEADER = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:48.0) Gecko/20100101 Firefox/48.0"}

class Color:
    GREEN = "\033[32m"
    RED = "\033[31m"
    ORANGE = "\033[33m"
    L_BLUE = "\033[1;34m"
    L_RED = "\033[1;31m"

class Show:
    """Class containing a show's info.

    Has attributes for the show's title and current season.
    If a premiere date and number of episodes are given, it will calculate
    the show's status (airing, ended, etc), its latest episode and
    the date when the show's last episode is airing. All those attributes
    are used for printing the show's information.
    """

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

def stripHTML(word):
    """Returns the string passed to it with stripped HTML tags

    Only strips the <b> and </b> tags which end up in the title
    inside getTorrents()
    """
    strip_first = word.replace("<b>", "")
    strip_second = strip_first.replace("</b>", "")
    return strip_second

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

def getShowData(show_name):
    """Return a dictionary containing a show's data.

    It has the following layout:
    {"title": [season, "premiere date", number of episodes]}
    """
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
            colorize(show.title, Color.GREEN),
            # adding 9 to compensate for the color escape codes
            # which Python "prints" too
            padding + 9,
            formatNumber(show.season),
            formatNumber(show.current_episode),
            getDay(show.premiere)
            )

    elif show.status == "airing_new":
        info = "{:<{}} | S{}E{} | {} {}".format(
            colorize(show.title, Color.GREEN),
            padding + 9,
            formatNumber(show.season),
            formatNumber(show.current_episode),
            getDay(show.premiere),
            colorize("New episode!", Color.L_BLUE)
            )

    elif show.status == "airing_last":
        info = "{:<{}} | S{}E{} | {} {}".format(
            colorize(show.title, Color.GREEN),
            padding + 9,
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
            colorize(show.title, Color.ORANGE),
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

def getTorrents(show):
    """Returns a list with torrent data tuples from a Show() object.

    Each tuple has the following elements:
    (show_title, number_of_seeds, torrent_hash)

    All data is fetched from btdb.in
    """
    source = "https://btdb.in/"
    search_prefix = "q/"
    sort_suffix = "/?sort=popular"
    show_name_formatted = "{} s{}e{}".format(
        show.title,
        formatNumber(show.season),
        formatNumber(show.current_episode)
        )

    search_query = "{}{}{}{}".format(
        source,
        search_prefix,
        show_name_formatted,
        sort_suffix
        )

    request = urllib.request.Request(search_query, headers=HEADER)
    response = urllib.request.urlopen(request)
    response_html_string = response.read().decode()

    title_regex = '(?<=\.html" title=").*(?="><span)'
    titles = re.findall(title_regex, response_html_string)

    seeds_regex = '(?<=Popularity: <span class="item-meta-info-value">)\d*'
    seeds = re.findall(seeds_regex, response_html_string)

    hash_regex = "(?<=magnet:\?xt=urn:btih:).*(?=&amp;dn)"
    hashes = re.findall(hash_regex, response_html_string)

    zipped = zip(titles, seeds, hashes)
    torrents = list(zipped)

    return torrents[:5]

def chooseTorrent(torrents):
    """Prompts the user for a choice and returns torrent information.

    Takes a list of torrent information tuples as an argument (see getTorrents())
    and returns a tuple with the torrent's title and hash
    """

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

    return torrents[choice][0], torrents[choice][2]

def downloadTorrent(torrent_title, torrent_hash):
    """Downloads and saves a torrent file

    Uses itorrent.org to download a torrent file from a provided torrent hash
    """

    download_source = "http://itorrents.org/torrent/"
    download_url = "{}{}.torrent".format(
        download_source,
        torrent_hash.upper()
        )
    # using urllib.request.Request() to change the header,
    # otherwise it returns a 403 forbidden error with Python's header
    request = urllib.request.Request(
        download_url,
        headers=HEADER
        )
    torrent_data = urllib.request.urlopen(request).read()
    torrent_file = open("{}.torrent".format(torrent_title), "wb")
    torrent_file.write(torrent_data)
    torrent_file.close()
    print("Torrent file downloaded")
