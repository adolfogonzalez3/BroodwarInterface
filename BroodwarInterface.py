import numpy as np
import subprocess
from time import sleep, time

from copy import deepcopy

import cybw

def withinBounds(array, lower, upper):
    withinLowerBound = array > lower
    withinUpperBound = array < upper
    return np.logical_and(withinLowerBound, withinUpperBound)
    
def getCenterPosition(unit):
    position = unit.getPosition()
    X = position.x
    Y = position.y
    return np.array([X, Y])

    
class BroodwarInterface(object):

    def __init__(self):
        self.__client = cybw.BWAPIClient
        self.__Broodwar = cybw.Broodwar
        self.events = []
        self.__SPECIAL_UNITS = [cybw.UnitTypes.Special_Map_Revealer]
        
        
    def __getUnitsFiltered(self, function, players=None, types=None, units=None):
        '''Will need a test to ensure consistency of behaviour for all combinations of inputs.'''
        if function is None:
            function = lambda x: x
        
        if players is not None:
            player_condition = lambda x: x.getPlayer().getID() in players
        else:
            player_condition = lambda x: True
        
        if types is not None:
            type_condition = lambda x: x.getType() in types
        else:
            type_condition = lambda x: True
            
        if units is not None:
            unit_condition = lambda x: x.getID() in units
        else:
            unit_condition = lambda x: True

        not_special = lambda x: x.getType() not in self.__SPECIAL_UNITS
            
        all_conditions = lambda x: player_condition(x) and type_condition(x) and unit_condition(x) and not_special(x)
            
        all_units = self.__Broodwar.getAllUnits()
            
        resulting_units = (function(u) for u in all_units if all_conditions(u) is True)
        return resulting_units
       
    def __getEvents(self):
        return [e for e in self.__Broodwar.getEvents()]
       
    def connect(self, speedup=True):
        while not self.__client.connect():
            sleep(0.5)
        events = [e.getType() for e in self.events]
        while cybw.EventType.MatchStart not in events:#not self.__Broodwar.isInGame():
            self.update()
            events = [e.getType() for e in self.events]
        self.__Broodwar.enableFlag(cybw.Flag.CompleteMapInformation)
        
        while not self.isInGame():
            self.update()
        
        if speedup is True:
            self.__Broodwar.setLocalSpeed(0)
            #Broodwar.setGUI(False)
            self.__Broodwar.setFrameSkip(0)
        else:
            self.__Broodwar.setLocalSpeed(167)
            #Broodwar.setGUI(False)
            self.__Broodwar.setFrameSkip(24)
        return True
    
    def isInGame(self):
        return self.__Broodwar.isInGame()
    
    def getUnits(self, players=None, types=None, units=None):
        function = None
    
        return self.__getUnitsFiltered(function, players, types, units)
    
    def getPositions(self, players=None, types=None, units=None):
        function = lambda X: getCenterPosition(X)
        
        return list(self.__getUnitsFiltered(function, players, types, units))
    
    def getHealth(self, players=None, types=None):
        function = lambda X: X.getHitPoints()
            
        return list(self.__getUnitsFiltered(function, players, types))
    
    def getShield(self, players=None, types=None):
        function = lambda X: X.getShield()
            
        return list(self.__getUnitsFiltered(function, players, types))
        
    def getDistanceFromPositionToUnits(self, position, units):
        '''Hasn't been used yet but will need a test if used.'''
        function = lambda X: getCenterPosition(X)
        positions = np.array(self.__getUnitsFiltered(function, units=units))
        unit_position = position
        difference = otherUnits_positions - unit_position
        distance = np.sqrt(np.sum(np.power(difference, 2), axis=1))
            
        return distance
        
    def getDistanceFromUnitToUnits(self, unit, units):
        '''Relies on getDistanceFromPositionToUnits so may not need a test.'''
        function = lambda X: getCenterPosition(X)
            
        return self.getDistanceFromPositionToUnits(function(unit), units)
    
    def getUnitsInRect(self, position, width, height, players=None, types=None):
        '''Hasn't been used much but if used will need a test.'''
        units = np.array(self.getUnits(players, types))
        unit_positions = self.getPositions(players, types)
        difference = unit_positions - position
        in_bounds = withinBounds(difference, np.zeros((1,2)), np.array([width, height]))
        agents_in_bounds = np.all(in_bounds, axis=1)
        
        return units[agents_in_bounds].tolist()
    
    def createUnitsMap(self, position, width, height, players=None, types=None):
        '''Would need a test.'''
        map = np.zeros((height, width), dtype=np.int8)
        unit_positions = self.getPositions(players, types)
        if len(unit_positions) == 0:
            return map
        difference = unit_positions - position
        in_bounds = withinBounds(difference, np.zeros((1,2)), np.array([width, height]))
        agents_in_bounds = np.all(in_bounds, axis=1)
        
        y, x = np.hsplit(difference[agents_in_bounds], 2)
        
        map[y, x] = 1
        
        return map
    
    def getEnemiesID(self):
        return [e.getID() for e in self.__Broodwar.enemies()]
        
    def getSelfID(self):
        return self.__Broodwar.self().getID()
        
    def quit(self):
        self.__Broodwar.leaveGame()
        
    def restart(self):
        self.__Broodwar.restartGame()
        
    def set_map(self, map_name, speedup=True):
        self.__Broodwar.setMap(map_name.encode())
        self.restart()
        
        events = [e.getType() for e in self.events]
        while cybw.EventType.MatchStart not in events: #not self.isInGame():
            self.update()
            events = [e.getType() for e in self.events]
        self.__Broodwar.enableFlag(cybw.Flag.CompleteMapInformation)
        
        while not self.isInGame():
            self.update()
        
        if speedup is True:
            self.__Broodwar.setLocalSpeed(0)
            #Broodwar.setGUI(False)
            self.__Broodwar.setFrameSkip(0)
        else:
            self.__Broodwar.setLocalSpeed(167)
            #Broodwar.setGUI(False)
            self.__Broodwar.setFrameSkip(24)
        
    def get_map_name(self):
        return self.__Broodwar.mapPathName()
        
    def update(self, number_of_updates=None, number_of_secs=None):
        '''Need to make sure that the events is being updated correctly.'''
        if number_of_updates is None and number_of_secs is None:
            self.__client.update()
            self.events = self.__getEvents()
        elif number_of_updates is not None and number_of_secs is None:
            for _ in range(number_of_updates):
                self.__client.update()
                self.events = self.__getEvents()
                if self.is_end() is True:
                    break
        elif number_of_updates is None and number_of_secs is not None:
            stop_on = time() + number_of_secs
            while time() < stop_on:
                self.__client.update()
                self.events = self.__getEvents()
        else:
            assert(False)
            
    def get_map_dimensions(self):
        '''Should be dimensions in pixels. Fix'''
        width = self.__Broodwar.mapWidth()
        height = self.__Broodwar.mapHeight()
        
        return np.array([height, width])
        
    def is_visible(self, players=None, types=None, units=None):
        '''Used to detect if units are visible to the player.
        
            Enemy Units may still exist even if they're not visible.
        '''
        if players is None:
            players = [self.getSelfID()]
        
        units = self.getUnits(players, types, units)
        existing_units = [u.exists() for u in units]
        return existing_units
        
    def getUnitIDs(self, players=None, types=None, units=None):
        '''Convience function to get unit ids.'''
        game_units = self.getUnits(players, types, units)
        unit_ids = [u.getID() for u in game_units]
        return unit_ids
        
    def is_end(self):
        '''Detects if the match has ended.'''
        for e in self.events:
            eventType = e.getType()
            if eventType == cybw.EventType.MatchEnd:
                return True
        return False
        
    def attack_position(self, unit_id, position):
        '''Attack a position with a given unit ID.'''
        X, Y = position
        cybw_position = cybw.Position(X, Y)
        unit = self.__Broodwar.getUnit(unit_id)
        unit.attack(cybw_position)
        
    def get_map_dims(self):
        width = self.__Broodwar.mapWidth()*32
        height = self.__Broodwar.mapHeight()*32
        
        return width, height
        
    def set_viewbox_position(self, position):
        X, Y = position
        cybw_position = cybw.Position(X, Y)
        self.__Broodwar.setScreenPosition(cybw_position)