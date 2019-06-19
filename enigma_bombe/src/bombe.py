#!/usr/bin/env python
# -*- coding: utf-8 -*-

from collections import defaultdict
from itertools import product
from enigma import EnigmaMachine, ALPHABET, N_LETTERS

class BombeMachine:

    def __init__(self, config_filename):
        """
        Initial configuration of the machine.
        """

        # load config file
        self.load_config_file(config_filename)

        # create menu
        self.create_menu()


    def load_config_file(self, config_filename):

        with open(config_filename) as file: 
            lines = file.read().splitlines()

            # crib
            self.crib_cipher = lines[0]
            self.crib_plain = lines[1]

            # menu paths
            self.n_paths = int(lines[2])
            self.paths = lines[3].split(" ")
            self.paths_input = lines[3][0]

            # rotors
            self.rotor_names = lines[4].split(" ")
            self.n_rotors = len(self.rotor_names)
            self.rotor_ring_settings = lines[5].split(" ")
            self.reflector_name = lines[6]
            

    def create_menu(self):

        # model graph like: https://www.python.org/doc/essays/graphs/
        self.menu = defaultdict()

        for i, letter_cipher in enumerate(self.crib_cipher):
            
            letter_plain = self.crib_plain[i]

            # letter cipher -> letter plain
            if letter_cipher not in self.menu:
                links_dict = defaultdict()
                links_dict[letter_plain] = [i]
                self.menu[letter_cipher] = links_dict
            else: 
                links_dict = self.menu[letter_cipher]
                if letter_plain not in links_dict:
                    links_dict[letter_plain] = [i]
                else:
                    links_list = links_dict[letter_plain]
                    links_list.append(i)
                    links_dict[letter_plain] = links_list
                    
                self.menu[letter_cipher] = links_dict

            # letter plain -> letter 
            if letter_plain not in self.menu:
                links_dict = defaultdict()
                links_dict[letter_cipher] = [i]
                self.menu[letter_plain] = links_dict
            else: 
                links_dict = self.menu[letter_plain]
                if letter_cipher not in links_dict:
                    links_dict[letter_cipher] = [i]
                else:
                    links_list = links_dict[letter_cipher]
                    links_list.append(i)
                    links_dict[letter_cipher] = links_list
                    
                self.menu[letter_plain] = links_dict


    def add_contradiction(self, letter, letter_cipher):
        if letter not in self.contradictions:
            self.contradictions[letter] = set([letter_cipher])
        else: 
            plug_contradictions = self.contradictions[letter]
            plug_contradictions.add(letter_cipher)
            self.contradictions[letter] = plug_contradictions

        if letter_cipher not in self.contradictions:
            self.contradictions[letter_cipher] = set([letter])
        else: 
            plug_contradictions = self.contradictions[letter_cipher]
            plug_contradictions.add(letter)
            self.contradictions[letter_cipher] = plug_contradictions


    def run(self):

        # loop through all combinations of rotors
        rotor_positions_combinations = [''.join(i) for i in product(ALPHABET, repeat = 3)]

        # viable plugboard connections for each rotor combination
        self.possibilities = defaultdict()

        # initialize empty enigma machine
        enigma = EnigmaMachine()

        for rotor_positions in rotor_positions_combinations:

            print("ROTOR POSITIONS: ", rotor_positions)

            # impossible plugboard connections
            self.contradictions = defaultdict()

            # start making first plugboard guess
            for guess in ALPHABET:
                plugboard = defaultdict()
                plugboard[self.paths_input] = guess
                plugboard[guess] = self.paths_input
                plugboard_possible = True

                #print("Guess: P({})={}".format(self.paths_input, guess))

                # go through paths to check guess
                for path in self.paths:
                    #print("Path: ", path)
                    for i in range( len(path) - 1 ): 

                        letter = path[i]
                        letter_connections = self.menu[letter]

                        letter_cipher = path[i+1]
                        letter_cipher_positions = letter_connections[letter_cipher] 

                        cipher_offset = letter_cipher_positions[0]
                        #TODO check when there is more than 1 connection

                        # load enigma config
                        enigma.load_config_bombe(self.n_rotors, self.rotor_names,
                                                self.rotor_ring_settings, rotor_positions, self.reflector_name)

                        # P(letter_cipher) = S_pos( P(letter) ) 
                        plug_letter = plugboard[letter]
                        plug_letter_cipher = enigma.cipher_letter_bombe(plug_letter, cipher_offset)

                        '''
                        print("{} = P( S_{}( P({}) ) )".format(letter_cipher, cipher_offset, letter))
                        print("P({}) = S_{}( P({}) ) = S_{}( {} )".format(letter_cipher, cipher_offset, letter, cipher_offset, plug_letter))
                        print("=> P({}) = {}".format(letter_cipher, plug_letter_cipher))
                        print("--")
                        '''

                        if letter_cipher in self.contradictions:

                            plug_contradictions = self.contradictions[letter_cipher]

                            if plug_letter_cipher in plug_contradictions:
                                
                                # merge with contradictions dictionary
                                for plug in plugboard:
                                    plug_cipher = plugboard[plug]
                                    self.add_contradiction(plug, plug_cipher)

                                # not worth keep checking on an inconsistency
                                plugboard_possible = False
                                #print("Contradiction found! Moving to next guess\n")
                                break
                        
                        if letter_cipher in plugboard:

                            # merge with contradictions dictionary
                            self.add_contradiction(letter_cipher, plug_letter_cipher)
                            for plug in plugboard:
                                plug_cipher = plugboard[plug]
                                self.add_contradiction(plug, plug_cipher)

                            # not worth keep checking on an inconsistency
                            plugboard_possible = False
                            #print("Inconsistency found! Moving to next guess\n")
                            break
                        else: 
                            plugboard[letter_cipher] = plug_letter_cipher
                            plugboard[plug_letter_cipher] = letter_cipher

                    # TODO for now I only check 1 path

                # Check if it found a good candidate and add it to the list
                if plugboard_possible:
                    print("Possible plugboard:")
                    print(plugboard)
                    if rotor_positions not in self.possibilities:
                        self.possibilities[rotor_positions] = [plugboard]
                    else:
                        self.possibilities[rotor_positions].append(plugboard)

