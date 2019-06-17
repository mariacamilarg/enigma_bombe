#!/usr/bin/env python
# -*- coding: utf-8 -*-

from collections import defaultdict

ALPHABET = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
N_LETTERS = 26

class EnigmaMachine:

    def __init__(self, config_filename):
        """
        Initial configuration of the machine.
        """

        # load data
        self.load_data()

        # read config file
        self.load_config_file(config_filename)


    def load_data(self):

        data_path = "../data/"
        rotors_filename = "rotors.txt"
        reflectors_filename = "reflectors.txt"

        # rotors
        self.rotors_data = defaultdict()
        with open(data_path+rotors_filename) as file: 
            lines = file.read().splitlines()

            for line in lines: 
                rotor_name, rotor_letters, rotor_turnovers = line.split(",")
                self.rotors_data[rotor_name] = rotor_letters

        # reflectors
        self.reflectors_data = defaultdict()
        with open(data_path+reflectors_filename) as file: 
            lines = file.read().splitlines()

            for line in lines: 
                reflector_name, reflector_letters = line.split(",")
                
                reflector_dict = defaultdict()
                for letter, letter_reflection in zip(ALPHABET, reflector_letters):
                    reflector_dict[letter] = letter_reflection

                self.reflectors_data[reflector_name] = reflector_dict


    def load_config_file(self, config_filename):

        with open(config_filename) as file: 
            lines = file.read().splitlines()

            # rotors
            self.n_rotors = int(lines[0])
            self.rotor_names = lines[1].split(" ")

            ring_settings = list(map(int, lines[2].split(" ")))
            self.rotor_ring_settings = defaultdict()
            for rotor_name, ring_setting in zip(self.rotor_names, ring_settings):
                self.rotor_ring_settings[rotor_name] = ring_setting

            offsets = list(map(int, lines[3].split(" ")))
            self.rotor_offsets = defaultdict()
            for rotor_name, offset in zip(self.rotor_names, offsets):
                self.rotor_offsets[rotor_name] = offset
            
            self.rotors = defaultdict()
            for rotor_name in self.rotor_names:
                if rotor_name in self.rotors_data: 
                    self.rotors[rotor_name] = self.rotors_data[rotor_name]
                else:
                    print("ERROR: There is no rotor with the name: {}".format(rotor_name))
                    exit()

            self.rotor_turns = defaultdict()
            for rotor_name in self.rotor_names:
                self.rotor_turns[rotor_name] = 0

            # plugboard
            self.n_plugboard_pairs = int(lines[4])
            plugboard_pairs = lines[5].split(" ")
            self.plugboard = defaultdict()
            for pair in plugboard_pairs: 
                l1, l2 = pair[0], pair[1]
                self.plugboard[l1] = l2
                self.plugboard[l2] = l1

            # reflector
            self.reflector_name = lines[6]
            if self.reflector_name in self.reflectors_data: 
                self.reflector = self.reflectors_data[self.reflector_name]
            else:
                print("ERROR: There is no reflector with the name: {}".format(self.reflector_name))
                exit()


    def step_rotors(self):
        # the right rotor (last one in list) always rotates,
        # from there others rotate like a clock works
        # i.e. turn when the one to their right makes a full turn

        rotor_names_inverted = self.rotor_names[::-1]

        # most-right rotor
        right_rotor_name = rotor_names_inverted[0]
        self.rotor_turns[right_rotor_name] = self.rotor_turns[right_rotor_name] + 1
        self.rotor_offsets[right_rotor_name] = (self.rotor_offsets[right_rotor_name] + 1) % N_LETTERS

        for rotor_name in rotor_names_inverted[1:]:

            if self.rotor_turns[right_rotor_name] % N_LETTERS == 0: 
                # it has given a full turn, so the curent rotor has to turn
                self.rotor_turns[rotor_name] = self.rotor_turns[rotor_name] + 1
                self.rotor_offsets[rotor_name] = (self.rotor_offsets[rotor_name] + 1) % N_LETTERS
            else:
                break

            right_rotor_name = rotor_name
            

    def cipher_letter(self, letter):

        # advance rotors
        self.step_rotors()
        
        # ciphered letter
        ciphered_letter = ""
        
        # enter plugboard switch
        plugboard_letter = self.plugboard.get(letter, letter)

        # enter rotors (inverted order)
        rotor_names_inverted = self.rotor_names[::-1]
        rotor_letter = plugboard_letter

        for rotor_name in rotor_names_inverted:
            # position in alphabet
            position_in = ALPHABET.find(rotor_letter)

            rotor_letters = self.rotors[rotor_name]
            rotor_offset = self.rotor_offsets[rotor_name]

            # pposition in the rotor
            position_out = (position_in + rotor_offset) % N_LETTERS
            
            rotor_letter = rotor_letters[position_out]

        # enter reflector 
        reflector_letter = self.reflector[rotor_letter]

        # enter rotors (normal order)
        rotor_letter = reflector_letter

        for rotor_name in self.rotor_names:
            # position in alphabet
            position_in = ALPHABET.find(rotor_letter)

            rotor_letters = self.rotors[rotor_name]
            rotor_offset = self.rotor_offsets[rotor_name]

            # pposition in the rotor
            position_out = (position_in + rotor_offset) % N_LETTERS
            
            rotor_letter = rotor_letters[position_out]

        # enter plugboard switch
        plugboard_letter = self.plugboard.get(rotor_letter, rotor_letter)

        # calculate ciphered letter
        ciphered_letter = plugboard_letter

        return ciphered_letter

    def cipher_text(self, text):

        ciphered_text = ""

        for letter in text:
            ciphered_letter = self.cipher_letter(letter)
            ciphered_text += ciphered_letter

        return ciphered_text
    

    