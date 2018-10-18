import twitter
import csv
import json
import os
import keys
from time import sleep

api = twitter.Api(consumer_key= keys.CONSUMER_KEY,
                  consumer_secret= keys.CONSUMER_SECRET,
                  access_token_key= keys.ACCESS_TOKEN_KEY,
                  access_token_secret= keys.ACCESS_TOKEN_SECRET,)

class TwitterData:
    def __init__(self, csv_file, QUERY):
        self.QUERY = QUERY
        self.csv_file_to_open = csv_file


    def get_radius(self, city_type):
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
        with open(self.csv_file_to_open, 'r') as city_list_file:
            city_csv = csv.reader(city_list_file)
            # next(city_csv, None)
            for row in city_csv:

                file_name = "%s.json" % "-".join(row[0].lower().split(" "))
                full_file_path = os.path.join("tweets", file_name)
                if os.path.exists(full_file_path):
                    print("Tweets for %s exist!" % row[0])
                    continue

                results = api.GetSearch(raw_query="q=%s&geocode=%s,%s,%s&count=100&tweet_mode=extended"
                                                  % (self.QUERY, row[2], row[1], self.get_radius(row[3])))
                print(row[0])
                print(row[3])
                print(results)
                text_results = []
                for t in results:
                    # print(t)
                    if t.full_text.startswith("RT @"):
                        text_results.append(t.retweeted_status.full_text)
                    else:
                        text_results.append(t.full_text)
                with open(full_file_path, 'w') as input_file:
                    json.dump(text_results, input_file)
                print("Grabbed tweets for %s." % row[0])
                sleep(5.1) # throttle requests

if __name__ == '__main__':
    x = TwitterData('cities.csv','obama')
    x.gather_data()