'''A module that provides convienent functions necessary for the project.

All methods called on __Broodwar and __client are BWAPI methods which have
documentation: https://bwapi.github.io/namespace_b_w_a_p_i.html

-Unit Types are described
 here: https://bwapi.github.io/namespace_b_w_a_p_i_1_1_unit_types.html
 
-Methods for the unit interface are
 here: https://bwapi.github.io/class_b_w_a_p_i_1_1_unit_interface.html
 
-Functions which work on the state of the game, such as gathering units or
 setting up speedups are
 here: https://bwapi.github.io/class_b_w_a_p_i_1_1_game.html
 
Not all functions in the BWAPI are implemented for the python version so there
may be functions that don't work.
'''

import numpy as np
from time import sleep, time

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
        '''Get units based on criteria given.
        
        This function is a base function used to generalize gathering info from
        units based on criteria, such as if the unit is owned by a certain player
        or is a certain unit type.
        
        function: A lambda function which is used to gather a particular element
        such as unit health or position.
        
        players: A list of player IDs used to select units belonging to units
        from one of the player IDs in the list.
        
        types: A list of unit types used to select units of a particular type
        The unit types are specified in the BWAPI documentation.
        
        units: A list of unit IDs used to select particular units.
        
        Will need a test to ensure consistency of behaviour for all combinations of inputs.
        '''
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
            
        resulting_units = [function(u) for u in all_units if all_conditions(u) is True]
        
        return resulting_units
       
    def __getEvents(self):
        '''Gather all events currently held by BWAPI into a list.'''
        return [e for e in self.__Broodwar.getEvents()]
       
    def connect(self, speedup=True):
        '''Connect with BWAPI.
        
        Must be run before accessing other BWAPI functions.
        The speedup parameter allows speedup functions to be disabled if 
        necessary such as when debugging.
        '''
        while not self.__client.connect():
            sleep(0.5)
        events = [e.getType() for e in self.events]
        while cybw.EventType.MatchStart not in events:
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
        '''Check if the game is currently in a match.'''
        return self.__Broodwar.isInGame()
    
    def getUnits(self, players=None, types=None, units=None):
        '''Gathers all units based on criteria.
        
        This function returns a list of unit interfaces which have methods
        described in the BWAPI documentation website.
        '''
        function = None
    
        return self.__getUnitsFiltered(function, players, types, units)
    
    def getPositions(self, players=None, types=None, units=None):
        '''Gather all unit positions that fit the criteria.
        
        Returns a list of positions where each position is a tuple of two
        integers.
        '''
        function = lambda X: getCenterPosition(X)
        
        return list(self.__getUnitsFiltered(function, players, types, units))
    
    def getHealth(self, players=None, types=None, units=None):
        '''Gather all unit health that fit the criteria.
        
        Returns the health points of units as an integer that is between 0 and
        the unit types max hitpoints.
        '''
        function = lambda X: X.getHitPoints()
            
        return list(self.__getUnitsFiltered(function, players, types, units))
    
    def getShields(self, players=None, types=None, units=None):
        '''Gather all unit shields that fit the criteria.
        
        Returns the shield points of units as an integer that is between 0 and
        the unit type's max shield points.
        '''
        function = lambda X: X.getShields()
            
        return list(self.__getUnitsFiltered(function, players, types, units))
        
    def getDistanceFromPositionToUnits(self, position, units):
        '''Get the euclidian distance of all units from a given position.'''
        function = lambda X: getCenterPosition(X)
        positions = np.array(self.__getUnitsFiltered(function, units=units))
        unit_position = position
        difference = otherUnits_positions - unit_position
        distance = np.sqrt(np.sum(np.power(difference, 2), axis=1))
            
        return distance
        
    def getDistanceFromUnitToUnits(self, unit, units):
        '''Get the euclidian distance of all units from a particular unit.'''
        function = lambda X: getCenterPosition(X)
            
        return self.getDistanceFromPositionToUnits(function(unit), units)
    
    def getUnitsInRect(self, position, width, height, players=None, types=None):
        '''Get all units that are within a rectangular area.'''
        units = np.array(self.getUnits(players, types))
        unit_positions = self.getPositions(players, types)
        difference = unit_positions - position
        in_bounds = withinBounds(difference, np.zeros((1,2)), np.array([width, height]))
        agents_in_bounds = np.all(in_bounds, axis=1)
        
        return units[agents_in_bounds].tolist()
    
    def createUnitsMap(self, position, width, height, players=None, types=None):
        '''Produce a matrix containings positions of units relative to a position.
        
        '''
        map = np.zeros((height, width))
        unit_positions = self.getPositions(players, types)
        if len(unit_positions) == 0:
            return map
        difference = unit_positions - position
        in_bounds = withinBounds(difference, np.zeros((1,2)), np.array([width, height]))
        agents_in_bounds = np.all(in_bounds, axis=1)
        
        y, x = np.hsplit(difference[agents_in_bounds], 2)
        
        map[y, x] = 1
        
        return map
        
    def createUnitsMapHealth(self, position, width, height, players=None, types=None):
        '''Produce a matrix containing the health of units within a rectangular area.'''
        map = np.zeros((height, width))
        unit_positions = self.getPositions(players, types)
        unit_health = np.add(self.getHealth(players, types), self.getShields(players, types)).reshape((-1, 1))
        if len(unit_positions) == 0:
            return map
        difference = unit_positions - position
        in_bounds = withinBounds(difference, np.zeros((1,2)), np.array([width, height]))
        agents_in_bounds = np.all(in_bounds, axis=1)
        
        y, x = np.hsplit(difference[agents_in_bounds], 2)
        
        map[y, x] = unit_health[agents_in_bounds]
        
        return map
    
    def getEnemiesID(self):
        '''Gather the IDs of the enemy players.'''
        return [e.getID() for e in self.__Broodwar.enemies()]
        
    def getSelfID(self):
        '''Get the players ID.'''
        return self.__Broodwar.self().getID()
        
    def quit(self):
        '''Leave the current match.'''
        self.__Broodwar.leaveGame()
        
    def restart(self):
        '''Restart the currrent match.'''
        self.__Broodwar.restartGame()
        
    def set_map(self, map_name, speedup=True):
        '''Set the map to the specified map and then start the match.'''
        self.__Broodwar.setMap(map_name.encode())
        self.restart()
        
        events = [e.getType() for e in self.events]
        while cybw.EventType.MatchStart not in events: #not self.isInGame():
            self.update()
            events = [e.getType() for e in self.events]
        self.__Broodwar.enableFlag(cybw.Flag.CompleteMapInformation)
        
        while not self.isInGame():
            self.update()
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
        '''Get the current map name.'''
        return self.__Broodwar.mapPathName()
        
    def update(self, number_of_updates=None, number_of_secs=None):
        '''Step through the game.
        
        Allows for stepping multiple times.
        '''
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
        '''Get the dimensions of the current map in Tiles.
        
        Tiles: Broodwar evenly divides the map into tiles. A tile is 32 by 32
        pixels.
        '''
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
        '''Gather unit IDs based on criteria.'''
        game_units = self.getUnits(players, types, units)
        unit_ids = [u.getID() for u in game_units]
        return unit_ids
        
    def is_end(self):
        '''Detect if the match has ended.'''
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
        return unit.attack(cybw_position)
        
    def move_to_position(self, unit_id, position):
        '''Move a unit to a position given its ID.'''
        X, Y = position
        cybw_position = cybw.Position(X, Y)
        unit = self.__Broodwar.getUnit(unit_id)
        return unit.move(cybw_position)
        
    def use_stim_pack(self, unit_id):
        '''Use a stim pack on units with the ability to do so.
        
        This is a ability that a few unit types have, such as the marine.
        '''
        unit = self.__Broodwar.getUnit(unit_id)
        return unit.useTech(cybw.TechTypes.Stim_Packs)
        
    def get_map_dims(self):
        '''Get the pixel width and pixel height of the current map.'''
        width = self.__Broodwar.mapWidth()*32
        height = self.__Broodwar.mapHeight()*32
        
        return width, height
        
    def set_viewbox_position(self, position):
        '''Set the current viewbox on a given position.'''
        X, Y = position
        cybw_position = cybw.Position(X, Y)
        self.__Broodwar.setScreenPosition(cybw_position)