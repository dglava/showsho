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
import sys

from showsho import utils

TODAY = datetime.date.today()

class Show:
    # used to adjust the airing dates for different timezones
    delay = datetime.timedelta(days=0)

    """Show object containing a show's info"""
    def __init__(self, title, season, premiere, episodes):
        self.title = title
        self.season = season
        self.premiere = premiere
        self.episodes = episodes

        if self.premiere and self.episodes:
            self.premiere = utils.getDateObject(premiere) + Show.delay
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
            elif utils.getDay(TODAY) == utils.getDay(self.premiere):
                self.status = "airing_new"
            else:
                self.status = "airing"

        elif self.last_episode_date < TODAY:
            self.status = "ended"

        elif self.premiere > TODAY:
            self.status = "soon"

def showShows(shows, show_only_airing):
    """Prints all the shows out with color-coded information"""
    # filter for the show_only_airing flag
    valid_status = ["airing", "airing_last", "airing_new", "soon"]

    if len(shows) < 1:
        print("File empty, add some shows to it!")
        return

    # prints info about each show based on attributes; sorts by title
    for show in sorted(shows, key=lambda show: show.title):
        # prints only currently/soon to be airing shows
        if show_only_airing:
            if show.status in valid_status:
                print(utils.showInfo(show))
                print("------------")
        # otherwise prints all shows
        else:
            print(utils.showInfo(show))
            print("------------")

def downloadShows(shows):
    """downloads a torrent file for shows which have a new episode"""
    if len(shows) < 1:
        return

    # used to display a message if no shows are available for download
    no_shows_to_download = True

    for show in shows:
        if show.status == "airing_new" or show.status == "airing_last":
            no_shows_to_download = False

            torrents = utils.getTorrents(show)
            if torrents:
                torrent_hash, torrent_title = utils.chooseTorrent(torrents)
                utils.downloadTorrent(torrent_hash, torrent_title)
            else:
                print("No torrents found for '{} S{}E{}'".format(
                    show.title,
                    utils.formatNumber(show.season),
                    utils.formatNumber(show.current_episode))
                    )

    if no_shows_to_download:
        print("No new episodes out. Nothing to download.")

def main(show_file_path, download, delay, only_airing):
    # loads JSON data from file, creates a list with Show() objects,
    # displays and optionally downloads the shows

    # adjusts the airing date for shows if specified
    if delay:
        Show.delay = datetime.timedelta(days=delay)

    try:
        show_file = open(show_file_path, "r")
        JSON_data = json.load(show_file)
    except FileNotFoundError:
        print("No such file: '{}'".format(show_file_path))
        sys.exit(2)
    except ValueError:
        print("Bad JSON file. Check the formatting and try again.")
        sys.exit(2)

    shows = []
    for title, data in JSON_data.items():
        # makes sure that the JSON data is valid
        if utils.verifyData(data[0], data[1], data[2]):
            # if it is, creates a Show() object for each show and
            # appends it to the shows list
            shows.append(Show(title, data[0], data[1], data[2]))
        else:
            print("Error in the show file; check show: '{}'".format(title))
            sys.exit(2)

    # prints all the shows
    showShows(shows, only_airing)
    # if the download flag was set, downloads new episodes
    if download:
        downloadShows(shows)
