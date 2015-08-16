import datetime
import json

from showsho import utils

TODAY = datetime.date.today()

WARNING = (
"""Unknown number of episodes. Please edit the show,
or else notifications about the show ending won't work."""
)

HELP = (
"""show:\tprints the shows out with their information
down:\tdownloads torrents for shows which have a new episode out
add:\tadds a new show to keep track of
edit:\tedit an existing show
delete:\tdelete a show
load:\tload file containing shows
save:\tsave shows to a file

help:\tprint this help description
quit:\tdestroy the universe..."""
)

class Show:
    def __init__(self, title, season, premiere, episodes):
        self.update(title, season, premiere, episodes)

    def update(self, title, season, premiere, episodes):
        """Sets and gets all the attributes; used during editing too"""
        self.title = title
        self.season = season
        self.premiere = premiere
        self.episodes = episodes

        # default fallback values, might get overwritten by methods
        self.airing = False
        self.latest_episode = 0
        self.ended = False
        self.new_episode = False
        self.last_episode = False

        if premiere:
            self.premiere = utils.getDateObject(premiere)
            self.setAiring()
            if self.airing:
                self.setLatestEpisode()
                self.setNewEpisode()
                if episodes:
                    self.setEnded()
                    self.setLastEpisode()

    def setLatestEpisode(self):
        """Gets episode number based on the season's start date"""
        difference = TODAY - self.premiere
        # days since premier // 7 = weeks = episodes passed;
        # adds 1 because episodes are indexed from 1 and not 0
        self.latest_episode = ((difference.days // 7) + 1)

    def setAiring(self):
        """Checks if the show is currently airing"""
        if self.premiere <= TODAY:
            self.airing = True

    def setEnded(self):
        if self.latest_episode > self.episodes:
            self.ended = True

    def setNewEpisode(self):
        """Checks if a new episode is out today"""
        if utils.getDay(TODAY) == utils.getDay(self.premiere):
            self.new_episode = True

    def setLastEpisode(self):
        """Checks if the latest episode is the last one"""
        if self.latest_episode == self.episodes:
            self.last_episode = True

def showShows(shows):
    # prints all the shows out with color-coded information

    if len(shows) < 1:
        print("No shows added. Use 'add' to start keeping track.")
        return

    # prints info about each show based on attributes; sorts by title
    for show in sorted(shows, key=lambda show: show.title):
        print("--------------------------")
        if show.ended:
            utils.printEnded(show)
        elif show.airing:
            utils.printAiring(show)
        elif show.premiere:
            utils.printAiringSoon(show)
        else:
            utils.printNotAiring(show)

def downloadShows(shows):
    # downloads a torrent file for shows which have a new episode

    if len(shows) < 1:
        print("No shows added. Use 'add' to start keeping track.")
        return

    # used to display a message if no shows are available for download
    no_shows_to_download = True

    for show in shows:
        if show.new_episode:
            no_shows_to_download = False

            torrents = utils.getTorrents(show)
            torrent_hash, torrent_title = utils.chooseTorrent(torrents)
            utils.downloadTorrent(torrent_hash, torrent_title)

    if no_shows_to_download:
        print("No new episodes out. Nothing to download.")

def addShow():
    # returns a Show() object with the entered data

    title = utils.setTitle()
    season = utils.setSeason()
    date = utils.setDate()
    episodes = utils.setEpisodes()
    print("Show successfully added.")
    return Show(title, season, date, episodes)

def editShow(shows):
    # edits a show

    print("Name of the show to edit:")
    show_to_edit = input(">")

    # TODO: find a better way to search for show and edit it,
    #       without iterating twice through the show list
    if show_to_edit not in [show.title for show in shows]:
        print("Show not found.")
        return

    for show in shows:
        if show.title == show_to_edit:
            title = utils.setTitle()
            season = utils.setSeason()
            date = utils.setDate()
            episodes = utils.setEpisodes()

            show.update(title, season, date, episodes)
            print("Show successfully edited.")

def deleteShow(shows):
    # removes a show

    print("Name of the show to delete:")
    show_to_delete = input(">")
    if show_to_delete not in [show.title for show in shows]:
        print("Show not found.")
        return
    else:
        for show in shows:
            if show.title == show_to_delete:
                shows.remove(show)
        print("Show deleted.")

def loadShows(old_shows, arg_path=None):
    # returns a list containing Show() objects

    # used only on startup if a filename was passed as an optional arg
    if arg_path:
        path = arg_path
    else:
        print("File to load:")
        path = input(">")

    try:
        file_obj = open(path, "r")
        JSON_data = json.load(file_obj)
        file_obj.close()
        print("Shows loaded.")
    except FileNotFoundError:
        print("No such file: '{}'".format(path))
        return old_shows

    # creates a Show() object for each entry, appends it to the list
    new_shows = []
    for title, data in JSON_data.items():
        new_shows.append(Show(
            title,
            data[0],
            data[1],
            data[2])
            )
    return new_shows

def saveShows(shows):
    # formats Show() objects into JSON and saves it to a file

    # converts a Show() object to an appropriate dictionary
    JSON_data = {}
    for show in shows:
        JSON_data[show.title] = [
            show.season,
            utils.getDateString(show.premiere),
            show.episodes
            ]

    print("Save as:")
    path = input(">")
    try:
        file_obj = open(path, "w")
        json.dump(JSON_data, file_obj)
        file_obj.close()
        print("Shows saved!")
    except PermissionError:
        print("Can't save, permission denied: '{}'".format(path))
    except FileNotFoundError:
        print("No such file or directory: '{}'".format(path))

def main(show_file):
    shows = []
    if show_file:
        shows = loadShows(shows, show_file)

    while True:
        choice = input(">")

        if choice == "show":
            showShows(shows)
        elif choice == "down":
            downloadShows(shows)
        elif choice == "add":
            shows.append(addShow())
        elif choice == "edit":
            editShow(shows)
        elif choice == "delete":
            deleteShow(shows)
        elif choice == "load":
            shows = loadShows(shows)
        elif choice == "save":
            saveShows(shows)
        elif choice == "help":
            print(HELP)
        elif choice == "quit":
            break
        else:
            print("Unknown command. Type 'help' for a list of commands")

        if choice != "quit":
            print()
