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
from showsho.show import Show

def print_shows(show_list, airing, padding):
    """Print list of shows.

    Goes through the list of Show() objects and prints useful
    information. If "airing" is True, it will only print shows
    that are airing or about to air. "Padding" is used to pad and
    align the output.
    """
    for show in show_list:
        if airing:
            if show.status in ["airing", "new", "soon", "last", "Unknown"]:
                print(utils.pretty_status(show, padding))
        else:
            print(utils.pretty_status(show, padding))

def update_shows(show_list, file_hash, cache_dir):
    """Update the show's data (attributes).

    Runs the Show().update method for each show in the list, getting
    new data. Creates additional "updated_list" which contains the
    new data in a dictionary. That dictionary is then saved to the
    cache file (JSON formatted).
    """
    updated_list = []
    for show in show_list:
        show.update()
        updated_list.append(show.dump_data())

    if updated_list:
        utils.save_data(updated_list, file_hash, cache_dir)

def download_shows(show_list):
    """Download torrent file for episodes.

    Goes though each show in the Show() object list. If a show has
    a new episode out, it appends information about those episodes
    in the "for_download" list.
    For every show and its episodes in the "for_downoload" list,
    get the torrent information and display a magnet link that
    can be used to download the show.

    Note: in the future the magnet link might be replaced by an
    automatic download of the torrent. See: utils.py/get_torrents().
    """
    for_download = []
    for show in show_list:
        if show.status in ["new", "last"]:
            for_download.append(show.check_episodes_download())

    for show in for_download:
        for episode in show:
            torrents = utils.get_torrents(episode[0], episode[1], episode[2])
            torrent_title, torrent_magnet = utils.choose_torrent(torrents)

            print("\n{}".format(torrent_magnet))

def main(file_path, airing, update, download, delay):
    """Runs the program in steps.

    First it sets up the cache directory which optionally already
    contains data about the shows. Useful to speed things up and
    to make it work offline.
    Then it gets a list of shows, which contains dictionaries with
    information about the show. Along the way, it additionally checks
    if the program is being run for the first time which is used to
    update the information later on.
    Once the list is available, it then creates a new list which is
    holding Show() objects. Show() objects are instantiated with
    data from the dictionaries in the list and contain methods to
    determine additional data about the show, as well as a method to
    dump a new dictionary with updated show information (saving a
    cache file).

    Finally, it runs through each show object from the list and
    displays the information. Depending on the options which are passed
    to main, it might also update the show's information, download them
    or only print shows that are airing.
    """
    # handling of the cache directory, file hash and show list
    cache_dir = utils.get_cache_dir()
    if not os.path.exists(cache_dir):
        os.mkdir(cache_dir)
    file_hash = utils.get_file_hash(file_path)
    first_run, shows = utils.get_shows_list(file_path, file_hash, cache_dir)

    # adds a delay to every date if the option is passed as an argument
    if delay:
        Show.delay = True

    # create a list of Show() objects
    show_object_list = []
    for show in shows:
        show_object_list.append(Show(
            show["title"],
            show["season"],
            show["premiere"],
            show["end"],
            show["episodesNumber"],
            show["episodes"]
            ))

    if first_run or update:
        update_shows(show_object_list, file_hash, cache_dir)

    print_shows(show_object_list, airing, Show.padding)

    if download:
        download_shows(show_object_list)
