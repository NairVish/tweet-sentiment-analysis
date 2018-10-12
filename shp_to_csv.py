import shapefile
import csv

all_cities_ne = []

shape = shapefile.Reader("cities_shapefile/cities.shp")
for r in shape.iterShapeRecords():
     print(r.shape.points[0])
     print(r.record)
     all_cities_ne.append([r.record[1],r.shape.points[0][0],r.shape.points[0][1], r.record[5]])

with open("cities.csv", "w") as output_city_file:
    writer = csv.writer(output_city_file)
    for c in all_cities_ne:
        writer.writerow(c)
