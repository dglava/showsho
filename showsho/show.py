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

import json
import datetime

from showsho import utils

API_URL = "http://api.tvmaze.com"
TODAY = datetime.date.today()

class Show:
    """Class containing everything needed to display a show.

    Holds the show's basic attributes passed to it and has methods
    to determine additional useful data and to update the data
    from the internet (using the TVMaze API).

    Only the "title" is needed during instatiation and it's always
    available because it's in the text file passed to it. The other
    arguments are either read from the cached file or empty (None).

    It creates the self.info and self.last_episode attributes,
    but empty and gets the show's status based on the known information
    (attributes).

    The Show.delay class attribute is used to delay the airdates by
    1 day, which is useful in certain timezones. It's used in all
    methods where premiere, end or other relevant dates are set.
    The Show.padding class attribute is used during printing, to make
    everything align nicely.
    """
    padding = 0
    delay = False

    def __init__(self, title, season, premiere, end, episodes):
        self.title = title
        self.season = season
        self.premiere = utils.date_from_string(premiere, Show.delay)
        self.end = utils.date_from_string(end, Show.delay)
        self.episodes = self.episodes_to_date(episodes)

        self.info = None
        self.last_episode = None
        self.get_status()
        self.get_last_episode()

    def fetch_show_info(self):
        """Download information about the show.

        Uses the TVMaze API to get various data about the show.
        The main endpoint is "singlesearch", but with embedded
        "season" and "episodes" information.

        If no show with the name can be found, self.info will be None.
        """
        API_endpoint = "/singlesearch/shows?q="
        API_embedded = "&embed[]=seasons&embed[]=episodes"
        search_query = "{}{}{}{}".format(
            API_URL,
            API_endpoint,
            self.title,
            API_embedded
            )
        response = utils.get_URL_string(search_query)
        if response:
            self.info = json.loads(response)

    def get_season(self):
        """Get the relevant season.

        Inside the "_embedded" data is information about the seasons.
        First we filter out the seasons list. Then we iterate through
        the list in reverse stopping at the first season which has
        a "premiereDate". That season is the one we want and we get
        its number.
        """
        seasons = self.info["_embedded"]["seasons"]
        for season in reversed(seasons):
            if season["premiereDate"]:
                current_season = season["number"]
                break
        self.season = int(current_season)

    def get_premiere(self):
        """Get the season's premiere date.

        Inside the "_embedded" data is information about the seasons.
        We want the value of the "premiereDate" key of the current
        season. Since seasons are indexed by 0 in the list, we have
        to subtract 1 from our actual season number while accessing
        the key's value.
        """
        premiere = self.info["_embedded"]["seasons"][self.season - 1]["premiereDate"]
        self.premiere = utils.date_from_string(premiere, Show.delay)

    def get_end(self):
        """Get the current season's end date.

        Inside the "_embedded" data is information about the seasons.
        We want the value of the "endDate" key of the current season.
        Since seasons are indexed by 0 in the list, we have to subtract
        1 from our actual season number while accessing the key's
        value.
        """
        end = self.info["_embedded"]["seasons"][self.season - 1]["endDate"]
        self.end = utils.date_from_string(end, Show.delay)

    def get_episodes(self):
        """Get the airing dates of the season's episodes.

        Inside the "_embedded" data is information about the episodes.
        First we filter out the episodes list. Then we iterate through
        the list in reverse, adding episode (key) and airing date
        (value) pairs to the dictionary. We stop at the first episode
        that's not part of our current season.

        Example dictionary:
        {"1": "2016-05-05", "2": "2016-05-12"}
        """
        # filtered out list containing only the episode dicts
        eps = self.info["_embedded"]["episodes"]

        episodes = {}
        for epi in reversed(eps):
            if epi["season"] == self.season:
                # sometimes the API has incomplete data and the airdate
                # is just an empty string. self.episodes_to_date()
                # won't work with that, so we assign the ending date
                # as the episode's airing date, just to have something.
                if not epi["airdate"]:
                    episodes[epi["number"]] = self.end
                else:
                    episodes[epi["number"]] = epi["airdate"]
            else:
                break

        self.episodes = self.episodes_to_date(episodes)

    def get_status(self):
        """Get the show's airing status.

        Determines the show's current status based on certain
        conditions. A show can be:
        airing  - a season is currently airing
        soon    - a season is premiering soon
        ended   - the season has ended (no info about a new season yet)
        done    - the show has ended
        new     - a new episode is airing today
        last    - the last episode is airing today

        unknown - if nothing else can be determined (usually for
                  shows that are unknown or when ran without an
                  internet connection with no cached file)
        """
        if self.end:
            # if today's date is past the last episode's date,
            # the show has ended
            if (self.end < TODAY):
                self.status = "ended"
                return
            # if today is the same day as the end date, the season's
            # last episode is airing
            elif TODAY == self.end:
                self.status = "last"
                return

        # if today's date is found inside a show's episode list
        # a new episode is out
        if self.episodes:
            if TODAY in self.episodes.values():
                self.status = "new"
                return

        if self.info:
            # if the show's status from the API data is "Ended" it means
            # it has ended
            if self.info["status"] == "Ended":
                self.status = "done"
                return
            # if the show's status from the API data is "TBD" it means
            # the season has ended, but not the show
            elif self.info["status"] == "To Be Determined":
                self.status = "ended"
                return

        if self.premiere:
            # if today's date is between the premiere and end date
            # the show is currently airing
            if self.premiere < TODAY < self.end:
                self.status = "airing"
                return
            # if the premiere date is in the future, the show will
            # start airing soon
            elif self.premiere > TODAY:
                self.status = "soon"
                return

        # if the status couldn't be determined by now, it's Unknown
        self.status = "Unknown"

    def episodes_to_date(self, dictionary):
        """Returns a dictionary with proper dateobjects.

        Takes a dictionary as an argument (the episodes dictionary
        which contains episode number and airing date pairs). Goes
        through each date (which is a string in the initial dict) and
        creates a dateobject from it. It appends each key,value pair
        to a new dictionary and returns it.
        """
        new_dictionary = {}
        for number, date in dictionary.items():
            new_dictionary[number] = utils.date_from_string(date, Show.delay)
        return new_dictionary

    def episodes_to_string(self, dictionary):
        """Returns a dictionary with strings from dateobjects.

        Does the opposite of episodes_to_date(). Used to create
        strings from dateobjects, because json.dump() cannot serialize
        dateobjects.
        """
        new_dictionary = {}
        for number, dateobject in dictionary.items():
            new_dictionary[number] = utils.string_from_date(dateobject, Show.delay)
        return new_dictionary

    def get_last_episode(self):
        """Get the last aired episode."""
        if not self.episodes:
            return
        # if the show has ended, the last episode's number will be
        # the number of total episodes
        if self.end < TODAY:
            self.last_episode = len(self.episodes)
            return
        # compares today's week number to the weeknumbers in the
        # list of episodes. the one that matches is the last aired
        # episode
        for ep, date in self.episodes.items():
            if TODAY.isocalendar()[1] == date.isocalendar()[1]:
                self.last_episode = ep

        # ugly hack to fix error when an double episode aired and
        # thje above way doesn't determine the correct last episode.
        # this is why all of this sucks and needs to be rewritten to
        # be simpler
        # just die in my sleep already
        if not self.last_episode:
            for ep, date in self.episodes.items():
                if TODAY.isocalendar()[1] == (date.isocalendar()[1] + 1):
                    self.last_episode = ep

    def update(self):
        """Updates the show's information from the web.

        Runs the various methods which update the show's data.
        """
        self.fetch_show_info()
        if not self.info:
            return
        self.get_season()
        self.get_premiere()
        self.get_end()
        self.get_episodes()
        # update the status according to the new data
        self.get_status()
        self.get_last_episode()

    def dump_data(self):
        """Return a dictionary with the show's data.

        If there is no self.info, it dumps an "empty" dictionary
        with only the show's title.
        """
        if not self.info:
            data_dict = {
                "title": self.title,
                "season": None,
                "premiere": "",
                "end": "",
                "episodes": {}
                }
        else:
            data_dict = {
                "title": self.title,
                "season": self.season,
                "premiere": utils.string_from_date(self.premiere, Show.delay),
                "end": utils.string_from_date(self.end, Show.delay),
                "episodes": self.episodes_to_string(self.episodes)
                }
        return data_dict

# see __init__.py download_shows() comment
#    def check_episodes_download(self):
#        """Return tuple with episodes that are airing today.
#
#        The TVMaze API's "episodesbydate" returns info about which
#        episodes are airing today. We append every episode that aired
#        to the "new_episodes" list in form of a tuple containing
#        the show's title, season and episode number.
#
#        If Show.delay is True, we have to pass yesterday's date to
#        the API query to get yesterday's results today.
#        """
#        if Show.delay:
#            date = TODAY - datetime.timedelta(days=1)
#        else:
#            date = TODAY
#
#        self.fetch_show_info()
#        show_id = self.info["id"]
#
#        search_query = "{}/shows/{}/episodesbydate?date={}".format(
#            API_URL,
#            show_id,
#            date.isoformat()
#            )
#        response = utils.get_URL_string(search_query)
#        info = json.loads(response)
#
#        new_episodes = []
#        for new_episode in info:
#            new_episodes.append(
#                (self.title, new_episode["season"], new_episode["number"])
#                )
#
#        return new_episodes
