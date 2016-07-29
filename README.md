# showsho
An easy and simple way to keep track of your favourite TV shows.

#### How to install
Run `$ python setup.py install`   
Arch users can use the included PKGBUILD

#### How to use
`$ showsho [-h] [-d] [-a] [-p DAYS] FILE`

`-d` or `--download` will print a magnet link for the torrent.  
`-a` or `--airing` will only display currently airing shows.  
`-p` or `--delay` adds a delay in days to the premiere date. See **Notes** for more information.  

The torrent information (magnet links) are fetched from [torrentz.com](http://www.torrentz.com/).
**Note:** downloading torrent files doesn't work currently, since torcache.net
is down. As a workaround, a magnet link is being printed which can be used
to download the torrent.

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

#### Screenshots
![](http://s23.postimg.org/gdguqt997/2016_03_23_16_13_28.png)

![](http://s23.postimg.org/l0mwskwm3/2016_03_23_16_14_51.png)

#### Notes
- Depending on your timezone, it is probably recommended to add an additional day to the show's premiere/airing dates with the `-p` flag. For example: if you're in UTC+2 and watching a show broadcast in the US, you don't want to get notified a day before it actually airs, but the day after. Downloading torrents will also benefit from that, since they might not be instantly available on the same day (night).
- **Remember:** While downloading .torrent files (or using the bittorrent protocol for downloads) isn't illegal by itself, you shouldn't download unauthorized copies of media.
