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

from showsho import utils

def showShows(shows, show_only_airing):
    """Prints all the shows out with color-coded information"""
    # filter for the show_only_airing flag
    valid_status = ["airing", "airing_last", "airing_new", "soon"]

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
    # used to display a message if no shows are available for download
    no_shows_to_download = True

    for show in shows:
        if show.status in ["airing_new", "airing_last"]:
            no_shows_to_download = False
            torrents = utils.getTorrents(show)
            if torrents:
                # if the torrent list isn't empty
                title, torrent_hash, source = utils.chooseTorrent(torrents)
                utils.downloadTorrent(title, torrent_hash, source)
            else:
                print("No torrents found for '{} S{}E{}'".format(
                    show.title,
                    utils.formatNumber(show.season),
                    utils.formatNumber(show.current_episode))
                    )

    if no_shows_to_download:
        print("No new episodes out. Nothing to download")

def main(show_file_path, download, delay, only_airing):
    # adjusts the airing date for shows if specified
    if delay:
        utils.Show.delay = datetime.timedelta(days=delay)

    # gets list of shows from the file path
    shows = utils.getShows(show_file_path)
    if len(shows) < 1:
        # if the list is empty, quits
        print("File empty. Add some shows!")
        return

    # prints the shows, takes into account the only_airing flag
    showShows(shows, only_airing)

    # downloads torrents if the download flag was passed on startup
    if download:
        downloadShows(shows)
