# showsho
An easy and simple way to keep track of your favourite TV shows.

#### How to install
Run `python setup.py`

#### How to use
`$ showsho`  
Or include a file with the *-f* flag:  
`$ showsho -f /path/to/shows.json`  

Now you can list all the shows with the `show` command:  
![](http://s3.postimg.org/go5iulvw3/2015_08_16_142044_644x411_scrot.png)
The list is color coded for convenience.  
- Shows that are airing are bright green  
- Shows with a known premiere date are green  
- Shows which have ended are red  
- Shows with unknown premiere dates are neutral  

To download a torrent, use the `down` command. It will only work if there's a new episode out.  
![](http://s3.postimg.org/puj845bqr/2015_08_16_143041_644x411_scrot.png)  
You can now use your favourite bittorrent client to actually download the episode.  
Torrent searching and downloading is done with the help of the [Strike API](https://getstrike.net/api/).  

You can `save` and `load` show files.  
To add a new show or edit an existing one from within showsho, use `add` and `edit`.  
For a list of all the commands type `help`. To quit use `quit`.  

#### Show file layout
They're JSON laid out as shown below.  
```
{
"show name": [season, "date", episodes],
}
```
`show name`: string with the show's name  
`season`: integer with the show's current season  
`date`: string with the date of the show's premiere in YYYY-MM-DD (ISO 8601) format. Can be null if unknown.  
`episodes`: integer with the number of episodes the season has. Can be null if unknown.  

#### Notes
- Depending on your timezone, it is probably recommended to add an additional day to a show's premiere/airing date. For example: if you're in UTC+2 and watching a show broadcast in the US, you don't want to get notified a day before it actually airs, but the day after.  
- **Remember:** While downloading .torrent files (or using the bittorrent protocol for downloads) isn't illegal by itself, you shouldn't download unauthorized copies of media.
