import shapefile
import csv
import us
import math


class GeoDataParser:

    def __init__(self, cities_shapefile, census_data_file, out_file_name):
        self.cities_shapefile = cities_shapefile
        self.census_data_file = census_data_file
        self.out_file_name = out_file_name

    @staticmethod
    def find_radius_from_area(area):
        # A = pi*r^2
        # r = sqrt(A/pi)
        return math.sqrt(area/math.pi)

    @staticmethod
    def get_radius(city_type):
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

        all_cities_ne = []

        shape = shapefile.Reader(self.cities_shapefile)
        for r in shape.iterShapeRecords():
             c = {
                 "name": r.record[1],
                 "lon": r.shape.points[0][0],
                 "lat": r.shape.points[0][1],
                 "type": r.record[5],
                 "state": str(us.states.lookup(r.record[3]).abbr),
             }
             all_cities_ne.append(c)

        gazetteer_matched_data = []
        not_found = []

        with open(self.census_data_file) as csvfile:
            r = csv.reader(csvfile, delimiter="\t")
            next(r)
            for row in r:
                line = [e.strip() for e in row]
                city_type_combo = line[3].split()
                if "(balance)" in city_type_combo:
                    city = ' '.join(city_type_combo[:-2])
                    type = ' '.join(city_type_combo[-2:])
                else:
                    city = ' '.join(city_type_combo[:-1])
                    type = ' '.join(city_type_combo[-1:])
                if type == "CDP":
                    type = "census designated place"
                elif type == "city (balance)":
                    type = "city (remainder)"

                area_sq_mi = line[10]
                lat = line[12]
                lon = line[13]
                state = line[0]

                d = None
                for c in all_cities_ne:
                    if c["name"].lower().strip() == city.lower().strip() and c["state"].lower().strip() == state.lower().strip():
                        d = c
                        break

                if d is None:
                    not_found.append(city)
                    continue

                # d = next((c for c in all_cities_ne if ), None)
                d["radius"] = round(self.find_radius_from_area(float(area_sq_mi)), 2)

                gazetteer_matched_data.append(d)

                # print("{}\n\ttype: {}\n\tarea: {}\n\tradius: {}\n\tlat: {}\n\tlon: {}\n\tstate: {}\n{}"
                #       .format(city, type, float(area_sq_mi), round(find_radius_from_area(float(area_sq_mi)), 2), float(lat),
                #               float(lon), state, str(d)))

        print("{} cities were extracted from the shapefile.".format(len(all_cities_ne)))
        print("{} of those cities were matched with Census data.".format(len(gazetteer_matched_data)))
        print("Not found in original USGS data: {}\n\tThese will be disregarded.".format(not_found))

        print("Now adding unmatched USGS cities back into data with generic radii.")
        for c in all_cities_ne:
            d = next((mc for mc in gazetteer_matched_data if mc["name"] == c["name"] and mc["state"] == c["state"]), None)
            if d is not None: continue

            c["radius"] = self.get_radius(c["type"])
            print("\t{} has been given a generic radius of {} ({}).".format(c["name"], c["radius"], c["type"]))
            gazetteer_matched_data.append(c)

        with open(self.out_file_name, "w") as output_city_file:
            writer = csv.writer(output_city_file)
            for c in gazetteer_matched_data:
                writer.writerow([c["name"], c["lon"], c["lat"], c["type"], c["state"], c["radius"]])


if __name__ == "__main__":
    USGS_SHAPEFILE = "usgs_ne_cities_shapefile/cities.shp"
    US_CENSUS_GAZETTEER_DATA = "us_census_gazetteer_ne.txt"
    OUTPUT = "cities.csv"
    p = GeoDataParser(USGS_SHAPEFILE, US_CENSUS_GAZETTEER_DATA, OUTPUT)
    p.parse()