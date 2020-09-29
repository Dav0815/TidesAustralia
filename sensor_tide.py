import appdaemon.plugins.hass.hassapi as hass
from datetime import timedelta, date, datetime, timezone
from bs4 import BeautifulSoup
import math
import requests
import globals


class SensorTide(hass.Hass):
    """ Sensor to pull tidal information from BOM (Australia).

    This sensor pulls the tidal information from BOM (Australia), cleans the data and 
    calculates current tide level and time to next event.

    The sensor requires the BeautifulSoup lib (pip install bs4) !

    Pick a location from the list below. If no location is provided, the closest 
    location will be determined from the Appdaemon long and lat values.

    The AAC attribute is important. Below a sample configuration in YAML.
    Tide:
        module: sensor_tide
        class: SensorTide
        actuator: sensor.tide
        tide_location: 'NSW_TP001'
        friendly_name: 'Next Tide'

    Please note the following copyright information from BOM Australia:
    “This product is based on Bureau of Meteorology information that
    has subsequently been modified. The Bureau does not necessarily
    support or endorse, or have any connection with, the product.
    In respect of that part of the information which is sourced from the
    Bureau, and to the maximum extent permitted by law:
    (i) The Bureau makes no representation and gives no warranty of
    any kind whether express, implied, statutory or otherwise in respect
    to the availability, accuracy, currency, completeness, quality or
    reliability of the information or that the information will be fit for any
    particular purpose or will not infringe any third party Intellectual
    Property rights; and
    (ii) the Bureau's liability for any loss, damage, cost or expense
    resulting from use of, or reliance on, the information is entirely
    excluded.” 


    Parameters
    ----------
    actuator: str
        Name of the sensor
    tide_location: str (optional)
        Sensor source station
    friendly_name: str (optional)
        Friendly name for the sensor
    """
    def initialize(self):
        # List of suported locations with coordinates and name
        self.location_list = {
            'NSW_TP001': { 'lat': -33.9666666666667, 'long': 151.216666666667, 'name': ' Botany Bay' },
            'NSW_TP002': { 'lat': -37.0666666666667, 'long': 149.9, 'name': ' Eden' },
            'NSW_TP003': { 'lat': -31.5166666666667, 'long': 159.05, 'name': ' Lord Howe Island' },
            'NSW_TP004': { 'lat': -32.9166666666667, 'long': 151.783333333333, 'name': ' Newcastle' },
            'NSW_TP005': { 'lat': -29.0666666666667, 'long': 167.95, 'name': ' Norfolk Island' },
            'NSW_TP006': { 'lat': -34.4833333333333, 'long': 150.916666666667, 'name': ' Port Kembla' },
            'NSW_TP007': { 'lat': -33.85, 'long': 151.233333333333, 'name': ' Sydney (Fort Denison)' },
            'NSW_TP008': { 'lat': -29.4333333333333, 'long': 153.366666666667, 'name': ' Yamba' },
            'NT_TP001': { 'lat': -12.4666666666667, 'long': 130.85, 'name': ' Darwin' },
            'NT_TP002': { 'lat': -12.2, 'long': 136.666666666667, 'name': ' Melville Bay (Gove Harbour)' },
            'NT_TP003': { 'lat': -13.8666666666667, 'long': 136.416666666667, 'name': ' Milner Bay (Groote Eylandt)' },
            'NT_TP014': { 'lat': -15.75, 'long': 136.816666666667, 'name': ' Centre Island' },
            'NT_TP036': { 'lat': -12.3333333333333, 'long': 130.7, 'name': ' Charles Point Patches' },
            'QLD_TP001': { 'lat': -19.85, 'long': 148.116666666667, 'name': ' Abbot Point' },
            'QLD_TP002': { 'lat': -20.0166666666667, 'long': 148.25, 'name': ' Bowen' },
            'QLD_TP003': { 'lat': -27.3666666666667, 'long': 153.166666666667, 'name': ' Brisbane Bar' },
            'QLD_TP004': { 'lat': -20.0833333333333, 'long': 150.3, 'name': ' Bugatti Reef' },
            'QLD_TP005': { 'lat': -24.7666666666667, 'long': 152.383333333333, 'name': ' Bundaberg (Burnett Heads)' },
            'QLD_TP006': { 'lat': -16.9333333333333, 'long': 145.783333333333, 'name': ' Cairns' },
            'QLD_TP008': { 'lat': -23.8333333333333, 'long': 151.25, 'name': ' Gladstone' },
            'QLD_TP009': { 'lat': -27.9666666666667, 'long': 153.416666666667, 'name': ' Gold Coast Operations Base' },
            'QLD_TP011': { 'lat': -27.95, 'long': 153.416666666667, 'name': ' Gold Coast Seaway' },
            'QLD_TP012': { 'lat': -21.2666666666667, 'long': 149.3, 'name': ' Hay Point' },
            'QLD_TP013': { 'lat': -17.5, 'long': 140.833333333333, 'name': ' Karumba' },
            'QLD_TP014': { 'lat': -14.5333333333333, 'long': 144.85, 'name': ' Leggatt Island' },
            'QLD_TP017': { 'lat': -18.5166666666667, 'long': 146.383333333333, 'name': ' Lucinda (Offshore)' },
            'QLD_TP018': { 'lat': -21.1166666666667, 'long': 149.233333333333, 'name': ' Mackay Outer Harbour' },
            'QLD_TP019': { 'lat': -26.6833333333333, 'long': 153.116666666667, 'name': ' Mooloolaba' },
            'QLD_TP020': { 'lat': -17.6, 'long': 146.116666666667, 'name': ' Mourilyan Harbour' },
            'QLD_TP021': { 'lat': -26.3833333333333, 'long': 153.1, 'name': ' Noosa Head' },
            'QLD_TP022': { 'lat': -23.5833333333333, 'long': 150.866666666667, 'name': ' Port Alma' },
            'QLD_TP023': { 'lat': -16.4833333333333, 'long': 145.466666666667, 'name': ' Port Douglas' },
            'QLD_TP024': { 'lat': -23.1666666666667, 'long': 150.8, 'name': ' Rosslyn Bay' },
            'QLD_TP025': { 'lat': -20.2833333333333, 'long': 148.783333333333, 'name': ' Shute Harbour' },
            'QLD_TP026': { 'lat': -10.6, 'long': 141.916666666667, 'name': ' Booby Island' },
            'QLD_TP027': { 'lat': -10.5666666666667, 'long': 142.15, 'name': ' Goods Island' },
            'QLD_TP030': { 'lat': -10.5833333333333, 'long': 142.216666666667, 'name': ' Thursday Island' },
            'QLD_TP032': { 'lat': -10.45, 'long': 142.45, 'name': ' Twin Island' },
            'QLD_TP033': { 'lat': -19.25, 'long': 146.833333333333, 'name': ' Townsville' },
            'QLD_TP034': { 'lat': -25.3, 'long': 152.9, 'name': ' Urangan' },
            'QLD_TP035': { 'lat': -24.9666666666667, 'long': 153.35, 'name': ' Waddy Point (Fraser Island)' },
            'QLD_TP036': { 'lat': -12.6666666666667, 'long': 141.866666666667, 'name': ' Weipa (Humbug Point)' },
            'QLD_TP104': { 'lat': -27.35, 'long': 153.1, 'name': ' Serpentine Creek' },
            'QLD_TP135': { 'lat': -18.25, 'long': 146.033333333333, 'name': ' Cardwell' },
            'QLD_TP138': { 'lat': -27.4666666666667, 'long': 153.033333333333, 'name': ' Brisbane Port Office' },
            'QLD_TP147': { 'lat': -27.0833333333333, 'long': 153.15, 'name': ' Bribie I., Bongaree' },
            'QLD_TP148': { 'lat': -27.0833333333333, 'long': 153.3, 'name': ' Bn M2, Moreton Bay' },
            'QLD_TP149': { 'lat': -27.1833333333333, 'long': 153.366666666667, 'name': ' Tangalooma Point' },
            'SA_TP001': { 'lat': -34.7833333333333, 'long': 138.483333333333, 'name': ' Port Adelaide (Outer Harbor)' },
            'SA_TP002': { 'lat': -35.0166666666667, 'long': 137.766666666667, 'name': ' Port Giles' },
            'SA_TP003': { 'lat': -34.7166666666667, 'long': 135.866666666667, 'name': ' Port Lincoln' },
            'SA_TP004': { 'lat': -33.1833333333333, 'long': 138.016666666667, 'name': ' Port Pirie' },
            'SA_TP005': { 'lat': -32.15, 'long': 133.633333333333, 'name': ' Thevenard' },
            'SA_TP006': { 'lat': -35.5666666666667, 'long': 138.633333333333, 'name': ' Victor Harbor' },
            'SA_TP007': { 'lat': -33.9333333333333, 'long': 137.616666666667, 'name': ' Wallaroo' },
            'SA_TP008': { 'lat': -33.0166666666667, 'long': 137.583333333333, 'name': ' Whyalla' },
            'TAS_TP001': { 'lat': -41.05, 'long': 145.916666666667, 'name': ' Burnie' },
            'TAS_TP003': { 'lat': -42.8833333333333, 'long': 147.333333333333, 'name': ' Hobart' },
            'TAS_TP004': { 'lat': -41.0666666666667, 'long': 146.8, 'name': ' Low Head' },
            'TAS_TP005': { 'lat': -41.15, 'long': 146.383333333333, 'name': ' Devonport' },
            'TAS_TP007': { 'lat': -42.55, 'long': 147.933333333333, 'name': ' Spring Bay' },
            'TAS_TP008': { 'lat': -40.7666666666667, 'long': 145.3, 'name': ' Stanley' },
            'VIC_TP001': { 'lat': -37.8833333333333, 'long': 147.966666666667, 'name': ' Lakes Entrance (Outer)' },
            'VIC_TP002': { 'lat': -38.55, 'long': 143.983333333333, 'name': ' Lorne' },
            'VIC_TP003': { 'lat': -37.8666666666667, 'long': 144.916666666667, 'name': ' Melbourne (Williamstown)' },
            'VIC_TP004': { 'lat': -38.1, 'long': 144.65, 'name': ' Corio Bay' },
            'VIC_TP005': { 'lat': -38.15, 'long': 144.366666666667, 'name': ' Geelong' },
            'VIC_TP006': { 'lat': -38.3333333333333, 'long': 144.9, 'name': ' Hovell Pile' },
            'VIC_TP007': { 'lat': -38.2666666666667, 'long': 144.666666666667, 'name': ' Queenscliff' },
            'VIC_TP008': { 'lat': -38.2, 'long': 144.75, 'name': ' West Channel Pile' },
            'VIC_TP009': { 'lat': -38.3, 'long': 144.616666666667, 'name': ' Point Lonsdale' },
            'VIC_TP010': { 'lat': -38.7, 'long': 146.466666666667, 'name': ' Port Welshpool Pier' },
            'VIC_TP011': { 'lat': -38.35, 'long': 141.616666666667, 'name': ' Portland' },
            'VIC_TP012': { 'lat': -38.9166666666667, 'long': 146.516666666667, 'name': ' Rabbit Island' },
            'VIC_TP013': { 'lat': -38.3666666666667, 'long': 145.216666666667, 'name': ' Western Port (Stony Point)' },
            'WA_TP001': { 'lat': -35.0333333333333, 'long': 117.9, 'name': ' Albany' },
            'WA_TP002': { 'lat': -20.8166666666667, 'long': 115.55, 'name': ' Barrow Island (Tanker Mooring)' },
            'WA_TP003': { 'lat': -20.7333333333333, 'long': 115.466666666667, 'name': ' Barrow Island (Wapet Landing)' },
            'WA_TP004': { 'lat': -18, 'long': 122.216666666667, 'name': ' Broome' },
            'WA_TP005': { 'lat': -33.3166666666667, 'long': 115.666666666667, 'name': ' Bunbury' },
            'WA_TP007': { 'lat': -14.25, 'long': 125.6, 'name': ' Cape Voltaire (Krait Bay)' },
            'WA_TP008': { 'lat': -24.9, 'long': 113.65, 'name': ' Carnarvon' },
            'WA_TP009': { 'lat': -10.4333333333333, 'long': 105.666666666667, 'name': ' Christmas Island' },
            'WA_TP011': { 'lat': -20.6166666666667, 'long': 116.75, 'name': ' Dampier (King Bay)' },
            'WA_TP012': { 'lat': -25.9333333333333, 'long': 113.533333333333, 'name': ' Denham' },
            'WA_TP013': { 'lat': -33.8666666666667, 'long': 121.9, 'name': ' Esperance' },
            'WA_TP014': { 'lat': -21.95, 'long': 114.133333333333, 'name': ' Exmouth' },
            'WA_TP015': { 'lat': -32.05, 'long': 115.733333333333, 'name': ' Fremantle' },
            'WA_TP016': { 'lat': -28.7833333333333, 'long': 114.6, 'name': ' Geraldton' },
            'WA_TP018': { 'lat': -21.65, 'long': 115.133333333333, 'name': ' Onslow (Beadon Creek)' },
            'WA_TP020': { 'lat': -20.3166666666667, 'long': 118.566666666667, 'name': ' Port Hedland' },
            'WA_TP021': { 'lat': -20.5833333333333, 'long': 117.183333333333, 'name': ' Port Walcott (Cape Lambert)' },
            'WA_TP022': { 'lat': -21.4666666666667, 'long': 115.016666666667, 'name': ' Thevenard Island' },
            'WA_TP023': { 'lat': -15.45, 'long': 128.1, 'name': ' Wyndham' },
            'WA_TP024': { 'lat': -16.1333333333333, 'long': 123.733333333333, 'name': ' Yampi Sound (Koolan Island)' },
            'WA_TP025': { 'lat': -21.65, 'long': 115.016666666667, 'name': ' Ashburton North' },
            'WA_TP032': { 'lat': -14.8333333333333, 'long': 128.3, 'name': ' Cape Domett' },
            'WA_TP043': { 'lat': -17.3, 'long': 123.6, 'name': ' Derby' },
        }

        # Setup the default state and attributes
        self.attribute = {}
        self.attribute.update({"unit_of_measurement": "m"})
        if "friendly_name" in self.args:
            self.attribute.update({"friendly_name":
                                  self.args["friendly_name"]})
        self.attribute.update({"icon": "mdi:waves"})
        # Set specific attribute
        self.attribute.update({"Next tide": ""})
        self.attribute.update({"Next height": 0})
        self.attribute.update({"Tide time": ""})
        self.attribute.update({"Time in min": 0})
        self.attribute.update({"degree": 0})
        self.attribute.update({"location": ""})
        self.set_state(self.args["actuator"],
                       attributes=self.attribute, state="Unknown")

        # Find the closest location or take config parameter
        self.location = self.find_closest_location()
        if "tide_location" in self.args :
            self.location = self.args["tide_location"]

        if self.location in self.location_list:
            self.tides = []
            # Refresh tidal information very night
            self.time_midnight = "00:00:05"
            self.runtime_midnight = self.parse_time(self.time_midnight)
            self.run_daily(self.refresh_tide_data, self.runtime_midnight)
            # Start the sensor and refresh every 5min
            runtime = datetime.now()
            addseconds = 10
            runtime = runtime + timedelta(seconds=addseconds)
            self.run_every(self.get_tide_data, runtime, 360)
        else:
            self.log("Location not supported or kown.")


    def get_tide_data(self, kwargs):
        """ Update the sensor values.
        """
        try:
            if len(self.tides) == 0 or self.tides is None:
                self.log("No data, refresh triggered")
                self.tides = self.update_tide_data()
            # Set values
            tide, min, time, height, current_height = self.get_next_tide(self.tides)
            self.attribute.update({"Next tide": tide})
            self.attribute.update({"Next height": height})
            self.attribute.update({"Tide time": time})
            self.attribute.update({"Time in min": min})
            self.attribute.update({"degree": round(self.scale_values(min, tide)) })
            self.attribute.update({"location": self.location_list[self.location].get('name') + " (" + str(self.location_list[self.location].get('distance')) + "km)" })
            self.set_state(self.args["actuator"],
                        attributes=self.attribute, state=round(current_height, 2))
        except TimeoutError:
            self.log("Refresh took too long. Try later.")

    def refresh_tide_data(self, kwargs):
        """ Update the tide information from the website.

        This function is called every night to pull the data for the upcoming tides.
        """
        self.log("Nightly refresh triggered")
        self.tides = self.update_tide_data()

    def get_next_tide(self, tides):
        """ Returns the next tide details.

        Parameters:
            tides (list): List of tide information

        Returns:
            str: Type of next tide (high/low)
            int: Minutes to next tide event
            date: Time of the next tide event
            float: Height of the next tide in m
            float: Current tidal level in m
        """
        last_height = 0
        last_min = 0
        for entry in tides:
            next_datetime = datetime.strptime(entry[0], '%Y-%m-%dT%H:%M:%S%z')
            current_datetime = datetime.now(timezone.utc)
            delta = (next_datetime - current_datetime).total_seconds()
            if delta > 0:
                next_height = entry[2]
                next_min = round(delta/60)
                current_height = round(
                    last_height + (next_height - last_height) *
                    ((last_min * -1) / (last_min * -1 + next_min)),
                    2
                )
                return entry[1], round(delta/60), entry[0], next_height, current_height
            else:
                last_height = entry[2]
                last_min = round(delta/60)

    def update_tide_data(self):
        """ Gets the tide details from BOM.

        Returns:
            tides (list): List of tide information
        """
        tides = []
        try:
            config = self.get_plugin_config()
            tz = '&tz='+config["time_zone"]
            # Get data from day -1 for three days.
            yesterday = (date.today() + timedelta(days=-1)).strftime("%d-%m-%Y")
            url = 'http://www.bom.gov.au/australia/tides/print.php?aac=' + \
                  self.location + '&type=tide&date=' + yesterday + \
                  tz + '&days=3'
            # Connect to the URL
            response = requests.get(url)
            # Parse HTML and save to BeautifulSoup object
            soup = BeautifulSoup(response.text, "html.parser")
            for tag in soup.findAll('tr'):
                for next in tag.findAll('td'):
                    att = next['class']
                    if att[0] == 'localtime' and len(att) == 2:
                        entry = [next['data-time-local'], att[1]]
                        tides.append(entry)
                    if att[0] == 'height' and len(att) == 2:
                        entry = tides[-1]
                        entry.append(float(next.text.replace(' m', '')))
                        tides[-1] = entry
            return(tides)
        except:
            self.log("Error getting tide data: " + url)

    def find_closest_location(self):
        """ Find the closest location from the list.

        Returns:
            str: Location id
        """
        location = ""
        min_distance = None
        config = self.get_plugin_config()
        base_coords = config["latitude"], config["longitude"]
        for temp in self.location_list:
            location_coords = float(self.location_list[temp].get('lat')), float(self.location_list[temp].get('long'))
            distance = self.haversine(base_coords, location_coords)
            self.log( temp + " is " + str(distance))
            if min_distance is None or min_distance > distance:
                location = temp
                min_distance = distance
                self.location_list[location]['distance'] = distance
        self.log("Closest point " + location + " " + self.location_list[location].get('name') + " being in " + str(self.location_list[location].get('distance')) + "km")
        return location

    def scale_values(self, next_min, next_tide):
        """ Scales time to degree values.
        The function helps translating time to next tide
        to a degree value that could be presented on a clock
        face.

        Parameters:
            next_min (int): Time to next tide
            next_tide (str): High or low tide

        Returns:
            int: period to next tide in degree

        """
        degree = (0 - 180) * ((next_min - 0) / (375 - 0)) + 180
        if next_tide == 'high-tide':
            degree += 180
        return degree

    def haversine(self, coord1, coord2):
        """ Calculates the distance between two coordindates.

        Parameters:
            coord1 (tuple): Coordinate tuple (lat, long)
            coord2 (tuple): Coordinate tuple (lat, long)

        Returns:
            float: Distance in km

        """
        try:
            R = 6372800  # Earth radius in meters
            lat1, lon1 = coord1
            lat2, lon2 = coord2
            phi1, phi2 = math.radians(lat1), math.radians(lat2) 
            dphi       = math.radians(lat2 - lat1)
            dlambda    = math.radians(lon2 - lon1)            
            a = math.sin(dphi/2)**2 + \
                math.cos(phi1)*math.cos(phi2)*math.sin(dlambda/2)**2
            return round(2*R*math.atan2(math.sqrt(a), math.sqrt(1 - a))/1000,1)
        except:
            self.log("Issue calculating the distance " + str(coord1) + " / " + str(coord2), level="WARNING")
            return 0
