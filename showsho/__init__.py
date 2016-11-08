# Showsho
# Copyright (C) 2015-2016  Dino Duratović <dinomol at mail dot com>
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

import os

from showsho import utils
from showsho import show

def get_shows(file_path, file_hash, cache_directory):
    """Return a list of showsho.show.Show() objects.

    Checks if there is cached data available for the file passed to
    showsho. If there is, it uses that data to create Show() objects.
    Otherwise it creates them "from scratch" using only the show's
    name.

    Additionally it returns a bool depending whether it's being run
    for the first time or not. That is useful to decide if the
    show's information should be fetched from the internet.
    """
    if utils.check_cached(file_hash, cache_directory):
        # since there's cached data, it's not being run for the first time
        first_run = False
        # cached file's filepath
        cached_file = "{}/{}".format(cache_directory, file_hash)
        shows = utils.shows_from_cache(cached_file)
    else:
        # since there's no cached data, it's being run for the first time
        first_run = True
        shows = utils.shows_from_scratch(file_path)

    return shows, first_run

def print_shows(shows, airing, padding):
    """Print information about Show() objects.

    Prints the status and information for each show in the shows list.
    If "airing" is True, it will only print shows that are airing.
    "padding" adjusts the padding in utils.pretty_status().
    """
    for show in shows:
        if airing:
            if show.status in ["airing", "soon", "new", "last"]:
                print(utils.pretty_status(show, padding))
        else:
            print(utils.pretty_status(show, padding))

def update_shows(shows, file_hash, cache_directory):
    """Update each show's information with data from the internet.

    First it checks if there's an internet connection, returns after
    a notifaction if there isn't.
    If there is connectivity, it updates each show by running the
    Show().update method on every show in the list.
    Finally it dumps the new data into the cache file (updates its
    content).
    """
    if not utils.check_connection():
        print("No internet connection. Cannot update shows!")
        return

    print("Updating and getting data about the shows...\n")
    for s in shows:
        s.update()

    # list to hold a dictionary for every show's data
    new_data = []
    for s in shows:
        # appends a dictionary with core data for the show
        new_data.append(s.dump_data())
    # saves it to disk, into the cache directory
    utils.save_data(new_data, file_hash, cache_directory)

def download_shows(shows):
    """Print a magnet link for episodes that aired today.

    Appends data about episodes that aired today (title, season,
    number)  to "episodes_to_download". Then it goes through each
    episode for each show in the list finding torrents and displaying
    a prompt to choose one of them. Finally it prints a magnet link
    for the chosen torrent.

    Note: this used to download actual torrent files,  but I can't
    find a reliable caching service to download them from. This might
    change in the future.
    """
    if not utils.check_connection():
        print("No internet connection. Cannot download episodes!")
        return

    episodes_to_download = []
    for s in shows:
        if s.status in ["new", "last"]:
            episodes_to_download.append(s.check_episodes_download())
    if not episodes_to_download:
        print("No new episodes out. Nothing to download.")
        return

    # nested loop, because episodes_to_download looks like this:
    # [
    #   [(show1, season, episode), (show1, season, episode)],
    #   [(show2, season, episode)]
    # ]
    for show in episodes_to_download:
        for ep in show:
            torrents = utils.get_torrents(ep[0], ep[1], ep[2])
            # when no torrents are found inform us about the exact episode
            if not torrents:
                show_info = "{} S{}E{}".format(ep[0], ep[1], ep[2])
                print("No torrents found for {}".format(show_info))
                return

            title, magnet_link = utils.choose_torrent(torrents)
            print("\n {}\n{}".format(
                utils.colorize(title, utils.Color.GREEN),
                magnet_link
                ))

def main(file_path, airing, update, download, delay):
    """Runs the main program.

    Gets the file's hash and cache directory (sets it up if required).
    Sets the delay if passed as a flag.
    Gets a list of Show() objects. Updates them if it's run for the
    first time or if the "update" flag is passed. Then it prints
    information about the show and finally if the "download" flag
    is passed, it downloads the new episodes.
    """
    file_hash = utils.get_file_hash(file_path)
    cache_directory = utils.get_cache_dir()
    if not os.path.exists(cache_directory):
        os.mkdir(cache_directory)

    if delay:
        show.Show.delay = True

    shows, first_run = get_shows(file_path, file_hash, cache_directory)

    if update or first_run:
        update_shows(shows, file_hash, cache_directory)

    print_shows(shows, airing, show.Show.padding)

    if download:
        download_shows(shows)
