
'''
Authors: Kostas Stamatiou, Dan Getman, Nate Ricklin, Dahl Winters, Donnie Marino
Contact: kostas.stamatiou@digitalglobe.com


GBDX Catalog Interface
'''
import requests
from pygeoif import geometry
import json

class Catalog():

    def __init__(self, interface):
        ''' Construct the Catalog interface class

        Args:
            interface: A reference to the GBDX Interface.

        Returns:
            An instance of the Catalog interface class.
        '''
        self.gbdx_connection = interface.gbdx_connection
        self.logger = interface.logger

    def get_strip_footprint_wkt(self, catID):
        '''Retrieves the strip footprint WKT string given a cat ID.

        Args:
            catID (str): The source catalog ID from the platform catalog.

        Returns:
            footprint (str): A POLYGON of coordinates.
        '''

        self.logger.debug('Retrieving strip footprint')
        url = ('https://geobigdata.io/catalog/v1/record/' 
               + catID + '?includeRelationships=false')

        r = self.gbdx_connection.get(url)
        if r.status_code == 200:
            footprint = r.json()['properties']['footprintWkt']
            return footprint
        elif r.status_code == 404:
            self.logger.debug('Strip not found: %s' % catID)
            r.raise_for_status()
        else:
            self.logger.debug('There was a problem retrieving catid: %s' % catID)
            r.raise_for_status()

    def get_address_coords(self, address):
        ''' Use the google geocoder to get latitude and longitude for an address string

        Args:
            address: any address string

        Returns:
            A tuple of (lat,lng)
        '''
        url = "https://maps.googleapis.com/maps/api/geocode/json?&address=" + address
        r = requests.get(url)
        r.raise_for_status()
        results = r.json()['results']
        lat = results[0]['geometry']['location']['lat']
        lng = results[0]['geometry']['location']['lng']
        return lat, lng

    def search_address(self, address):
        ''' Perform a catalog search over an address string

        Args:
            address: any address string

        Returns:
            catalog resultset dictionary
        '''
        lat, lng = self.get_address_coords(address)
        return self.search_point(lat,lng)

    def search_point(self, lat, lng):
        ''' Perform a catalog search over a specific point, specified by lat,lng

        Args:
            lat: latitude
            lng: longitude

        Returns:
            catalog resultset dictionary
        '''
        postdata = {  
            "searchAreaWkt":"POLYGON ((%s %s, %s %s, %s %s, %s %s, %s %s))" % (lng, lat,lng,lat,lng,lat,lng,lat,lng,lat),
            "filters":[  
            ],
            "types":[  
                "Acquisition"
            ]
        }
        url = 'https://geobigdata.io/catalog/v1/search?includeRelationships=false'
        headers = {'Content-Type':'application/json'}
        r = self.gbdx_connection.post(url, headers=headers, data=json.dumps(postdata))
        r.raise_for_status()
        return r.json()




