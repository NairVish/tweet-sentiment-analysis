import json
import csv
import os
import pandas as pd
import folium
from colour import Color
from time import sleep
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

class SentimentAnalyzer:
    def __init__(self,csv_file):
        self.csv_file = csv_file
        self.analyzer = SentimentIntensityAnalyzer()

    def mean(self, numbers):
        return float(sum(numbers)) / len(numbers)

    def run_it(self):
        fill_gradient = list(Color("red").range_to(Color("Green"), 1001))

        all_cities_scores = []

        with open(self.csv_file, 'r') as input_cities_csv:
            cities_csv = csv.reader(input_cities_csv)
            # next(cities_csv, None)
            for row in cities_csv:
                print(row[0])
                file_name = "output-%s.json" % "-".join(row[0].lower().split(" "))
                full_file_path = os.path.join("tweets", file_name)

                with open(full_file_path, 'r') as city_tweets:
                    all_tweets = json.load(city_tweets)
                    all_scores = []
                    if not all_tweets:
                        print("No tweets to process for %s" % row[0])
                        continue
                    for tweet in all_tweets:
                        vs = self.analyzer.polarity_scores(tweet)
                        all_scores.append(vs["compound"])
                    avg_score = self.mean(all_scores)
                    # all_cities_scores.append({"lat": row[1], "lon": row[2], "score": avg_score})
                    l = [row[1], row[2], (avg_score+1)/2, row[0], row[3], len(all_tweets), row[5]]
                    all_cities_scores.append(l)
                    print(l)

        # print("Final results: " + all_cities_scores)

        with open("results.csv", 'w') as results_csv_file:
            results_csv = csv.writer(results_csv_file)
            results_csv.writerow(["lon", "lat", "score", "city", "area_type", "num_tweets", "city_radius"])
            for score_set in all_cities_scores:
                results_csv.writerow(score_set)

        score_df = pd.read_csv('results.csv', sep=',')
        score_df["lat"] = score_df["lat"].astype(float)
        score_df["lon"] = score_df["lon"].astype(float)
        score_df["num_tweets"] = score_df["num_tweets"].astype(int)
        score_df["city_radius"] = score_df["city_radius"].astype(float)

        print(score_df)

        # Bc heatmap adds when zooming out.
        # Any way to average it instead?
        # Alternatives: Chloropleth, bubble map
        hmap = folium.Map(location=[40.71, -74.0], zoom_start=10, tiles="Mapbox Bright")

        # Add markers one by one on the map
        for i in range(0, len(score_df)):
            gradient_score = int(round(score_df.iloc[i]['score'] * 1000))
            folium.Circle(
                location=[score_df.iloc[i]['lat'], score_df.iloc[i]['lon']],
                # popup=score_df.iloc[i]['name'],
                popup="%s - %d tweets retrieved - Compound: %.2f" % (score_df.iloc[i]['city'], score_df.iloc[i]['num_tweets'], score_df.iloc[i]['score']),
                radius= score_df.iloc[i]['city_radius']*1400,
                # color=outline_gradient[gradient_score + 200].hex_l,
                color=fill_gradient[gradient_score].hex_l,
                fill=True,
                fill_color=fill_gradient[gradient_score].hex_l
            ).add_to(hmap)


        # heat_data = [[row['lat'],row['lon']] for index, row in score_df.iterrows()]
        # HeatMap(heat_data, max_val=2).add_to(hmap)

        hmap.save("heatmap.html")
        print("The map was succesfuly plotted as: heatmap.html")

if __name__ == '__main__':
    x = SentimentAnalyzer('cities.csv')
    x.run_it()