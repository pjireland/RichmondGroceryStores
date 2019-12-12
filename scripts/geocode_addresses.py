#!/usr/bin/env python

from __future__ import division, print_function
import pandas as pd
import os
import googlemaps
import json


def read_addresses(file):
    '''Read the addresses CSV file'''
    df = pd.read_csv(file)
    return df


def get_gmaps_handle():
    api_key = os.environ['API_KEY']
    gmaps = googlemaps.Client(key=api_key)
    return gmaps


def write_lat_lng(df, filename):
    '''Save latitude and longitude to a CSV file'''
    df = df[(df['lat'] != 'nan') & (df['lng'] != 'nan')]
    df = df.rename(index=str, columns={'Unnamed: 0': 'index'})
    df.to_csv(os.path.join('data', filename),
              index=False)


def geocode_address(address, gmaps):
    '''Geocode an address using the Google Maps API'''
    geocode = gmaps.geocode(address)
    try:
        location = geocode[0]['geometry']['location']
        return str(location['lat']) + ' ' + str(location['lng'])
    except:
        print('Failed to geocode address:', address, flush=True)
        return 'nan nan'


def geocode_addresses():
    '''
    Main routine for geocoding the addresses
    in `./data/*.csv`
    '''

    for f in ['grocery_stores']:
      df = read_addresses(os.path.join('data', f + '.csv'))
      gmaps = get_gmaps_handle()
      df['lat_lng'] = df.apply(lambda row: geocode_address(row.address, gmaps), axis=1)
      df['lat'] = df['lat_lng'].apply(lambda row: row.split()[0])
      df['lng'] = df['lat_lng'].apply(lambda row: row.split()[1])
      df = df.drop(['lat_lng'], axis=1)
      write_lat_lng(df, f + '_with_latlng.csv')


if __name__ == "__main__":
    geocode_addresses()

