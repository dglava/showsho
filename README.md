# showsho
An easy and simple way to keep track of your favourite TV shows.

#### How to install
Run `$ python setup.py install`   
There are no external dependencies outside of the standard Python library   
Arch users can use the included PKGBUILD

#### How to use
`$ showsho [-h] [-d] [-a] [-p] FILE`

`-d` or `--download` will download the latest episode (if airing today).  
`-a` or `--airing` will only display currently airing shows.  
`-p` or `--delay` adds a delay in days to the premiere date. See **Notes** for more information.  
`FILE` should be a text file containing one show's name per line.

It uses the [TVMaze API](http://www.tvmaze.com/api) to get data about shows.
All the torrent information is downloaded from [btdb.in](https://btdb.in).

#### Screenshots
![](https://s22.postimg.org/h546cqe01/2016_10_20_13_27_47.png)

![](https://s22.postimg.org/pbw64b42p/2016_10_20_13_28_40.png)

#### Notes
- Depending on your timezone, it is probably recommended to use the `-p` flag. For example: if you're in UTC+2 and watching a show broadcast in the US, you don't want to get notified a day before it actually airs, but the day after. Downloading torrents will also benefit from that, since they might not be instantly available on the same day (night).
- **Remember:** While downloading .torrent files (or using the bittorrent protocol for downloads) isn't illegal by itself, you shouldn't download unauthorized copies of media.
