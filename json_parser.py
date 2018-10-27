"""
This class cleans JSON data for tweet sentiment analysis.
Things that it parses for are: links, "\n", "\\", and "\"" in addition to removing duplicates.

Things to do: Remove unicode.
    * Alternative solution to that is to copy and paste the values into https://codebeautify.org/jsonviewer
      and it will clean it for you and format it correctly.
"""
import json
import re
import os


class CleanData:
    """
    The data cleaner.
    """
    def __init__(self, json_file, output_json_file):
        """
        Initializes the class.
        :param json_file: The input tweet data.
        :param output_json_file: The output file to store the cleaned tweet data.
        """
        self.json_file = json_file
        self.output_json_file = output_json_file

    @staticmethod
    def open_json(json_file):
        """
        Opens the JSON file.
        :param json_file: The JSON file to open.
        :return: The loaded data.
        """
        with open(json_file) as json_data_string:
            ds = json.load(json_data_string)
            print('\t\tThe original size of ' + str(json_file) + ' is: \t' + str(len(ds)))
            return ds

    @staticmethod
    def write_json(json_file, data_to_dump):
        """
        Writes data to the specified JSON file.
        :param json_file: The
        :param data_to_dump:
        :return: The name of the input JSON file.
        """
        with open(json_file, 'w') as f:
            json.dump(data_to_dump, f)
            return json_file

    def remove(self, all_tweets):
        """
        Cleans the data.
        :param all_tweets: The input JSON data.
        :return: The cleaned data.
        """
        # if the JSON data is empty, then there are probably no tweets. Just return the empty list.
        if not all_tweets:
            return all_tweets

        final_list = []
        text = []
        pattern_to_eliminate = r"http\S+"

        for t in all_tweets:
            # remove duplicates
            if t not in final_list:
                final_list.append(t)

        # clean through
        list_one = [x.replace("\n", '') for x in final_list]
        list_two = [x.replace("\\", '') for x in list_one]
        list_three = [x.replace("\"", '*') for x in list_two]
        list_four = [x.replace("", '') for x in list_three]
        for sentence in list_four:
            clean = re.sub(pattern_to_eliminate, "", sentence)
            text.append(clean)
        print('\t\tAfter cleaning, the size of the file is \t' + str(len(text)))
        return text

    def clean_it(self):
        """
        Calls the cleaning procedure.
        """
        file = self.open_json(self.json_file)
        file = self.remove(file)
        output_file = self.write_json(self.output_json_file, file)
        print('\t\tYour file has been succesfully parsed as a new file named: ' + str(self.output_json_file))


if __name__ == '__main__':
    curr_dir = os.chdir("tweets")
    for file in os.listdir(os.getcwd()):
        if not file.endswith(".json"): continue
        x = CleanData(file, 'output-' + file)
        x.clean_it()
