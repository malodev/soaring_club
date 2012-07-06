# Copyright (C) 2009 Mauro Longano <mlongano@gmail.com>
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
"""
Module containing class for aircraft info and a class to Collecting
all aircraft
"""

import time
from configobj import ConfigObj
from UserDict import DictMixin
import models

config = ConfigObj('planeslog.ini')

class Error(Exception):
    """Base class for exceptions in this module."""
    pass

class PlaneIDError(Error):
    """Exception raised when plane has no ID.

    """
    pass

#Constant identifying aircraft position
UNKNOWN_POSITION = -1
ON_GROUND, IN_FLIGHT = range(2)
ACCEPTED_POSITION = range(2) 

class Plane(object):
    """Store plane log information"""
    
    def __init__(self, flarm_id=None,
                 regmark=None,
                 pilot=None,
                 owners = None,
                 config=None,
                 date=time.localtime(),
                 ):
        """Initialize plane log instance. Instance must be identified by flarm_id
        or regmark. If they are both None init rise an Exception

        """
        if flarm_id is None and regmark is None:
            raise PlaneIDError("You have to give either falrm id or mark")
        if flarm_id is None:
            self.flarm_id = regmark
        else:
            self.flarm_id = flarm_id
        if regmark is None:
            self.regmark = flarm_id
        else:
            self.regmark = regmark
      
        self.date = {}
        self.date['takeoff'] = None
        self.date['landing'] = None
        self.airport = {}

        if not config is None:
            self.airport['takeoff'] = config['defaults']['airport']
        else:
            self.airport['takeoff'] = 'Unknown'

        self.airport['landing'] = self.airport['takeoff']

        self.owners = []
        self.pilot = pilot
        self.cents = 0
        self.state = {'speed':None,
                      'heading':None,
                      'altitude':None,
                      'position':UNKNOWN_POSITION}
        self.is_info_good = True
        self.info_bad_status = ''
        self.speed = None
        self.heading = None
        self.altitude = None
    
    def reset_info_status(self):
        self.is_info_good = True
        self.info_bad_status = ''
        
    def set_position(self,value):
        if value in ACCEPTED_POSITION:
            self.state['position'] = value
        else:
            self.state['position'] = UNKNOWN_POSITION
            
    def get_position(self):
        return self.state['position']
    
    position = property(get_position, set_position)
            
    def update_takeoff_date(self, date):
        '''
        
        @param date:
        '''
        self.date['takeoff'] = date
        
    def update_landing_date(self, date):
        '''
        
        @param date:
        '''
        self.date['landing'] = date

    def is_in_flight(self):
        '''
        
        '''
        return self.state['position'] == IN_FLIGHT

    def set_in_flight(self):
        '''
        
        '''
        self.state['position'] = IN_FLIGHT


    def is_on_ground(self):
        '''
        
        '''
        return self.state['position'] == ON_GROUND

    def set_on_ground(self):
        '''
        
        '''
        self.state['position'] = ON_GROUND

    def is_in_unknown_position(self):
        '''
        return True if plane position is unknown
        '''
        return self.state['position'] == UNKNOWN_POSITION

    def set_unknown_position(self):
        '''Set plane position to unknown'''
        self.state['position'] = UNKNOWN_POSITION
    

class ActivePlanes(DictMixin):
    """Store the list of planes that have to be accounting"""
    def __init__(self):
        self._planes = {}

    def __getitem__(self, plane_id):
        return self._planes[plane_id]

    def __setitem__(self, plane_id, value):
        """If there's already a plane with that plane_id do nothing"""
        if plane_id not in self._planes:
            self._planes[plane_id] = value

    def __delitem__(self, plane_id):
        del self._planes[plane_id]

    def keys(self):
        return self._planes.keys()


    def add_plane(self, plane):
        if plane.regmark not in self._planes:
            self._planes[plane.regmark] = plane
            return True
        else:
            return False

class PlanesLog(object):
    def __init__(self):
        self.log=[]

    def add_entry(self, plane):
        entry = {}
        entry['flarm_id'] = plane.flarm_id
        entry['takeoff'] = plane.date['takeoff']
        entry['landing'] = plane.date['landing']
        self.log.append(entry)
        
   
if __name__ == '__main__':
    logs = ActivePlanes()
    plane_id = '12344'
    logs[plane_id] = Plane(plane_id, config=config)
    for l in logs.keys():
        print logs[l].flarm_id,logs[l].airport['takeoff'], logs[l].inflight
        
