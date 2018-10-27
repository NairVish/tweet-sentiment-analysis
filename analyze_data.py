"""
The sentiment analyzer and plotter.

Analyzes sentiments on cleaned tweet data, plots sentiments on a bubble map, and saves the bubble map as an html file.
"""
import csv
import json
import os

import folium
import pandas as pd
from colour import Color
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer


class TweetSentimentAnalyzer:
    """
    The sentiment analyzer and plotter.
    """
    HEATMAP_OUTPUT_NAME = "heatmap.html"

    def __init__(self, cities_csv_file):
        """
        Initializes the class.
        :param cities_csv_file: The csv file that holds the list of cities.
        """
        self.cities_csv_file = cities_csv_file
        self.sentiment_analyzer = SentimentIntensityAnalyzer()
        self.fill_gradient = list(Color("red").range_to(Color("Green"), 1001))

    @staticmethod
    def mean(numbers):
        """
        Calculates the mean of a list of numbers.
        :param numbers: The input list of numbers.
        :return: The mean.
        """
        return float(sum(numbers)) / len(numbers)

    def run_it(self):
        """
        Runs the sentiment analyzer.
        """
        all_cities_scores = []

        # Open the csv file with the list of cities...
        with open(self.cities_csv_file, 'r') as input_cities_csv:
            cities_csv = csv.reader(input_cities_csv)

            # For each row in the csv (i.e., for each city in the list)...
            for row in cities_csv:
                print("\tProcessing tweets for {}.".format(row[0]))

                # Establish the name of the input file with the cleaned tweets
                file_name = "output-{}.json".format("-".join(row[0].lower().split(" ")))
                full_file_path = os.path.join("tweets", file_name)

                # Open the JSON with the cleaned tweets
                with open(full_file_path, 'r') as city_tweets:
                    all_tweets = json.load(city_tweets)
                    all_scores = []

                    # If the file is empty, then we have no tweets to process. Simply continue.
                    if not all_tweets:
                        print("\tNo tweets to process for {}.".format(row[0]))
                        continue

                    # Else for each tweet in the file...
                    for tweet in all_tweets:
                        # Calculate a sentiment score
                        vs = self.sentiment_analyzer.polarity_scores(tweet)
                        # Add the compound score to the list of scores we already have for this city
                        all_scores.append(vs["compound"])

                    # Average all of the compound scores
                    avg_score = self.mean(all_scores)

                    # Grab the necessary info for this city:
                    # [lon, lat, adjusted compound score, city_name, city_type, num_tweets, city_radius]
                    l = [row[1], row[2], (avg_score + 1) / 2, row[0], row[3], len(all_tweets), row[5]]
                    all_cities_scores.append(l)
                    # print(l)

        # print("Final results: " + all_cities_scores)

        # Create a new csv for all of the results...
        with open("results.csv", 'w') as results_csv_file:
            results_csv = csv.writer(results_csv_file)
            results_csv.writerow(["lon", "lat", "score", "city", "area_type", "num_tweets", "city_radius"])
            for score_set in all_cities_scores:
                results_csv.writerow(score_set)

        # Use the csv created in the last step to establish a data frame for the data
        score_df = pd.read_csv('results.csv', sep=',')
        score_df["lat"] = score_df["lat"].astype(float)
        score_df["lon"] = score_df["lon"].astype(float)
        score_df["num_tweets"] = score_df["num_tweets"].astype(int)
        score_df["city_radius"] = score_df["city_radius"].astype(float)

        # print(score_df)

        # Invoke Folium to create a map using Mapbox Bright tiles, centered on NYC
        hmap = folium.Map(location=[40.71, -74.0], zoom_start=10, tiles="Mapbox Bright")

        # For each city's data in the data frame...
        for i in range(0, len(score_df)):
            # Use the sentiment score to calculate the appropriate color
            # (i.e., the correct position on the pre-established gradient)
            gradient_score = int(round(score_df.iloc[i]['score'] * 1000))

            # Create a circle/bubble
            folium.Circle(
                location=[score_df.iloc[i]['lat'], score_df.iloc[i]['lon']],    # At the specified lat/lon
                popup="{} - {} tweets retrieved - Compound: {:.2f}".format(           # With a popup specifying the city's name, # tweets, and avg sentiment score
                    score_df.iloc[i]['city'], score_df.iloc[i]['num_tweets'], score_df.iloc[i]['score']),
                radius=score_df.iloc[i]['city_radius'] * 1400,                  # Calculate a relative radius using the radius data
                color=self.fill_gradient[gradient_score].hex_l,                 # Use the gradient score to color the bubble's outline appropriately
                fill=True,                                                      # Fill the bubble...
                fill_color=self.fill_gradient[gradient_score].hex_l             # with the same color too
            ).add_to(hmap)                                                      # Add this bubble to the previously-created map

        # Save the heatmap
        hmap.save(self.HEATMAP_OUTPUT_NAME)
        print("\tThe map was succesfully plotted as: {}".format(self.HEATMAP_OUTPUT_NAME))


if __name__ == '__main__':
    x = TweetSentimentAnalyzer('cities.csv')
    x.run_it()
