import json
import re
import os

'''
This class currently cleans json data for tweet sentiment analysis
Things that it parses for are: links , "\n", "\\" and "\""
As well as removing duplicates

Things to do: Remove unicode. Alternative solution to that is to copy and paste the values into https://codebeautify.org/jsonviewer
and it will clean it for you and format it correctly
'''


class CleanData:
    def __init__(self, json_file, output_json_file):
        self.json_file = json_file
        self.output_json_file = output_json_file

    def open_json(self, json_file):
        with open(json_file) as json_data_string:
            ds = json.load(json_data_string)
            print('The original size of ' + str(json_file) + ' is: \t' + str(len(ds)))
            return ds

    def write_json(self, json_file, data_to_dump):
        with open(json_file, 'w') as f:
            json.dump(data_to_dump, f)
            return json_file

    def remove(self, duplicate):
        final_list = []
        text = []
        pattern_to_eliminate = r"http\S+"
        for num in duplicate:
            if num not in final_list:
                final_list.append(num)
                list_one = [x.replace("\n", '') for x in final_list]
                list_two = [x.replace("\\", '') for x in list_one]
                list_three = [x.replace("\"", '*') for x in list_two]
                list_four = [x.replace("", '') for x in list_three]
        for sentence in list_four:
            clean = re.sub(pattern_to_eliminate, "", sentence)
            text.append(clean)
        print('After cleaning the size of the file is \t' + str(len(text)))
        return text

    def clean_it(self):
        file = self.open_json(self.json_file)
        file = self.remove(file)
        output_file = self.write_json(self.output_json_file, file)
        print('Your file has been succesfully parsed as a new file named: ' + str(self.output_json_file))


if __name__ == '__main__':
    curr_dir = os.chdir("tweets")
    for file in os.listdir(os.getcwd()):
        if not file.endswith(".json"): continue
        x = CleanData(file, 'output-' + file)
        x.clean_it()
