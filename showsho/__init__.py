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
    """Show object containing a show's info"""
    def __init__(self, title, season, premiere, episodes):
        self.title = title
        self.season = season
        self.premiere = premiere
        self.episodes = episodes

        if self.premiere and self.episodes:
            self.premiere = utils.getDateObject(premiere)
            self.getLastEpisodeDate()
            # TODO: prevent getting the current episode if the show
            #       stopped airing
            self.getCurrentEpisode()
            self.getStatus()
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
        """Sets attributes based on a shows current status"""
        # for shows currently on air
        if self.premiere <= TODAY <= self.last_episode_date:
            # if a a show's last episode is on today
            if self.last_episode_date == TODAY:
                self.status = "airing_last"
            # if there's a new episode out today
            elif utils.getDay(TODAY) == utils.getDay(self.premiere):
                self.status = "airing_new"
            # otherwise it's just airing
            else:
                self.status = "airing"

        # if a show has ended
        elif self.last_episode_date < TODAY:
            self.status = "ended"

        # if a show has a known premiere date
        elif self.premiere > TODAY:
            self.status = "soon"

def showShows(shows):
    # prints all the shows out with color-coded information
    if len(shows) < 1:
        print("File empty, add some shows to it!")
        return

    # prints info about each show based on attributes; sorts by title
    for show in sorted(shows, key=lambda show: show.title):
        print("------------")
        print(utils.showInfo(show))
    print("------------")

def downloadShows(shows):
    # downloads a torrent file for shows which have a new episode
    if len(shows) < 1:
        return

    # used to display a message if no shows are available for download
    no_shows_to_download = True

    for show in shows:
        if show.status == "airing_new":
            no_shows_to_download = False

            torrents = utils.getTorrents(show)
            torrent_hash, torrent_title = utils.chooseTorrent(torrents)
            utils.downloadTorrent(torrent_hash, torrent_title)

    if no_shows_to_download:
        print("No new episodes out. Nothing to download.")

def main(show_file_path, download_set):
    # loads JSON data from file, creates a list with Show() objects,
    # displays and optionally downloads the shows
    try:
        show_file = open(show_file_path, "r")
        JSON_data = json.load(show_file)
    except FileNotFoundError:
        print("No such file: {}".format(show_file_path))
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
            print("Error in the show file; check show: {}".format(title))
            sys.exit(2)

    # displays all the shows
    showShows(shows)
    # if the download flag was set, downloads new episodes
    if download_set:
        downloadShows(shows)
