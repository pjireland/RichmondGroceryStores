# Distances to grocery stores in Richmond, Indiana

This map indicates the distance from a given location in Richmond, Indiana,
to the nearest grocery store. One goal of this visualization is to highlight
areas that might classify as [food deserts](https://en.wikipedia.org/wiki/Food_desert).

There are three different levels to which a user can interact with these data,
and the prerequisites and approach for each is given below.

## Level 1: View the existing data

### Prerequisities

None

### Approach

The exisiting data can be viewed online here: [https://pjireland.github.io/distance_to_stores.html](https://pjireland.github.io/distance_to_stores.html)

## Level 2: Regenerate the data

### Prerequisites

[Anaconda](https://www.anaconda.com/distribution/#download-section)

### Approach

Run the following command at the top level of the cloned repository:

```
python scripts/map_distance_to_stores.py
``` 

The resulting map will be placed within the `results` directory under the
filename `distance_to_stores.html`.


## Level 3: Add additional data

### Prerequisites

1. [Anaconda](https://www.anaconda.com/distribution/#download-section)

2. Python client library for Google Maps API Web Services.  This can be installed via the command

```
pip install googlemaps
```

   It is used to geocode (obtain the latitude and longitude) of grocery stores.

3. Sign up for a [Google Maps API key](https://developers.google.com/maps/documentation/javascript/get-api-key).

   * Note that that while Google Maps API is a paid service, the monthly free allowances are typically sufficient
     for geocoding the data, but be careful to not exceed your free allowance.

### Approach

1. Download logos of any new grocery stores to the `data` folder.
2. Add/modify grocery store data in the file `./data/grocery_stores.csv`.
    * The name, address, name of downloaded logo image, and desired width and height (in pixels) of the logo image should be added/modified.
3. Geocode the addresses
    * Export your Google Maps API key to the environment variable `API_KEY`.  On Linux and Mac machines, this can be done through the command `export API_KEY=yourAPIkey`.
    * Run `python scripts/geocode_addresses.py` from the top level of the cloned repo to geocode each address in `./data/grocery_stores.csv`.
4. Map the distance to the grocery stores

    * If desired, the variables near the top of the `./scripts/map_distance_to_stores.py` file can be modified to alter how the maps are drawn.
    * The command `python scripts/map_distance_to_stores.py` should then be run in the top level of the cloned repository.

    * The resulting map will be placed within the `results` directory under the filename `distance_to_stores.html`.
