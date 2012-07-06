# Copyright (C) 2009 Mauro Longano <mlongano@gmail.com>
# Derived from nmea.py Twisted module by Matthew W. Lefkowitz
#
# This file is part of Aircrafts Logbook.
#
# Aircrafts Logbook is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Aircrafts Logbook is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser Public License for more details.
#
# You should have received a copy of the GNU Lesser Public License
# along with Aircrafts Logbook.  If not, see <http://www.gnu.org/licenses/

"""NMEA 0183 and Biofly(TM) extension parser for logging aircrafts

Maintainer: U{Mauro Longano<mailto:mlongano@gmail.com>}

The following NMEA 0183 sentences are currently understood::
    GPGGA (fix)
    GPRMC (position and time)

The following Biofly extension sentences are currently understood::
    PSK (aircraft information received from a Flarm device)
    
"""

#TODO: Add entry that don't have landing time but only takeoff time
#TODO: Merge files that have same date
#FIXME: What if we got takeoff time and landing time but there are other takeoff and landing in the middle that we aren't aware of? 

from configobj import ConfigObj
from planeslog import Plane, ActivePlanes
from debug import degug_print #IGNORE:W0401
import csv
import glob
import math
import operator

EARTH_MEAN_RADIUS = 6371009 # mean earth radius
FLARM_DB = 'flarm.ini' # INI file where flarm is associated to registration mark and other informations
CSV_FILE = '/tmp/ramstein.csv' # file where test code write csv records
#BIOFLY_LOG_FILES = '../rec/*0409*.txt' # pattern of Biofly log files to processes
#BIOFLY_LOG_FILES = '/media/CUS/Programmi/biofly/BESVS_BESVS_TOWER/rec/*0409*.txt' # pattern of Biofly log files to processes
BIOFLY_LOG_FILES = '/tmp/Ramstein1*.txt' # pattern of Biofly log files to processes


class InvalidSentence(Exception):
    '''
    Exception raised when the sentence is invalid
    '''
    pass

class InvalidChecksum(Exception):
    '''
    Exception raised when checksum is invalid
    '''
    pass

#utility functions
def head_tail(sequence):
    '''
    
    @param sequence:
    '''
    try:
        head, tail = sequence[0], sequence[1:]
    except IndexError:
        head = None
        tail = []
    return (head, tail)

def map_to_int(sequence, ignore_error = True, ignored_value = None):
    list_of_int = []
    for element in sequence:
        try:
            int_value = int(element)
            list_of_int.append(int_value)
        except ValueError:
            if ignore_error:
                list_of_int.append(ignored_value)
            else:
                raise ValueError
    return list_of_int

def map_to_str(sequence):
    return [str(x) for x in sequence]

def seconds_to_cents(seconds):
    return round((seconds/60.0 * 100) / 60.0, 1)

def seconds_to_hours_minutes(seconds):
    hours = seconds // 3600
    minutes = (seconds % 3600)//60
    return '%02d.%02d' % (hours,minutes)

def check_time(time_tuple):
    for val in time_tuple:
        if val < 0:
            return False
    return True

def delta_time(t1,t2):
    '''t1 and t2 are list of hours,minutes,seconds of type int. Seconds are ignored'''
    if check_time(t1) and check_time(t2):
        minutes1 = t1[0]*60 + t1[1]
        minutes2 = t2[0]*60 + t2[1]
        delta = abs(minutes2-minutes1)
        hours = delta // 60
        minutes = (delta % 60)
        return '%02d.%02d' % (hours, minutes)
    else:
        return '??.??' 

#TODO: defining function to compute air distance from latitude, longitude, altitude
def great_circle_distance(position1, position2):
    '''
    
    @param position1:
    @param position2:
    '''
    R = EARTH_MEAN_RADIUS
    lat1,long1=position1
    lat2,long2=position2
    return math.acos(math.sin(lat1)*math.sin(lat2)+math.cos(lat1)*math.cos(lat2)*math.cos(long2-long1))*R

def air_distance(position1, position2, altitude2):
    '''
    
    @param position1:
    @param position2:
    @param altitude2:
    '''
    R = EARTH_MEAN_RADIUS

def _int(string):
    '''
    
    @param string:
    '''
    try:
        return int(string)
    except ValueError:
        return 0

def _float(string):
    '''
    
    @param string: string to convert to float
    '''
    try:
        return float(string)
    except ValueError:
        return 0

def decode_utc(utc):
    '''
    
    @param utc: utc time string formatted as hhmmss
    @return: tuple of ints (hh, mm, ss)  
    '''
    utc_hh, utc_mm, utc_ss = (int(utc[:2]), int(utc[2:4]), int(utc[4:6]))
    return (utc_hh, utc_mm,  utc_ss)


def decode_latlon(latitude, n_or_s, longitude, e_or_w):
    '''
    
    @param latitude:
    @param n_or_s: character 'N' or 'S' for north or south
    @param longitude:
    @param e_or_w: character 'E' or 'W' for east or west
    '''
    try:
        latitude = float(latitude[:2]) + float(latitude[2:])/60.0
    except ValueError:
        latitude = 0.0
    if n_or_s == 'S':
        latitude = -latitude
    try:
        longitude = float(longitude[:3]) + float(longitude[3:])/60.0
    except ValueError:
        longitude = 0.0
    if e_or_w == 'W':
        longitude = -longitude
    return (latitude, longitude)


    
class TowerLog(object):
    """This class parses log sentences and update its status accordingly
    """

    delimiter = '\r\n'
    dispatch = {
        'GPGGA': 'fix',
        'GPRMC': 'position_time',
        'PSK': 'plane_state'
    }
    #TODO: Some of this parameters have to be moved to a configuration file.
    # generally you may miss the beginning of the first message
    ignore_invalid_sentence = True
    # checksums shouldn't be invalid
    ignore_checksum_mismatch = False
    # ignore unknown sentence types
    ignore_unknown_sentencetypes = False
    # do we want to even bother checking to see if it's from the 20th century?
    convert_dates_before_y2k = False
    
    #speed threshold for takeoff in km/h
    takeoff_speed = 60
    #speed threshold for landing in km/h
    landing_speed = 30
    #altitude margin in meters. This value have to take in consideration also the offset of GPS antenna from ground
    altitude_margin = 40


    def __init__(self):
        """init tower object to a default status"""
        self._default_status()
        self.log = []
        self.is_live_log = False
        
    def _default_status(self):
        '''
        set attribute to a default value. We use this method to reinitialize status 
	for every log file processing
        '''
        self.time = '??/??/???? ??:??:??' #IGNORE:W0201
        self.latitude = 0.0 #IGNORE:W0201
        self.longitude = 0.0 #IGNORE:W0201
        self.tower_altitude = 0.0 #IGNORE:W0201
        self.track = 0.0 #IGNORE:W0201
        self.speed = 0.0 #IGNORE:W0201
        self.hdop = 0 #IGNORE:W0201
        self.satellites = 0 #IGNORE:W0201
        self.active_planes = ActivePlanes() #IGNORE:W0201
        
    def handle_line(self, line):
        '''
        Check if the sentence has the correct checksum and dispatch the payload info
        to correct processor depending on the sentence type.
        
        @param line: sentence to parse
        '''
        if not line.startswith('$'):
            if self.ignore_invalid_sentence:
                return
            raise InvalidSentence("%r does not begin with $" % (line,))
        
        # message is everything between $ and *, checksum is xor of all ASCII
        # values of the message
        sentence_line, checksum = line[1:].strip().split('*')
        sentence = sentence_line.split(',')
        sentencetype, sentence = sentence[0], sentence[1:]
        dispatch = self.dispatch.get(sentencetype, None)

        if (not dispatch) and (not self.ignore_unknown_sentencetypes):
            raise InvalidSentence("sentencetype %r" % (sentencetype,))
        if not self.ignore_checksum_mismatch:
            checksum = int(checksum, 16)
            calculated_checksum = reduce(operator.xor, 
                                         [ord(x) for x in sentence_line])
        if checksum != calculated_checksum:
            raise InvalidChecksum("Given 0x%02X != 0x%02X" % 
                                  (checksum, calculated_checksum))
        processor = getattr(self, "process_%s" % dispatch, None)
        if not (dispatch and processor):
            # missing dispatch and processor
            return
        # return handler(*decoder(*message))
        try:
            processor(*sentence)
        except TypeError, error:
            degug_print('==>', dispatch, error.message, '\n\t\t\t', 
                        sentence, '\n\t\t\t', sentence_line)
            if not self.ignore_invalid_sentence:
                raise InvalidSentence("%r is not a valid %s (%s) sentence" % 
                                      (line, sentencetype, dispatch))

    def process_position_time(self, 
                              utc, 
                              status, 
                              latitude, n_or_s, 
                              longitude, e_or_w, 
                              speed, 
                              track, 
                              utcdate, 
                              magvar, magdir, 
                              *args):
        """
        Process GPRMC sentence as defined below: 
        RMC - Recommended minimum specific GPS/Transit data
        RMC,225446,A,4916.45,N,12311.12,W,000.5,054.7,191194,020.3,E*68
           225446       Time of fix 22:54:46 UTC
           A            Navigation receiver warning A = OK, V = warning
           4916.45,N    Latitude 49 deg. 16.45 min North
           12311.12,W   Longitude 123 deg. 11.12 min West
           000.5        Speed over ground, Knots
           054.7        Course Made Good, True
           191194       Date of fix  19 November 1994
           020.3,E      Magnetic variation 20.3 deg East
           *68          mandatory checksum

        """

        if status == "A":
            self.latitude, self.longitude = decode_latlon(latitude, n_or_s, 
                                                          longitude, e_or_w)
            if speed != '':
                speed = float(speed)
            else:
                speed = None
            if track != '':
                track = float(track)
            else:
                track = None
            utc = decode_utc(utc)
            utcdate = (int(utcdate[0:2]), 
                       int(utcdate[2:4]), 
                       2000+int(utcdate[4:6]))  
            if self.convert_dates_before_y2k and utcdate[2] > 2073:
                # GPS was invented by the US DoD in 1973, but NMEA uses 2 digit
                # year.
                # Highly unlikely that we'll be using NMEA or this twisted 
                # module in 70 years, but remotely possible that you'll be 
                # using it to play back data from the 20th century.
                utcdate = (utcdate[0], utcdate[1], utcdate[2] - 100)
    
            self.time = ("%02d/%02d/%04d %02d:%02d:%02d" % (utcdate+utc))
            self.speed = speed
            self.track = track

        
    def process_fix(self, 
                    utc,        
                    latitude, n_or_s, 
                    longitude, e_or_w, 
                    posfix, 
                    satellites, 
                    hdop, 
                    altitude, altitude_units, 
                    geoid_separation, geoid_separation_units, 
                    dgps_age, dgps_station_id, 
                    *args):
        """
        Process GPGGA sentence as defined below: 
        GGA - essential fix data which provide 3D location and accuracy data.
        
         $GPGGA,123519,4807.038,N,01131.000,E,1,08,0.9,545.4,M,46.9,M,,*47
        
        Where:
             GGA          Global Positioning System Fix Data
             123519       Fix taken at 12:35:19 UTC
             4807.038,N   Latitude 48 deg 07.038' N
             01131.000,E  Longitude 11 deg 31.000' E
             1            Fix quality: 0 = invalid
                                       1 = GPS fix (SPS)
                                       2 = DGPS fix
                                       3 = PPS fix
                                       4 = Real Time Kinematic
                                       5 = Float RTK
                                       6 = estimated (dead reckoning) (2.3 feature)
                                       7 = Manual input mode
                                       8 = Simulation mode
             08           Number of satellites being tracked
             0.9          Horizontal dilution of position
             545.4,M      Altitude, Meters, above mean sea level
             46.9,M       Height of geoid (mean sea level) above WGS84 ellipsoid
             (empty field) time in seconds since last DGPS update
             (empty field) DGPS station ID number
             *47          the checksum data, always begins with *
        """
        self.latitude, self.longitude = decode_latlon(latitude, n_or_s, 
                                                            longitude, e_or_w)
        self.satellites = _int(satellites)
        self.hdop = _float(hdop)
        self.tower_altitude = _float(altitude)
             
    def process_plane_state(self, 
                            p1, 
                            latitude, longitude, altitude, head, 
                            p6, p7, 
                            speed, 
                            id1, 
                            flarm_id, 
                            *args):

        """
        Process PSK sentence as described below:
        PSK - Biofly Sentence
        PSK,100,46.01862,11.15967,1139,267,0,0,108,DD9F36n3,DD9F36*27            
           100          ????
           46.01862     Latitude 46.01862 (+ is N)
           11.15967     Longitude 11.15967 deg (+ is E)
           1139         Altitude, Metres, above mean sea level
           267          Heading
           0            ????
           0            ????
           108          Ground speed
           DD9F36n3     ????
           DD9F36       Flarm Id (ICAO ID)


        """                     
        if speed == '' or flarm_id == '':
            return
        try:
            plane = self.active_planes[flarm_id]
        except KeyError:
            self.active_planes[flarm_id] = Plane(flarm_id)
            plane = self.active_planes[flarm_id]
                    
        (plane.state['speed'], 
        plane.state['heading'],
        plane.state['altitude']) = speed, head, altitude
        altitude_threshold = self.tower_altitude + self.altitude_margin

        if plane.is_in_unknown_position():
            if (float(speed) > self.takeoff_speed and 
                float(altitude) > altitude_threshold):
                degug_print('==>Bad takeoff time:%s flarm_id:%s, speed:%s, altitude:%s' % 
                            (self.time, flarm_id, speed, altitude))
                plane.set_in_flight()
                plane.update_takeoff_date(self.time)              
                plane.is_info_good = False
                plane.info_bad_status += ('- Bad takeoff time: got after takeoff (speed:%s, altitude:%s) -' % 
                                          (speed,altitude))
            else:
                plane.set_on_ground()
                
        elif plane.is_on_ground() and float(speed) > self.takeoff_speed:
            if float(altitude) > altitude_threshold:
                plane.is_info_good = False
                plane.info_bad_status += ('- Bad takeoff time: altitude error (speed:%s, altitude:%s) -' % 
                                          (speed,altitude))
            plane.set_in_flight()
            plane.update_takeoff_date(self.time)
        elif (plane.is_in_flight() and 
              float(altitude) < altitude_threshold and 
              float(speed) < self.landing_speed):
            plane.set_on_ground()
            plane.update_landing_date(self.time)
            self.add_entry(plane)
            #plane info status has to be resetting!!!
            plane.reset_info_status()
    
    def add_entry(self, plane):
        '''
        
        @param plane: Plane object from witch extract information for logging purpose
        
        Extract informations from plane and add an entry to log
        
        '''
        entry = {}
        entry['flarm_id'] = plane.flarm_id
        entry['takeoff'] = plane.date['takeoff']
        entry['landing'] = plane.date['landing']
        if plane.date['takeoff'][:10] != plane.date['landing'][:10]:
            plane.is_info_good = False
            plane.info_bad_status += '- Date of takeoff and landing differs -'
        entry['is_info_good'] = plane.is_info_good
        entry['info_bad_status'] = plane.info_bad_status
        self.log.append(entry)
    
    
    def process_logs(self, files):
        '''Process each file in files. Files must be in Tower Station format''' 
        for file_name in files:
            self._default_status()
            for line in open(file_name,'r'):
                self.handle_line(line)

    def process_file(self, file_log):
        '''Process file object. File must be in Tower Station format''' 
        self._default_status()
        for line in file_log:
            self.handle_line(line)
    
    def generate_log_book(self):
        '''Generate a log that has the format suitable for club accounting'''
        #TODO: define informations and order to records and makes it customizable
        #TODO: choose a solution for matching flarm_id, registration mark and pilot
        #TODO: check the validity against the date in INI file
        config = ConfigObj(FLARM_DB)
        
        for entry in self.log:
            if config.has_key(entry['flarm_id']):
                regmark = config[entry['flarm_id']]['regmark']
            else:
                regmark = entry['flarm_id']
            takeoff_date, takeoff_time = entry['takeoff'].split(' ') # splitting date and time
            landing_date, landing_time = entry['landing'].split(' ')
            takeoff_date = '-'.join(takeoff_date.split('/')[::-1]) # we record data as dd/mm/yyyy 
            takeoff_time = map_to_int(takeoff_time.split(':'),ignored_value=-1)
            landing_date = '-'.join(landing_date.split('/')[::-1])
            landing_time = map_to_int(landing_time.split(':'),ignored_value=-1)
            fligth_duration = delta_time(takeoff_time, landing_time)
            record = [landing_date,
                      regmark, 
                      '%02d.%02d' % tuple(takeoff_time[:2]),
                      '%02d.%02d' % tuple(landing_time[:2]),
                      fligth_duration,
                      entry['is_info_good'],
                      entry['info_bad_status'] 
                      ]
            yield record
            

    def write_log_book(self, file_name):
        '''Write log book to a csv file'''
        writer = csv.writer(open(file_name, "wb"))
        writer.writerows(self.generate_log_book())
            
if __name__ == '__main__':
    # Self-testing code goes here.
    nmea = TowerLog()
    files = glob.glob(BIOFLY_LOG_FILES)
    nmea.process_logs(files)
#    for record in nmea.generate_log_book():
#        print record
    nmea.write_log_book(CSV_FILE)
