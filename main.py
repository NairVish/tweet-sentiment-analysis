from json_parser import CleanData
from analyze_data import SentimentAnalyzer
from grab_data import TwitterData
import argparse
import os
import glob

parser = argparse.ArgumentParser()
parser.add_argument('-q', '--query',
                    help='Type whatever you are looking for. This can be an @ mention, a hashtag, or any other term.',
                    type=str, required=True)
args = parser.parse_args()

original_directory = os.getcwd()
if not os.path.exists(os.path.join(original_directory, "cities.csv")):
    print("The cities list does not exist. Run shp_to_csv.py to generate it.")
    os._exit(1)

print('Gathering data')
data = TwitterData('cities.csv', args.query)
data.gather_data()

print('Cleaning data')
tweet_directory = os.path.join(os.getcwd(), 'tweets')
os.chdir(tweet_directory)

for file in os.listdir(os.getcwd()):
    if not file.endswith(".json") or file.startswith("output-"): continue
    print("\tCleaning {}".format(file))
    x = CleanData(file, 'output-' + file)
    x.clean_it()

os.chdir(original_directory)
print('Starting sentiment analyzer and plotter')

x = SentimentAnalyzer('cities.csv')
x.run_it()
