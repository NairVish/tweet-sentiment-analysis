import twitter
import csv
import json
import os
import keys
from time import sleep

QUERY = ""

api = twitter.Api(consumer_key=keys.CONSUMER_KEY,
                  consumer_secret=keys.CONSUMER_SECRET,
                  access_token_key=keys.ACCESS_TOKEN_KEY,
                  access_token_secret=keys.ACCESS_TOKEN_SECRET)


def get_radius(city_type):
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


with open('cities.csv', 'r') as city_list_file:
    city_csv = csv.reader(city_list_file)
    # next(city_csv, None)
    for row in city_csv:

        file_name = "%s.json" % "-".join(row[0].lower().split(" "))
        full_file_path = os.path.join("tweets", file_name)
        if os.path.exists(full_file_path):
            print("Tweets for %s exist!" % row[0])
            continue

        results = api.GetSearch(raw_query="q=%s&geocode=%s,%s,%s&count=100&tweet_mode=extended"
                                          % (QUERY, row[2], row[1], get_radius(row[3])))
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
