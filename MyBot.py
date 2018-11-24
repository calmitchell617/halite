#!/usr/bin/env python3
# Python 3.6

# Import the Halite SDK, which will let you interact with the game.
import hlt

# This library contains constant values.
from hlt import constants

# This library contains direction metadata to better interface with the game.
from hlt.positionals import Direction

# This library allows you to generate random numbers.
import random

# Logging allows you to save messages for yourself. This is required because the regular STDOUT
#   (print statements) are reserved for the engine-bot communication.
import logging

""" <<<Game Begin>>> """

# This game object contains the initial game state.
game = hlt.Game()
# At this point "game" variable is populated with initial map data.
# This is a good place to do computationally expensive start-up pre-processing.
# As soon as you call "ready" function below, the 2 second per turn timer will start.
ship_dict = {}
game.ready("MyPythonBot")

# Now that your bot is initialized, save a message to yourself in the log file with some important information.
#   Here, you log here your id, which you can always fetch from the game object by using my_id.
logging.info("Successfully created bot! My Player ID is {}.".format(game.my_id))

""" <<<Game Loop>>> """

while True:
    # This loop handles each turn of the game. The game object changes every turn, and you refresh that state by
    #   running update_frame().
    game.update_frame()
    # You extract player metadata and the updated map metadata here for convenience.
    me = game.me
    game_map = game.game_map

    # A command queue holds all the commands you will run this turn. You build this list up and submit it at the
    #   end of the turn.
    command_queue = []

    for ship in me.get_ships():

        logging.info(ship_dict)

        # If ship doesn't have a status, it must be new. Put it in the ship_dict
        if ship.id not in ship_dict:
            ship_dict[ship.id] = None

        # If ship's status is returning, keep going (unless on shipyard)
        if ship_dict[ship.id] == 'returning':

            # If ship isn't on shipyard, keep going home
            if ship.position != me.shipyard.position:
                command_queue.append(
                    ship.move(
                        game_map.naive_navigate(ship, me.shipyard.position)
                    )
                )
                break

            # If ship is on shipyard, switch to exploring mode 
            ship_dict[ship.id] = 'exploring'


        # If ship is full, return to shipyard

        if ship.halite_amount >+ constants.MAX_HALITE * .7:
            ship_dict[ship.id] = 'returning'

            command_queue.append(
                    ship.move(
                        game_map.naive_navigate(ship, me.shipyard.position)
                    )
                )
            break


        # If ship is on halite-rich cell, harvest it
        if game_map[ship.position].halite_amount > 25:
            command_queue.append(ship.stay_still())
            break

        # Explore for closest cell with a good amount of halite
        else:
            command_queue.append(
                ship.move(
                    random.choice([ Direction.North, Direction.South, Direction.East, Direction.West ])))

    # If the game is in the first 200 turns and you have enough halite, spawn a ship.
    # Don't spawn a ship if you currently have a ship at port, though - the ships will collide.
    if game.turn_number <= 200 and me.halite_amount >= constants.SHIP_COST and not game_map[me.shipyard].is_occupied:
        command_queue.append(me.shipyard.spawn())

    # Send your moves back to the game environment, ending this turn.
    game.end_turn(command_queue)

