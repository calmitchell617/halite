# TODO
# Create "offense" by parking a ship on the enemies shipyards.
# IF enemy ship is on shipyard, kill it
# Send em home at the end

# Current version 43


#!/usr/bin/env python3
# Python 3.6

# Import the Halite SDK, which will let you interact with the game.
import hlt

# This library contains constant values.
from hlt import constants

# This library contains direction metadata to better interface with the game.
from hlt.positionals import Direction, Position

# This library allows you to generate random numbers.
import random

# Logging allows you to save messages for yourself. This is required because the regular STDOUT
#   (print statements) are reserved for the engine-bot communication.
import logging

""" <<<Game Begin>>> """

# This game object contains the initial game state.
game = hlt.Game()
game_map = game.game_map
# At this point "game" variable is populated with initial map data.
# This is a good place to do computationally expensive start-up pre-processing.
# As soon as you call "ready" function below, the 2 second per turn timer will start.
ship_dict = {}

cells = []

width = game_map.width

for i in range(width):
    for j in range(width):
        cells.append((i, j))

if width == 32:
    turns = 401
if width == 40:
    turns = 426
if width == 48:
    turns = 451
if width == 56:
    turns = 476
if width == 64:
    turns = 501


game.ready("MyPythonBot")

# Now that your bot is initialized, save a message to yourself in the log file with some important information.
#   Here, you log here your id, which you can always fetch from the game object by using my_id.
logging.info("Successfully created bot! My Player ID is {}.".format(game.my_id))

""" <<<Game Loop>>> """

while True:
    # This loop handles each turn of the game. The game object changes every turn, and you refresh that state by
    #   running update_frame().
    game.update_frame()

    turns_left = turns - game.turn_number
    # You extract player metadata and the updated map metadata here for convenience.
    me = game.me
    game_map = game.game_map

    # A command queue holds all the commands you will run this turn. You build this list up and submit it at the
    #   end of the turn.
    command_queue = []

    logging.info(ship_dict)

    for ship in me.get_ships():

        distance_to_shipyard = game_map.calculate_distance(ship.position, me.shipyard.position)

        if distance_to_shipyard + (len(me.get_ships()) * 2) >= turns_left:
            # if shipyard is next door, move to it.
            surrounding_cardinals = ship.position.get_surrounding_cardinals()
            logging.info('shipyard: {}, ship position: {}'.format(me.shipyard.position, ship.position))
            if me.shipyard.position in surrounding_cardinals:
                move = game_map.get_unsafe_moves(ship.position, me.shipyard.position)[0]
                logging.info(move)
                command_queue.append(ship.move(move))
                continue
            # if not, naively move toward it
            else:
                command_queue.append(
                    ship.move(game_map.naive_navigate(ship, me.shipyard.position)))
                continue

        # If ship doesn't have a status, it must be new. Put it in the ship_dict
        if ship.id not in ship_dict:
            ship_dict[ship.id] = 'exploring'

        # If ship's status is returning, keep going (unless on shipyard)
        if ship_dict[ship.id] == 'returning':

            # If ship isn't on shipyard, keep going home
            if ship.position != me.shipyard.position:
                command_queue.append(
                    ship.move(game_map.naive_navigate(ship, me.shipyard.position)))
                continue

            # If ship is on shipyard, switch to exploring mode 
            else:
                ship_dict[ship.id] = 'exploring'


        # If ship is full, return to shipyard

        if ship.halite_amount >= constants.MAX_HALITE * .9:
            ship_dict[ship.id] = 'returning'

            command_queue.append(ship.move(game_map.naive_navigate(ship, me.shipyard.position)))
            continue

        # If ship is on halite-rich cell, harvest it
        if game_map[ship.position].halite_amount >= 25:
            command_queue.append(ship.stay_still())
            continue

        # Explore for closest cell with a good amount of halite
        else:
            closest_cell = (None, float('inf'))
            for cell in cells:
                map_cell = game_map[Position(cell[0], cell[1])]
                distance = game_map.calculate_distance(ship.position, map_cell.position)
                halite = map_cell.halite_amount
                if halite > 150 and distance < closest_cell[1]:
                    closest_cell = (map_cell, distance)

            command_queue.append(ship.move(game_map.naive_navigate(ship, closest_cell[0].position)))
            continue

    # If the game is in the first 200 turns and you have enough halite, spawn a ship.
    # Don't spawn a ship if you currently have a ship at port, though - the ships will collide.
    if game.turn_number <= turns / 3 and me.halite_amount >= constants.SHIP_COST and not game_map[me.shipyard].is_occupied:
        command_queue.append(me.shipyard.spawn())

    # Send your moves back to the game environment, ending this turn.
    game.end_turn(command_queue)

