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

import hashlib
import os
import os.path
import urllib.request
import datetime
import json

class Color:
    GREEN = "\033[32m"
    RED = "\033[31m"
    ORANGE = "\033[33m"
    L_BLUE = "\033[1;34m"
    L_RED = "\033[1;31m"

def format_number(number):
    """Add a leading zero to the episode/season if necessary."""
    return "{:0>2}".format(number)

def colorize(text, color):
    """Return colorized text."""
    return "{}{}\033[0m".format(color, text)

def get_cache_dir():
    """Return string with cache directory.

    This is the  directory where the cached data files are stored.
    It takes into account the XDG base directory standard, but if the
    environment variables aren't set it falls back to ~/.cache.
    """
    base_dir = os.getenv(
        "XDG_CACHE_HOME",
        os.path.expanduser("~/.cache")
        )
    full_dir = "{}/showsho".format(base_dir)
    return full_dir

def get_file_hash(file_path):
    """Return the provided file's SHA1 hash."""
    file_ = open(file_path, "rb")
    hash_ = hashlib.sha1()
    hash_.update(file_.read())
    return hash_.hexdigest()

def get_lines_from_file(file_path):
    """Return the file's content as lines contained in a list."""
    list_ = []
    file_ = open(file_path, "r")
    for line in file_:
        list_.append(line.strip())
    return list_

def check_cached(file_hash, cache_directory):
    """Check if cached version of file exists.

    Look in the cache_directory to see if a file with the provided
    hash exists.
    """
    files_in_cache = os.listdir(cache_directory)
    if file_hash in files_in_cache:
        return True
    else:
        return False

def get_URL_string(url):
    """Return a string with the content of an URL."""
    try:
        response = urllib.request.urlopen(url)
        response_string = response.read().decode()
        return response_string
    except urllib.error.HTTPError:
        return None

def date_from_string(date_string, delay=False):
    """Return a date object from the string.

    The string should be specified in ISO 8601 format: YYYY-MM-DD.
    If it's not specified in that format, returns the original string.
    Optionally it also adds a delay of 1 day to the date (see
    showsho/show.py Show() for explanations).
    """
    try:
        split_string = date_string.split("-")
        date = datetime.date(
            int(split_string[0]),
            int(split_string[1]),
            int(split_string[2])
            )
        if delay:
            date = date + datetime.timedelta(days=1)
        return date
    except:
        return date_string

def string_from_date(dateobject, delay=False):
    """Return a string in ISO 8601 format from a dateobject.

    Opposite of date_from_string. Optionally removes 1 day (to
    compensate for the added 1 day from date_from_string()).
    """
    if delay:
        dateobject = dateobject + datetime.timedelta(days=-1)
        return dateobject.isoformat()
    else:
        return dateobject.isoformat()

def get_shows_list(file_path, file_hash, cache_dir):
    """Return a list with a show's key data.

    The list contains a dictionary for each show. The dictionary
    contains data like the show's title, season premiere, etc.

    Dictionary's structure:
    {
    "title": str,
    "season": int,
    "premiere": str,
    "episodesNumber": int,
    "end": str,
    "episodes": {"1": "2016-06-06"}
    }

    It checks first if there's a cached file with the show's data
    (in JSON format). If there is, it reads the data from it. If
    there isn't, it creates an empty skeleton dictionary for
    each show with only the "title" taken from the file passed to
    it. Additionally it sets "first_run" to True. That variable is
    used to signal that the show's information should be updated
    later (see Show.update() from showsho/shows.py).
    """
    first_run = False

    cache_dir = get_cache_dir()
    if not os.path.exists(cache_dir):
        os.mkdir(cache_dir)

    # get hash and check if it's in the cache directory
    file_hash = get_file_hash(file_path)
    if check_cached(file_hash, cache_dir):
        file_ = open("{}/{}".format(cache_dir, file_hash))
        shows_list = json.load(file_)
    else:
        # if it's not, create a skeleton dictionary for every show
        # in the list, appending it to the list of dicts
        shows_list = []
        list_ = get_lines_from_file(file_path)
        for show in list_:
            skeleton_dict = {
                "title": show,
                "season": None,
                "premiere": "",
                "end": "",
                "episodesNumber": None,
                "episodes": {}
                }
            shows_list.append(skeleton_dict)
        # doing so means it's run for the first time
        first_run = True

    return first_run, shows_list

def save_data(data, file_hash, cache_dir):
    """Save data to the cache directory.

    Takes a list with dictionaries for each show and writes it
    to a file in JSON format. Uses the file's hash as the filename
    and saves it in the cache directory.
    """
    file_ = open("{}/{}".format(cache_dir, file_hash), "w")
    json.dump(data, file_, ensure_ascii=False, indent=0)

def pretty_status(show, padding):
    """Return a nicely formatted string with info.

    Takes a Show() object instance as argument and returns a string
    containing information about the show depending on its status.
    Adds padding to the title to line shows up. The padding value
    is calculated during Show() object instantiation. Adding an
    additional padding of 9 to compensate for the fact that
    Python also "print" the color escape codes.
    """
    if show.status == "airing":
        return "{:<{}} | S{}E{} | {}".format(
            colorize(show.title, Color.GREEN),
            padding + 9,
            format_number(show.season),
            format_number(show.last_episode),
            show.premiere.strftime("%a")
            )

    elif show.status == "soon":
        return "{:<{}} | Season {} premiere on {}".format(
            colorize(show.title, Color.ORANGE),
            padding + 9,
            format_number(show.season),
            show.premiere.strftime("%a, %d %b %Y")
            )

    elif show.status == "ended":
        return "{:<{}} | Last episode S{}E{}".format(
            show.title,
            padding,
            format_number(show.season),
            format_number(show.last_episode)
            )

    elif show.status == "done":
        return "{:<{}} | Show has ended | Last episode S{}E{}".format(
            colorize(show.title, Color.RED),
            padding + 9,
            format_number(show.season),
            format_number(show.last_episode)
            )

    elif show.status == "new":
        return "{:<{}} | S{}E{} | {}".format(
            colorize(show.title, Color.GREEN),
            padding + 9,
            format_number(show.season),
            format_number(show.last_episode),
            colorize("New Episode!", Color.L_BLUE)
            )

    elif show.status == "last":
        return "{:<{}} | S{}E{} | {}".format(
            colorize(show.title, Color.GREEN),
            padding + 9,
            show.season,
            show.last_episode,
            colorize("Last episode!", Color.L_RED)
            )
