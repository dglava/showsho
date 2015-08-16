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
    # returns a date object for the given date string; format YYYY-MM-DD
    yyyy, mm, dd = date_string.split("-")
    date_object = datetime.date(int(yyyy), int(mm), int(dd))
    return date_object

def getDay(date_object):
    # returns the name of the day of a date object like: Mon, Tue, Wed
    return date_object.strftime("%a")

def getDateString(date_object):
    # returns a string from a date in the format YYYY-MM-DD
    if date_object:
        return date_object.strftime("%Y-%m-%d")
    else:
        return date_object

def formatNumber(number):
    # adds a leading zero to the episode/season if necessary
    if len(str(number)) == 1:
        return "0{}".format(number)
    else:
        return str(number)

def validateNumber(allow_none=False):
    # returns a number (int) with input validation
    # if allow_none is True, it can also return None if input is blank
    while True:
        choice = input(">")
        if allow_none:
            if choice == "":
                return None
            elif choice.isdigit():
                return int(choice)
        elif choice.isdigit():
            return int(choice)
        print("Invalid choice, must enter a number, try again.")

def setTitle():
    # gets the show's title, used during adding or editing a show
    print("Show's title:")
    title = input(">")
    return title

def setSeason():
    # gets the season number, used during adding or editing a show
    print("Season number:")
    season = validateNumber()
    return season

def setDate():
    # gets the premiere date, used during adding or editing a show
    print("Season's premiere date in the YYYY-MM-DD format.")
    print("Leave blank if unknown.")
    # input validation
    while True:
        date = input(">")
        if date == "":
            return None
        try:
            getDateObject(date)
            return date
        except (ValueError, TypeError):
            print("Invalid choice, enter it in the proper format.")

def setEpisodes():
    # gets the number of episodes in the season,
    # used during adding or editing a show
    print("Number of episodes the season has. Leave blank if unknown.")
    episodes = validateNumber(True)
    return episodes

def printAiring(show):
    #prints shows which are currently airing
    line1 = colorize(show.title, Color.L_GREEN)
    line2 = "S{}E{} | {}".format(
        formatNumber(show.season),
        formatNumber(show.latest_episode),
        getDay(show.premiere))

    if show.last_episode:
        line1 += " {}".format(colorize("Last episode!", Color.L_RED))
    if show.new_episode:
        line2 += " {}".format(colorize("New episode!", Color.L_BLUE))
    # warning if the number of episodes for the season is missing
    if not show.episodes:
        line2 += "\n{}".format(colorize(WARNING, Color.L_RED))

    print(line1)
    print(line2)

def printAiringSoon(show):
    # prints shows which have a season premier date set
    line1 = colorize(show.title, Color.GREEN)
    line2 = "Season {} premiere on: {}".format(
        formatNumber(show.season),
        show.premiere.strftime("%a, %d. %b")
        )
    # warning if the number of episodes for the season is missing
    if not show.episodes:
        line2 += "\n{}".format(colorize(WARNING, Color.L_RED))

    print(line1)
    print(line2)

def printEnded(show):
    # prints shows which have ended airing
    line = "{}\nLast episode: S{}E{}".format(
        colorize(show.title, Color.RED),
        formatNumber(show.season),
        formatNumber(show.episodes)
        )
    print(line)

def printNotAiring(show):
    # prints shows which aren't airing and have no premiere date set
    line = "{}\nSeason {} premiere unknown".format(
        show.title,
        formatNumber(show.season))
    print(line)

def getTorrents(show):
    # returns a list with a dict for the top 5 torrents of a show
    source = "https://getstrike.net/api/v2/torrents/search/?phrase="
    search = "{}%20s{}e{}".format(
        show.title.replace(" ", "%20"),
        formatNumber(show.season),
        formatNumber(show.latest_episode)
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
        print("\nNo torrents found for show '{}'".format(show.title))
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
    choice = validateNumber()

    # TODO: maybe extend validateNumber() to check for range,
    #       would help avoid this check
    if choice in range(len(torrents)):
        chosen_torr = torrents[choice]
        return chosen_torr["torrent_hash"], chosen_torr["torrent_title"]
    else:
        print("Invalid choice.")
        return None, None

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