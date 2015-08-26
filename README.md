# showsho
An easy and simple way to keep track of your favourite TV shows.

#### How to install
Run `python setup.py`

#### How to use
To display the shows:  
`$ showsho shows.json`  
To download the latest episodes use the `-d` or `--download` flag:  
`$ showsho -d shows.json`  
To delay the airing dates for a couple of days, use the `-p` or `--delay` flag. See **Notes** for more info.  
`$ showsho -p 1 shows.json`

The list is color coded for convenience.
- Shows that are airing are bright green
- Shows with a known premiere date are green
- Shows which have ended are red
- Shows with unknown premiere dates are neutral

#### Show file layout
They're JSON laid out as shown below.  
```
{
"show name": [season, "date", episodes]
}
```
`show name`: string with the show's name  
`season`: integer with the show's current season  
`date`: string with the date of the show's premiere in YYYY-MM-DD format. Can be null if unknown.  
`episodes`: integer with the number of episodes the season has. Can be null if unknown, but only if `date` is also null. If you set this to null while date has a proper value, you'll get an error while trying to load your file.  


Example file:  
```
{
"True Detective": [2, "2015-06-22", 8],
"Rectify": [3, "2015-07-10", 6],
"Archer": [7, null, null],
"Better Call Saul": [2, null, null],
"Homeland": [5, "2015-10-05", 12],
"It's Always Sunny in Philadelphia": [11, null, null]
}
```

#### Notes
- Depending on your timezone, it is probably recommended to add an additional day to the show's premiere/airing dates with the `-d` flag. For example: if you're in UTC+2 and watching a show broadcast in the US, you don't want to get notified a day before it actually airs, but the day after. Downloading torrents will also benefit from that, since they might not be instantly available on the same day (night).
- **Remember:** While downloading .torrent files (or using the bittorrent protocol for downloads) isn't illegal by itself, you shouldn't download unauthorized copies of media.
