from pymongo import MongoClient
import traceback

'''
    This creates some test data for the truckroutes project in a mongoDB Atlas cluster. 
    For the connection to the database to work, the client IP address needs
    to be whitelisted.

    Creates 10 entries with different numbers of waypoints. 
    All entries contain valid data; not to be used for edge case/
    validation testing.

    Requires the pymongo library (the official MongoDB library for python)
    run:
    pip -U install pymongo
    or a similar command. 
'''
def main():
    try: 
        uri = "mongodb+srv://truckroutescluster.bi2q6l4.mongodb.net/?authSource=%24external&authMechanism=MONGODB-X509&retryWrites=true&w=majority"
        client = MongoClient(uri,
                        tls=True,
                        tlsCertificateKeyFile='X509-cert-3993792231671370887.pem',
                        )
        db = client['truckRoutes']
        collection = db['exampleData']

        db.drop_collection('exampleData')

        res = collection.insert_many([
            {
                'start_address':'Carlton Crescent Summer Hill',
                'end_address':'Brisbane, QLD',
                'waypoint_1':'Bathurst, NSW',
                'waypoint_2':'Queenbeyen, NSW'
            },
            {
                'start_address':'Bunnings Warehouse, Ashfield, NSW',
                'end_address':'Inverell, NSW',
                'waypoint_1':'Katoomba, NSW',
                'waypoint_2':'Gloucester, NSW',
                'waypoint_3': 'Baradine, NSW',
                'waypoint_4': 'Brewarrina, NSW'
            },
            {
                'start_address':'Sunshine Coast, QLD',
                'end_address':'Cairns, NSW',
            },
            {
                'start_address':'Carlton Crescent Summer Hill',
                'end_address':'Melbourne, VIC',
                'waypoint_1':'Wollongong, NSW',
                'waypoint_2':'Nowra, NSW',
                'waypoint_3':'Narooma, NSW',
                'waypoint_4':'Thredbo, NSW',
                'waypoint_5':'Merimbula, NSW',
                'waypoint_6':'Albury, NSW',
            },
            {
                'start_address':'Broken Hill, NSW',
                'end_address':'Sydney Tools, Bankstown',
                'waypoint_1':'Mudgee, NSW',
                'waypoint_2':'Orange, NSW'
            },
            {
                # sydney priceline stores
                'start_address':'100 Burwood Rd, Burwood, NSW',
                'end_address':'260A Liverpool Rd Ashfield, NSW',
                'waypoint_1':'51-57 Norton St Leichhardt, NSW',
                'waypoint_2':'19 Roseby St, Drummoye',
                'waypoint_3':'121 Charles St, Canterbury',
                'waypoint_4':'20 Smidmore St, Marrickville',
                'waypoint_5':'Broadway Shopping Center, Sydney',
                'waypoint_6':'60 Charlotte St Clemton Park',
            },
            {
                # sydney bunnings tour
                'start_address':'Cnr Parramatta Rd & Frederick St Ashfield NSW',
                'end_address':'40 Euston Rd Alexandria NSW',
                'waypoint_1':'Cnr Richland St & Kingsgrove Rd, Kingsgrove',
                'waypoint_2':'Cnr Roberts Road & Amarina Ave, Greenacre',
                'waypoint_3':'383 West Botany St Rockdale'
            },
            {
                'start_address':'Carlton Crescent Summer Hill',
                'end_address':'Brisbane, QLD',
                'waypoint_1':'Bathurst, NSW',
                'waypoint_2':'Queenbeyen, NSW'
            },
            {
                'start_address':'Carlton Crescent Summer Hill',
                'end_address':'Brisbane, QLD',
                'waypoint_1':'Bathurst, NSW',
                'waypoint_2':'Queenbeyen, NSW'
            },
            {
                'start_address':'Carlton Crescent Summer Hill',
                'end_address':'Brisbane, QLD',
                'waypoint_1':'Bathurst, NSW',
                'waypoint_2':'Queenbeyen, NSW'
            },
        ])
    except:
        print("Something unexpected occured. Data may not have been created.")

    
    doc_count = collection.count_documents({})
    if doc_count == 10:
        print(f"Successfully created and inserted {doc_count} documents.")
    else:
        print("Something unexpected occured.")

if __name__ == '__main__':
    main()