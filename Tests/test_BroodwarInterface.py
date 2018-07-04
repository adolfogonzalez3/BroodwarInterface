'''Must test BroodwarInterface differently due to how BWAPI interacts with cybw.'''

import os
import pygame
import numpy as np
import matplotlib.pyplot as plt
from time import sleep, time
import cybw

from BroodwarInterface import BroodwarInterface

def reduce(array, reduceBy=2):
    '''Reduce the size of an array by squashing the array.

    If there exists a conflict with merging adjacent cells of differing values,
    add their values together and if the sum is less than zero make the value
    -1 otherwise 1'''
    width, height = array.shape
    new_array = np.zeros((int(width/reduceBy), int(height/reduceBy)))
    array[0:reduceBy, 0:reduceBy]
    for x in range(0, reduceBy):
        for y in range(0, reduceBy):
            new_array = new_array + array[x::reduceBy,y::reduceBy]
    new_array[new_array < 0] = -1
    new_array[new_array > 0] = 1
    #new_array = new_array/reduceBy**2
    return new_array

def test_createUnitMap(interface, map):
    interface.connect()
    interface.set_map(large_map)
    while interface.is_end():
        if interface.isInGame() and interface.is_visible(player):
            ally_units = [u.getID() for u in interface.getUnits(players=player)]
            print('Ally Units: ', ally_units)
            enemy_units = interface.getUnitIDs(players=enemy)
            print('Enemy Units: ', enemy_units)
            enemy_positions = interface.getPositions(players=enemy)
            if len(enemy_positions) != 0:
                position = enemy_positions[0]
            else:
                position = [0, 0]
            for u in ally_units:
                interface.attack_position(u, position)
        
            ally_positions = interface.getPositions(players=player, types=ally_type)
            ally = ally_positions[0] - np.array([512, 512])
            ally_area = interface.createUnitsMap(ally, 1024, 1024, players=player)
            reduced_ally_area = reduce(ally_area, 16)
            boosted_ally_area = reduced_ally_area*255
            
            enemy_area = interface.createUnitsMap(ally, 1024, 1024, players=enemy)
            reduced_enemy_area = reduce(enemy_area, 16)
            boosted_enemy_area = reduced_enemy_area*255
            
            empty_layer = np.zeros((64, 64))
            rgb_image = np.stack([boosted_ally_area, empty_layer, boosted_enemy_area],
                                axis=-1)
            
            surf_area = pygame.surfarray.make_surface(rgb_image)
            scaled_surf_area = pygame.transform.scale(surf_area, (1024, 1024))
            screen.blit(scaled_surf_area, (0, 0))
            pygame.display.update()
            pygame.event.clear()
        interface.update()
    

def test_set_map(interface, maps):
    interface.connect()
    for map in maps:
        interface.set_map(map)
        assert(interface.get_map_name() == 'maps\\{}'.format(map))
        
def test_connect(interface):
    if interface.connect():
        assert('Broodwar instance not detected.')
        
def test_update(interface, map):
    interface.connect()
    interface.set_map(map)
    begin = time()
    interface.update(number_of_secs=0.5)
    elapsed = time()-begin
    assert(np.isclose(elapsed, 0.5, atol=1))

def test_getUnits(interface, maps, numbers):
    interface.connect()
    for map, num in zip(maps, numbers):
        interface.set_map(map)
        units = interface.getUnits()
        units = set([u.getID() for u in units])
        print('All IDs: ', units)
    
if __name__ == '__main__':
    
    interface = BroodwarInterface()
    map_path = os.environ['BROODWAR_MAP_PATH']
    test_map = os.path.join(map_path, 'test.scm')
    
    positions = interface.getPositions()
    print(positions)
    position = positions[0] - np.array([512, 512])
    area = interface.createUnitsMap(position, 1024, 1024)
    #print(area[512, 512])
    area = reduce(area, 16)
    #print(np.sum(area))
    #plt.imshow(area)
    #plt.show()
    boosted_area = area*255
    surf_area = pygame.surfarray.make_surface(boosted_area)
    pygame.init()
    screen = pygame.display.set_mode((1024, 1024))
    scaled_surf_area = pygame.transform.scale(surf_area, (1024, 1024))
    rotated_surf_area = pygame.transform.rotate(scaled_surf_area, 90)
    screen.blit(rotated_surf_area, (0, 0))
    pygame.display.update()
    
    large_map_name = '20Mv30Zergling.scm'
    large_map = os.path.join(map_path, large_map_name)
    interface.set_map(large_map)
    
    units = interface.getUnits()
    units = set([u.getPlayer().getID() for u in units])
    print('All IDs: ', units)
    
    player = [interface.getSelfID()]
    print('Player ID: ', player)
    ally_type = [cybw.UnitTypes.Terran_Marine]
    enemy = interface.getEnemiesID()
    print('Enemy IDs: ', enemy)
    
    ally_units = [u.getID() for u in interface.getUnits(players=player)]
    test = np.array([u.getID() for u in interface.getUnits(units=ally_units)])
    print('Ally unit IDs: ', ally_units)
    print('Test unit IDs: ', test)
    print('Checking for consistency: ', np.all(ally_units == test))
    positions = interface.getPositions(units=ally_units)
    print('Ally Positions: ', positions)
    f = lambda U: (U.x, U.y)
    ally_positions = np.array([f(u.getPosition()) for u in interface.getUnits(players=player)])
    print('Test Positions: ', ally_positions)
    print('Positions Equal: ', np.all(positions == ally_positions))
    
    #test_ids = interface.getUnitIDs(units=ally_units)
    #print(ally_units)
    #print(test_ids)
    
    #print('All Units: ', interface.getPositions().shape)
    #print('Player Units: ', interface.getPositions(players=player).shape)
    #print('Enemy Units: ', interface.getPositions(players=enemy).shape)
    
    test_createUnitMap(interface, test_map)
    
    
    
    '''interface.connect()
    while True:
        if interface.is_end() is True:
            print('Game End', interface.is_end())
            interface.set_map(large_map)
            ally_units = [u.getID() for u in interface.getUnits(players=player)]
            print(ally_units)
        elif interface.isInGame() and interface.is_visible(player):
            ally_units = [u.getID() for u in interface.getUnits(players=player)]
            print('Ally Units: ', ally_units)
            enemy_units = interface.getUnitIDs(players=enemy)
            print('Enemy Units: ', enemy_units)
            enemy_positions = interface.getPositions(players=enemy)
            if len(enemy_positions) != 0:
                position = enemy_positions[0]
            else:
                position = [0, 0]
            for u in ally_units:
                interface.attack_position(u, position)
        
            ally_positions = interface.getPositions(players=player, types=ally_type)
            ally = ally_positions[0] - np.array([512, 512])
            ally_area = interface.createUnitsMap(ally, 1024, 1024, players=player)
            reduced_ally_area = reduce(ally_area, 16)
            boosted_ally_area = reduced_ally_area*255
            
            # test_pos = np.array([f(u.getPosition()) for u in interface.getUnits(players=player)])
            # print(np.all(ally_positions == test_pos))
            
            enemy_area = interface.createUnitsMap(ally, 1024, 1024, players=enemy)
            reduced_enemy_area = reduce(enemy_area, 16)
            boosted_enemy_area = reduced_enemy_area*255
            
            empty_layer = np.zeros((64, 64))
            rgb_image = np.stack([boosted_ally_area, empty_layer, boosted_enemy_area],
                                axis=-1)
            
            surf_area = pygame.surfarray.make_surface(rgb_image)
            scaled_surf_area = pygame.transform.scale(surf_area, (1024, 1024))
            screen.blit(scaled_surf_area, (0, 0))
            pygame.display.update()
            pygame.event.clear()
        interface.update()'''