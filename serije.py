import datetime
import json

TODAY = datetime.date.today()

WARNING = """Unknown number of episodes. Please edit the show,
or else notifications about the show ending won't work."""

class Color:
    GREEN = "\033[32m"
    RED = "\033[31m"
    L_GREEN = "\033[1;32m"
    L_BLUE = "\033[1;34m"
    L_RED = "\033[1;31m"

def colorize(text, color):
    return "{}{}\033[0m".format(color, text)

def getDateObject(date_string):
    # returns a date object for the given date string; format YYYY-MM-DD
    yyyy, mm, dd = date_string.split("-")
    date_object = datetime.date(int(yyyy), int(mm), int(dd))
    return date_object

def getDay(date_object):
    # returns the name of the day of a date object like: Mon, Tue, Wed
    return date_object.strftime("%a")

def getDateString(date_object):
    # returns a string from a date in the format YYYY-MM-DD
    if date_object:
        return date_object.strftime("%Y-%m-%d")
    else:
        return date_object

def formatNumber(number):
    # adds a leading zero to the episode/season if necessary
    if len(str(number)) == 1:
        return "0{}".format(number)
    else:
        return str(number)

def setTitle():
    # gets the show's title, used during adding or editing a show
    print("Show's title:")
    title = input(">")
    return title

def setSeason():
    # gets the season number, used during adding or editing a show
    print("Season number:")
    # input validation
    while True:
        season = input(">")
        try:
            int(season)
            break
        except ValueError:
            print("Invalid choice, must enter a number, try again.")
    return int(season)

def setDate():
    # gets the premiere date, used during adding or editing a show
    print("Season's premiere date in the YYYY-MM-DD format.")
    print("Leave blank if unknown.")
    # input validation
    while True:
        date = input(">")
        if date == "":
            return None

        try:
            getDateObject(date)
            break
        except (ValueError, TypeError):
            print("Invalid choice, enter it in the proper format.")

    return date

def setEpisodes():
    # gets the number of episodes in the season,
    # used during adding or editing a show
    print("Number of episodes the season has. Leave blank if unknown.")
    # input validation
    while True:
        episodes = input(">")
        if episodes == "":
            return None

        try:
            int(episodes)
            break
        except ValueError:
            print("Invalid choice, must enter a number, try again.")

    return int(episodes)

def printAiring(show):
    # prints shows which are currently airing
    info = "{}\nEpisode: S{}E{}".format(
        colorize(show.title, Color.L_GREEN),
        formatNumber(show.season),
        formatNumber(show.latest_episode)
        )
    # adds a notification if a new episode is out
    if show.new_episode:
        info += " {}".format(colorize("New episode!", Color.L_BLUE))
    # warning if the number of episodes for the season is missing
    if not show.episodes:
        info += "\n{}".format(colorize(WARNING, Color.L_RED))
    print(info)

def printAiringSoon(show):
    # prints shows which have a season premier date set
    info = "{}\nSeason {} premiere on: {}".format(
        colorize(show.title, Color.GREEN),
        formatNumber(show.season),
        show.premiere.strftime("%a, %d. %b")
        )
    # warning if the number of episodes for the season is missing
    if not show.episodes:
        info += "\n{}".format(colorize(WARNING, Color.L_RED))
    print(info)

def printEnded(show):
    # prints shows which have ended airing
    info = "{}\nLast episode: S{}E{}".format(
        colorize(show.title, Color.RED),
        formatNumber(show.season),
        formatNumber(show.episodes)
        )
    print(info)

def printNotAiring(show):
    # prints shows which aren't airing and have no premiere date set
    info = "{}\nSeason {} premiere unknown".format(
        show.title,
        formatNumber(show.season))
    print(info)

class Show:
    def __init__(self, title, season, premiere, episodes):
        self.title = title
        self.season = season
        self.premiere = premiere
        self.episodes = episodes

        # default fallback values, might get overwritten by methods
        self.airing = False
        self.latest_episode = 0
        self.ended = False
        self.new_episode = False

        if premiere:
            self.premiere = getDateObject(premiere)
            self.setAiring()
            if self.airing:
                self.setLatestEpisode()
                self.setNewEpisode()
                if episodes:
                    self.setEnded()

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
        if getDay(TODAY) == getDay(self.premiere):
            self.new_episode = True

def showShows(shows):
    # prints all the shows out with color-coded information

    if len(shows) < 1:
        print("No shows added. Use 'add' to start keeping track.")
        return

    # prints info about each show based on attributes; sorts by title
    for show in sorted(shows, key=lambda show: show.title):
        print("--------------------------")
        if show.ended:
            printEnded(show)
        elif show.airing:
            printAiring(show)
        elif show.premiere:
            printAiringSoon(show)
        else:
            printNotAiring(show)
    print("--------------------------")

def addShow():
    # returns a Show() object with the entered data

    title = setTitle()
    season = setSeason()
    date = setDate()
    episodes = setEpisodes()
    print("Show successfully added.")
    return Show(title, season, date, episodes)

def editShow(shows):
    # edits a show
    # TODO: maybe change this to not use deletion;
    #       add a Show.update() method, and move everything from
    #       Show().__init__ to it. Then call that method in here,
    #       instead of deleting the Show() object and replacing it with
    #       a new one.

    print("Name of the show to edit:")
    show_to_edit = input(">")

    # TODO: find a better way to search for show and edit it,
    #       without iterating twice through the show list
    if show_to_edit not in [show.title for show in shows]:
        print("Show not found.")
        return

    for show in shows:
        if show.title == show_to_edit:
            shows.remove(show)

            title = setTitle()
            season = setSeason()
            date = setDate()
            episodes = setEpisodes()

            shows.append(Show(title, season, date, episodes))
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

def loadShows(shows):
    # returns a list containing Show() objects

    path = input(">")
    try:
        file_obj = open(path, "r")
        JSON_data = json.load(file_obj)
        file_obj.close()
        print("Shows loaded.")
    except FileNotFoundError:
        print("No such file: '{}'".format(path))
        return shows

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
            getDateString(show.premiere),
            show.episodes
            ]

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

def main():
    shows = []

    while True:
        choice = input(">")

        if choice == "show":
            showShows(shows)
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
        elif choice == "quit":
            break

if __name__ == "__main__":
    main()
