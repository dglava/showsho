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

    # contains updated versions of show dictionaries in case they
    # get updated
    updated_list = []
    for show in show_object_list:
        if first_run or update:
            show.update()
            updated_list.append(show.dump_data())

        if airing:
            if show.status in ["airing", "new", "soon", "last"]:
                print(utils.pretty_status(show, Show.padding))
        else:
            print(utils.pretty_status(show, Show.padding))

    # if data has been updates, save it to the new cache file
    if updated_list:
        utils.save_data(updated_list, file_hash, cache_dir)
