# truckRoutes

Truckroutes is a proof of concept demonstration solution to the
following problem:

A logistics company suspects that some of its drivers are deviating
from planned travel routes while on long distance journeys. This may 
be to visit people, conduct other business, or for any other reason.
The company does not have GPS data for the routes, but they do have
the truck odometer readings for the beginning and end of the routes, as
well as addresses for the places visited.

TruckRoutes takes this data and makes a request to the googleMaps 
Directions API, which returns average distance information about each
leg of the journey, and the total distance in meters. This can be used to 
find significant differences between actual and expected odometer readings, 
which could lead the company to investigate further.

Data can either be input and output with CSV files in the local directories, 
or through a MongoDB database.

## usage

Usage of truckroutes requires:
- access to the mongoDB database with a X.509 certificate and whitelisted IP address
- an API key registered for use with the googlemaps Directions API
- installation of the googlemaps and pymongo python libraries:
    - pip install -U googlemaps (or similar command)
    - pip install -U pymongo (or similar command)

## input and output
There are two options - csv and mongoDB.
Uncomment process_from_csv in main() to use the csv method. 
Uncommebt process_from_db in main() to use the db method.

### CSV
If input is provided as a csv file, use the process_from_csv function. Output will also be to a csv file. 
An example CSV is provided as example_infile.csv. 
An example CSV output file is provided as route plotting.csv.

### MongoDB database
truckRoutes connects to a mongoDB database with a collection called 'exampleData'.
Each document in the collection must have a start_address and an end_address which must
be an address string which the googlemaps API can process. 
e.g "123 example st lewisham sydney"
e.g "bunnings warehouse ashfield sydney"

Additionally, the document may have up to 6 waypoints where
with keys are:
waypoint_n, 1 < n < 6

A results collection is created called exampleDataResults.
The script creates a result document for each journey which
contains the distance in meters of each legs of the journey, 
plus the total distance travelled. 