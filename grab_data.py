"""
The Twitter data downloader.

Downloads and stores tweet data for each city in the specified csv file.
"""
import csv
import json
import os
from time import sleep

import twitter

import keys


class TwitterData:
    """
    The Twitter data downloader.
    """

    def __init__(self, cities_csv_file, QUERY):
        """
        Initializes the class.
        :param cities_csv_file: The csv file that holds the list of cities.
        :param QUERY: The query to search for.
        """
        self.QUERY = QUERY
        self.cities_csv_file = cities_csv_file
        self.api = twitter.Api(consumer_key=keys.CONSUMER_KEY,
                               consumer_secret=keys.CONSUMER_SECRET,
                               access_token_key=keys.ACCESS_TOKEN_KEY,
                               access_token_secret=keys.ACCESS_TOKEN_SECRET)

    @staticmethod
    def get_radius(city_type):
        """
        Determines a generic radius for a geographical entity depending the on the type of the entity.
        :param city_type: The type.
        :return: The generic radius in "##mi" form.
        """
        if city_type == "city":
            return "10mi"
        elif city_type == "census designated place":
            return "2mi"
        elif city_type == "village" or city_type == "town":
            return "3mi"
        elif city_type == "borough":
            return "7mi"
        elif city_type == "city (remainder)":
            return "4mi"

    def gather_data(self):
        """
        Gathers the data.
        """
        # Open the csv file with the list of cities...
        with open(self.cities_csv_file, 'r') as city_list_file:
            city_csv = csv.reader(city_list_file)

            # For each row in the csv (i.e., for each city in the list)...
            for row in city_csv:
                # Establish the name of the output file for the downloaded tweets
                file_name = "%s.json" % "-".join(row[0].lower().split(" "))
                full_file_path = os.path.join("tweets", file_name)

                # If a file with this name already exists...
                if os.path.exists(full_file_path):
                    # Then skip this city, because we probably already have tweets for this city
                    print("\t\tTweets for %s already exist!" % row[0])
                    continue

                # Contact the Twitter API to get all of the tweets for this city
                # Using: the query, the lat+lon+radius to search, a maximum of 100 tweets in the response, and getting
                #   all possible data for each tweet
                results = self.api.GetSearch(raw_query="q=%s&geocode=%s,%s,%s&count=100&tweet_mode=extended"
                                                       % (self.QUERY, row[2], row[1], self.get_radius(row[3])))

                print("\t\t{} - {}\n\t\t\t{}".format(row[0], row[3], results))

                text_results = []
                # For each tweet in the response...
                for t in results:
                    # If this is a retweet...
                    if t.full_text.startswith("RT @"):
                        # Grab the retweet, because if an individual retweets another user's status then it can
                        # be assumed that the retweeted status reflects the individual's sentiment on the topic
                        text_results.append(t.retweeted_status.full_text)
                    else:
                        # Grab the top-level tweet
                        text_results.append(t.full_text)

                # Dump all of the grabbed tweets into a JSON file...
                with open(full_file_path, 'w') as input_file:
                    json.dump(text_results, input_file)
                print("\t\t\tGrabbed tweets for %s." % row[0])

                # Throttle requests to the Twitter API (user auth)
                # Twitter limits to 180 requests/15-minute window, which equals 1 request every 5 seconds
                # See: https://developer.twitter.com/en/docs/basics/rate-limits.html
                sleep(5.1)  # throttle requests


if __name__ == '__main__':
    x = TwitterData('cities.csv', 'obama')
    x.gather_data()
