"""
The geo-data parser.

Parses shapefile and census data for later use.
"""
import csv
import math

import shapefile
import us


class GeoDataParser:
    """
    The geo-data parser.
    """

    def __init__(self, cities_shapefile, census_data_file, out_file_name):
        """
        Initializes the class.
        :param cities_shapefile: The path to the shapefile with NE cities.
        :param census_data_file: The path to the census data.
        :param out_file_name: The name of the output file.
        """
        self.cities_shapefile = cities_shapefile
        self.census_data_file = census_data_file
        self.out_file_name = out_file_name
        print("\tINSTANTIATED GEODATA PARSER")

    @staticmethod
    def find_radius_from_area(area):
        """
        Reverse the circle area formula to determine a radius using the area of a circle.
        :param area: The area of the circle in question.
        :return: The calculated radius.
        """
        return math.sqrt(area / math.pi)

    @staticmethod
    def get_radius(city_type):
        """
        Determines a generic radius for a geographical entity depending the on the type of the entity.
        :param city_type: The type.
        :return: The generic radius.
        """
        if city_type == "city":
            return 9
        elif city_type == "census designated place":
            return 2
        elif city_type == "village" or city_type == "town":
            return 3
        elif city_type == "borough":
            return 7
        elif city_type == "city (remainder)":
            return 4

    def parse(self):
        """
        Parses the files.
        """
        all_cities_ne = []

        # Read the shapefile
        print("\tReading shapefile.")
        shape = shapefile.Reader(self.cities_shapefile)

        # For each record in the shapefile...
        for r in shape.iterShapeRecords():
            # Grab the entity's name, lat, lon, type, and state (in abbreviated form)
            c = {
                "name": r.record[1],
                "lon": r.shape.points[0][0],
                "lat": r.shape.points[0][1],
                "type": r.record[5],
                "state": str(us.states.lookup(r.record[3]).abbr),
            }
            all_cities_ne.append(c)

        # For each shapefile record, attempt to match it with census data
        gazetteer_matched_data = []
        skipped_count = 0

        print("\tReading Census data and matching shapefile data with census data.")

        # Open the census data...
        with open(self.census_data_file) as csvfile:
            r = csv.reader(csvfile, delimiter="\t")  # as a tab-delimited file
            next(r)  # skip the header

            # for each row in the file...
            for row in r:
                # divide the row using the existing whitespace
                line = [e.strip() for e in row]

                # get the city and city type, which were not separated by the strip operation
                city_type_combo = line[3].split()

                # attempt to divide the city name and city type
                if "(balance)" in city_type_combo:
                    # if the city type is "city (balance)"
                    # then take the last two words as the type and everything else as the city name
                    city = ' '.join(city_type_combo[:-2])
                    type = ' '.join(city_type_combo[-2:])
                else:
                    # the last word is the type
                    # everything else is the city name
                    city = ' '.join(city_type_combo[:-1])
                    type = ' '.join(city_type_combo[-1:])

                # alter some terms to match with the terms used in the USGS shapefile data
                if type == "CDP":
                    type = "census designated place"
                elif type == "city (balance)":
                    type = "city (remainder)"

                # extract some more data points from the census data
                area_sq_mi = line[10]
                lat = line[12]
                lon = line[13]
                state = line[0]

                # search the shapefile data for this census city
                d = next((c for c in all_cities_ne
                          if c["name"].lower().strip() == city.lower().strip()
                          and c["state"].lower().strip() == state.lower().strip())
                         , None)

                # if this census city was not found in the shapefile data, skip it
                if d is None:
                    skipped_count += 1
                    continue

                # else find the radius of the city
                # The census data provides the total land area for each city. Let us assume that the city is circular
                # and find the radius by reversing the circle area formula.
                d["radius"] = round(self.find_radius_from_area(float(area_sq_mi)), 2)

                # add this data to our matched data
                gazetteer_matched_data.append(d)

                # print("{}\n\ttype: {}\n\tarea: {}\n\tradius: {}\n\tlat: {}\n\tlon: {}\n\tstate: {}\n{}"
                #       .format(city, type, float(area_sq_mi), round(find_radius_from_area(float(area_sq_mi)), 2), float(lat),
                #               float(lon), state, str(d)))

        print("\t{} cities were extracted from the shapefile.".format(len(all_cities_ne)))
        print("\t{} of those cities were matched with Census data.".format(len(gazetteer_matched_data)))
        print("\t{} cities in the Census data were not present in the shapefile. Disregarding these.".format(
            skipped_count))

        print("\tNow re-adding {} unmatched shapefile cities back into the data with generic radii.".format(
            len(all_cities_ne) - len(gazetteer_matched_data)))

        # some shapefile cities were not found in the census data...
        # for these cities, assign generic radii
        # thus, for each city in the shapefile record...
        for c in all_cities_ne:
            # try to find it in the census data...
            d = next((mc for mc in gazetteer_matched_data if mc["name"] == c["name"] and mc["state"] == c["state"]),
                     None)
            # if it's found, skip it since we don't need to do anything
            if d is not None: continue

            # assign the generic radius
            c["radius"] = self.get_radius(c["type"])
            print("\t\t{} has been given a generic radius of {} ({}).".format(c["name"], c["radius"], c["type"]))

            # append to the "matched" data
            gazetteer_matched_data.append(c)

        # write the matched data to the cities csv file
        print("\tWriting matched data to {}.".format(self.out_file_name))
        with open(self.out_file_name, "w") as output_city_file:
            writer = csv.writer(output_city_file)
            for c in gazetteer_matched_data:
                writer.writerow([c["name"], c["lon"], c["lat"], c["type"], c["state"], c["radius"]])

        print("\tDONE!")


if __name__ == "__main__":
    USGS_SHAPEFILE = "usgs_ne_cities_shapefile/cities.shp"
    US_CENSUS_GAZETTEER_DATA = "us_census_gazetteer_ne.txt"
    OUTPUT = "cities.csv"
    p = GeoDataParser(USGS_SHAPEFILE, US_CENSUS_GAZETTEER_DATA, OUTPUT)
    p.parse()
