# Twitter Sentiment Analysis

By:
* Vishnu Nair ([@NairVish](https://github.com/NairVish))
* Keith Low ([@keithlowc](https://github.com/keithlowc))

A series of scripts that downloads tweets for a list of cities (in this case, northeastern U.S. cities) using a particular
query, cleans them, computes an average sentiment for each city's tweets, and plots these average sentiment scores on a
bubble map of the northeastern U.S.

## Screenshots

The following sentiment maps were created using tweets pulled during the evening of October 6, 2018 using the query **"trump."**


_Metro NYC area_

![Sentiment map over the metro NYC area](https://raw.githubusercontent.com/NairVish/tweet-sentiment-analysis/master/demo/metro-nyc.png "NYC sentiment map for the 'trump' query (10/06/18)")

_Northeast U.S. (PA, NJ, NY, CT, RI, MA, VT, NH, ME)_

![Sentiment map over the Northeastern U.S.](https://raw.githubusercontent.com/NairVish/tweet-sentiment-analysis/master/demo/ne-us.png "NE U.S. sentiment map for the 'trump' query (10/06/18)")

## Interactive Demo

The actual heatmap output for the above query can be found [here](https://nairvish.github.io/tweet-sentiment-analysis/).

## Structure

* **`shp_to_csv.py`**: Forms the list of cities to get tweets for by parsing shapefile data from the USGS and Gazetteer
data from the U.S. Census Bureau. The output is a CSV file of all of the cities and their respective states, lat/lons, and
size.
    * Specifically, we use the [ESRI northeast cities shapefiles for the Long Island Sound ArcView project area](https://cmgds.marine.usgs.gov/publications/of02-002/data/basemaps/cities.htm) 
    from the U.S. Geological Survey to get a list of cities in the Northeast, and the [2010 Census Gazetteer Files](https://www.census.gov/geo/maps-data/data/gazetteer2010.html) from the U.S. Census
    Bureau (specifically `places` data for each of the states in question) to get each city's size.
    * From the above processing, we attempt to get data for a total of 606 cities/towns/etc.
* **`grab_data.py`**: Connects to the Twitter API (standard tier) to grab tweets for each specified city.
    * **`keys.py`** holds the appropriate API keys.
    * To allow for quick processing, we only download up to 100 tweets. (Though, of course, more will be useful.)
* **`json_parser.py`**: Cleans the tweet data (links, some special characters, etc.) and removes duplicates.
* **`analyze_data.py`**: Computes sentiments on the cleaned tweet data (using [VADER Sentiment Analysis](https://github.com/cjhutto/vaderSentiment)),
plots them on a bubble map (using [Folium](https://github.com/python-visualization/folium)), and saves the resultant map in an html file.
* **`main.py`**: A simple script that executes almost all of the above in one go.
