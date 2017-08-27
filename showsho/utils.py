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
import re

from showsho import show

HEADER = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:48.0) Gecko/20100101 Firefox/48.0"}

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
    _list = []
    _file = open(file_path, "r")
    for line in _file:
        _list.append(line.strip())
    return _list

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

def shows_from_cache(file_path):
    """Return list of showsho.show.Show() objects from cache.

    Gets data for shows from a cached file. Uses that data to create
    Show() objects for each and returns a list containing a Show()
    object for every show in the cache file.
    """
    file_ = open(file_path, "r")
    json_data = json.load(file_)

    shows = []
    for s in json_data:
        shows.append(show.Show(
            s["title"],
            s["season"],
            s["premiere"],
            s["end"],
            s["episodes"]
            ))

    return shows

def shows_from_scratch(file_path):
    """Return a list of showsho.show.Show() objects for the first time.

    Gets a list of show names from a file. Then it creates Show()
    objects for every show in the list with no information except
    the show's name.
    """
    show_names = get_lines_from_file(file_path)

    shows = []
    for s in show_names:
        shows.append(show.Show(
            s,
            None,
            "",
            "",
            {}
            ))

    return shows

def get_URL_string(url):
    """Return a string with the content of an URL."""
    try:
        response = urllib.request.urlopen(url)
        response_string = response.read().decode()
        return response_string
    except urllib.error.HTTPError:
        return None

def get_choice(length):
    """Return user's chosen number, with input validation for a range."""
    while True:
        choice = input(">")
        if choice.isdigit() and int(choice) in range(length):
            return int(choice)
    print("Invalid choice, must enter a number, try again.")

def date_from_string(date_string, delay):
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

def string_from_date(dateobject, delay):
    """Return a string in ISO 8601 format from a dateobject.

    Opposite of date_from_string. Optionally removes 1 day (to
    compensate for the added 1 day from date_from_string()).
    """
    if delay:
        dateobject = dateobject - datetime.timedelta(days=1)
        return dateobject.isoformat()
    else:
        return dateobject.isoformat()

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
            format_number(show.season),
            format_number(show.last_episode),
            colorize("Last episode!", Color.L_RED)
            )

    elif show.status == "Unknown":
        return "{} - {}".format(
            colorize(show.title, Color.L_RED),
            "not found. Please check the show's name"
            )

def check_connection():
    """Return True if connected to the internet.

    Uses Google(tm) to check for connectivity.
    """
    try:
        urllib.request.urlopen("http://www.google.com")
        return True
    except urllib.error.URLError:
        return False

# see __init__.py download_shows() comment
#def get_torrents(title, season, episode):
#    """Return a list with torrent data tuples.
#
#    Takes a show's name, season and episode number and looks up
#    torrents on btdb.in. Returns a tuple containing the
#    torrent's title, number of seeds and magnet link.
#
#    Each tuple has the following elements:
#    (show_title, number_of_seeds, magnet_link)
#
#    Note: the magnet link might be temporary, until I find a reliable
#    torrent caching service. All the ones I've tried don't cache
#    the slightly more obscure shows, so downloading the torrent file
#    won't work.
#    """
#    source = "https://btdb.in/"
#    search_prefix = "q/"
#    sort_suffix = "/?sort=popular"
#    show_name_formatted = "{} s{}e{}".format(
#        title,
#        format_number(season),
#        format_number(episode)
#        )
#
#    search_query = "{}{}{}{}".format(
#        source,
#        search_prefix,
#        show_name_formatted,
#        sort_suffix
#        )
#
#    request = urllib.request.Request(search_query, headers=HEADER)
#    response = urllib.request.urlopen(request)
#    response_html_string = response.read().decode()
#
#    title_regex = '(?<=\.html" title=").*(?="><span)'
#    titles = re.findall(title_regex, response_html_string)
#
#    seeds_regex = '(?<=Popularity: <span class="item-meta-info-value">)\d*'
#    seeds = re.findall(seeds_regex, response_html_string)
#
##    hash_regex = "(?<=magnet:\?xt=urn:btih:).*(?=&amp;dn)"
##    hashes = re.findall(hash_regex, response_html_string)
#    magnet_regex = '(?<=magnet" href=").*(?="\ class="magnet")'
#    magnets = re.findall(magnet_regex, response_html_string)
#
#    zipped = zip(titles, seeds, magnets)
#    torrents = list(zipped)
#
#    return torrents[:5]
#
#def choose_torrent(torrents):
#    """Prompt the user for a choice and return torrent information.
#
#    Takes a sequence of torrent information sequences, display them
#    and prompts the user to choose one. Returns the torrent's name
#    and magnet link.
#
#    Note: it used to return the torrent's hash, see get_torrents().
#    """
#    print("\nDownload file:")
#    index = 0
#    for torr in torrents:
#        print("[{}] seeds:{}\t{}".format(
#            colorize(index, Color.GREEN),
#            torr[1],
#            torr[0]
#            ))
#        index += 1
#    choice = get_choice(len(torrents))
#    return torrents[choice][0], torrents[choice][2]
#
