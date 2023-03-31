'''
    To use this script, you need to have the googlemaps and 
    pymongo python libraries installed.
    To install, run
    pip install -U googlemaps
    pip instill -U pymongo
    or a similar command.

    Truckroutes is a proof of concept demonstration solution to the
    following problem:

    A logistics company suspects that some of its drivers are deviating
    from planned travel routes while on long distance journeys. This may 
    be to visit people, conduct other business, or for any other reason.
    The company does not have GPS data for the routes, but they do have
    the truck odometer readings for the beginning and end of the routes, as
    well as addresses for the places visited between the start and end
    destinations, if any. 

    TruckRoutes takes this data and makes a request to the googleMaps 
    Directions API, which returns average distance information about each
    leg of the journey, and the total distance in meters. This can be used to 
    find significant differences between actual and expected odometer readings, 
    which could lead the company to investigate further.

    Data can either be input and output with CSV files in the local directories, 
    or through a MongoDB database. Read below for relevant information.

'''
from pymongo import MongoClient

import traceback
import googlemaps
from datetime import datetime
import json, csv, os

def process_from_csv(infile, outfile, gmaps, duration=False):
    '''
        Takes an infile in .csv format with the following header:
        StartAddress,Waypoint1,Waypoint2,Waypoint3,Waypoint4,Waypoint5,Waypoint6,EndAddress

        Each column should include an address as a string, for example
        '45 Bennett Rd St Clair Nsw'

        Addresses must have enough information to identify them to googlemaps
        accurately, otherwise outputs may be incorrect.

        Outputs a .csv file (in the current working directory) with the header:
        StartAddress, Waypoint1, Waypoint2, Waypoint3, Waypoint4,
                  Waypoint5, Waypoint6, EndAddress, Distance1, Distance2,
                   Distance3, Distance4, Distance5, Distance6, Distance7,
                   TotalDistance

        Where the distance columns represent the meters travelled between each waypoint
        along the journey. Total distance is the entire journey in meters.
    '''
    with open(outfile, 'w', newline = '') as csv_outfile:
        writer_obj = csv.writer(csv_outfile, delimiter=',')
        header = ["StartAddress", "Waypoint1", "Waypoint2", "Waypoint3", "Waypoint4",
                  "Waypoint5", "Waypoint6", "EndAddress", "Distance1", "Distance2",
                   "Distance3", "Distance4", "Distance5", "Distance6", "Distance7",
                   "TotalDistance"]
        writer_obj.writerow(header)
        with open(infile, 'r', newline='') as csv_infile:
            reader_obj = csv.DictReader(csv_infile, delimiter=',')
            for row in reader_obj:
                start_address = row['StartAddress']
                end_address = row['EndAddress']

                waypoints = []
                for i in range(1, 7):
                    if row["Waypoint" + str(i)] != '':
                        waypoints.append(row["Waypoint" + str(i)])

                directions_result = gmaps.directions(
                                                    start_address,
                                                    end_address,
                                                    mode='driving',
                                                    units='metric',
                                                    waypoints=waypoints
                                                    )
                out_row = []
                num_legs = len(directions_result[0]['legs'])
                legs_list = directions_result[0]['legs']

                for i in range(0, num_legs):
                    out_row.append(legs_list[i]['start_address'])
                
                for i in range(0, 7 - num_legs):
                    out_row.append('')

                out_row.append(legs_list[num_legs - 1]['end_address'])

                total_distance = 0
                for i in range(0, num_legs):
                    out_row.append(legs_list[i]['distance']['value'])
                    total_distance += legs_list[i]['distance']['value']

                for i in range(0, 7 - num_legs):
                    out_row.append('')

                out_row.append(total_distance)

                print(out_row)

                writer_obj.writerow(out_row)


'''
    Processes route information saved in a mongoDB database.
    The documents to be processed should have the following entries:
    start_address : <address> (string)
    end_address : <address> (string)
    waypoint_n : <address> (string)

    Waypoints are optional. Supports up to 6 waypoints. 

    Creates a new mongoDB collection based on the db_name which 
    contains a results entry for each trip. 
    Contains the distance of each 'leg' of the journey, and the 
    total distance travelled (in meters).
'''
def process_from_db(gmaps, uri, keyfile, db_name, collection_name):
    client = MongoClient(uri,
                     tls=True,
                     tlsCertificateKeyFile=keyfile,
                     )
    db = client[db_name]
    collection = db[collection_name]

    doc_count = collection.count_documents({})
    if doc_count < 100000:
        entries = collection.find({})
    else:
        # come up with a way to do batches
        pass

    # clear any results in the db
    db.drop_collection(collection_name + 'Results')
    out_collection = db[collection_name + 'Results']

    try:
        counter = 0
        for row in entries:
            start_address = row['start_address']
            end_address = row['end_address']

            waypoints = []
            for i in range(1, 7):
                try:
                    waypoints.append(row["waypoint_" + str(i)])
                except:
                    continue

            while len(waypoints) < 7:
                waypoints.append('')

            # make the call to gmaps
            directions_result = gmaps.directions(
                                                start_address,
                                                end_address,
                                                mode='driving',
                                                units='metric',
                                                waypoints=waypoints
            )

            # construct the result and save to mongoDB instance as new collection
            out_list = []
            num_legs = len(directions_result[0]['legs'])
            legs_list = directions_result[0]['legs']
            total_dist = 0

            for i in range(0, num_legs):
                out_list.append({
                                'leg': i+1,
                                'start_address': legs_list[i]['start_address'],
                                'end_address': legs_list[i]['end_address'],
                                'distance': legs_list[i]['distance']['value']

                })
                total_dist += legs_list[i]['distance']['value']

            out_list.append({
                'total_distance': total_dist
            })

            # write out the row to the mongoDB instance
            out_collection.insert_one({'result':out_list})
            counter+=1
    except:
        print("An error occurred. Some or all of the data may not have been processed.")
        print(f"Currently processing the {counter}th entry.")
        
        
    if (out_collection.count_documents({}) != collection.count_documents({})):
        print("An unexpected error occurred. The number of results does not match the number of entries") 
        traceback.print_exc
    else:
        print("Processing complete.")


def test_request(gmaps):
    # note the lat/lng coords currently return errors

    melb_lat_lng = {'lat': -37.81522414992452, 'lng': 144.95662719155996 }
    melb_address = 'St. Kilda Beach Melbourne'

    canberra_lat_lng = {'lat': -352802, 'lng': 149.128998 }
    canberra_address = 'parliament house, canberra'

    syd_lat_lng = { 'lat': -33.23468723467, 'lng': 147.3538239847 }
    syd_address = 'summer hill station'

    directions_result = gmaps.directions(
                                        melb_address,
                                        syd_address,
                                        mode='driving',
                                        units='metric',
                                        waypoints=[canberra_address]
                                        )
    
    for leg in directions_result[0]['legs']:
        print("Start: " + leg['start_address'])
        print("End: " + leg['end_address'])
        print("Distance: " + str(leg['distance']['value']))
        print("-----------------------------------------")

def main():
    # googlemaps api key for authenciation - must have to use the googlemaps api
    with open("api_key.txt", 'r', newline='') as api_key_file:
        API_KEY = api_key_file.readline()
    gmaps = googlemaps.Client(key=API_KEY)

    # mongoDB authentication information (typically stored in a file with restricted access)
    uri = "mongodb+srv://truckroutescluster.bi2q6l4.mongodb.net/?authSource=%24external&authMechanism=MONGODB-X509&retryWrites=true&w=majority"
    keyfile='X509-cert-3993792231671370887.pem'
    db_name = 'truckRoutes'
    collection_name = 'exampleData'

    cwd = os.getcwd()

    # filenames of input and output csvs in the current working directory
    infile = cwd + "\\example_infile.csv"
    outfile = cwd + "\\route plotting.csv"

    # uncomment to process csv
    # process_from_csv(infile, outfile, gmaps)
    # uncomment to process mongoDB database
    # process_from_db(gmaps, uri, keyfile, db_name, collection_name)
    
    # uncomment to test connectivity to the googlemaps API
    # test_request(gmaps)

if __name__ == '__main__':
    main()
