from json_parser import CleanData
from analyze_data import SentimentAnalyzer
from grab_data import TwitterData
import argparse
import os
import glob

parser = argparse.ArgumentParser()
parser.add_argument('query', help='Type whatever you are looking for. IE: obama', type= str)
args = parser.parse_args()

original_directory = os.getcwd()

print('Gathering data')
data = TwitterData('cities.csv',args.query)
data.gather_data()

print('Cleaning data')
directory = os.getcwd() + '/tweets'
new_directory = directory

os.chdir(directory)

for file in glob.glob('*.json'):
	file_name = file
	new_directory_file = directory + '/' + file
	print(new_directory_file)
	x = CleanData(new_directory_file, 'output-' + file_name)
	x.clean_it()

os.chdir(original_directory)

print('Starting setiment analyzer and plotter')

x = SentimentAnalyzer('cities.csv')
x.run_it()