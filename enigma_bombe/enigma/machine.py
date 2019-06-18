#!/usr/bin/env python
# -*- coding: utf-8 -*-

from collections import defaultdict

ALPHABET = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
N_LETTERS = 26

class Reflector:

    def __init__(self, name, letters):
        """
        Initial configuration of the reflector's data.
        """

        # name
        self.name = name

        # letters
        self.reflections = defaultdict()
        for pin_in, output_letter in enumerate(letters):
            pin_out = ALPHABET.index(output_letter)
            self.reflections[pin_in] = pin_out

    def reflect(self, pin_in):
        pin_out = self.reflections[pin_in]
        return pin_out

class Rotor:

    def __init__(self, name, letters, turnovers):
        """
        Initial configuration of the rotor's data.
        """

        # name
        self.name = name

        # letters
        self.wiring = defaultdict()
        self.wiring_inverse = defaultdict()
        for pin_in, output_letter in enumerate(letters):
            pin_out = ALPHABET.index(output_letter)
            self.wiring[pin_in] = pin_out
            self.wiring_inverse[pin_out] = pin_in

        # turnovers
        self.turnovers = []
        for turn in turnovers:
            pin_turn = ALPHABET.index(turn)
            self.turnovers.append(pin_turn)

    def load_config(self, ring_setting_letter, offset_letter):

        self.ring_setting = ALPHABET.index(ring_setting_letter) 
        self.position = ALPHABET.index(offset_letter)

        # correct for ring setting (position and turnovers)
        self.position = (self.position - self.ring_setting) % N_LETTERS

        for i, turnover in enumerate(self.turnovers):
            new_turnover = (turnover - self.ring_setting) % 26
            self.turnovers[i] = new_turnover


    def step(self, turnover=False):
        """
        Returns true if the rotor to its left has to turnover.

        turnover = signal if this rotor turns
        """
        turn_left = False

        if turnover:
            self.position = ( self.position + 1 ) % N_LETTERS
            if self.position in self.turnovers:
                turn_left = True

        return turn_left

    def process_inwards(self, std_in):
        """
        Receives input signal and returns output pin (right to left)
        """
        pin_in = (std_in + self.position) % N_LETTERS
        
        pin_out = self.wiring[pin_in]
        pin_out = (pin_out - self.position) % N_LETTERS

        return pin_out

    def process_outwards(self, std_out):
        """
        Receives output signal and returns input pin (left to right)
        """
        pin_out = (std_out + self.position) % N_LETTERS
        
        pin_in = self.wiring_inverse[pin_out]
        pin_in = (pin_in - self.position) % N_LETTERS

        return pin_in


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
                rotor = Rotor(rotor_name, rotor_letters, rotor_turnovers)
                self.rotors_data[rotor_name] = rotor

        # reflectors
        self.reflectors_data = defaultdict()
        with open(data_path+reflectors_filename) as file: 
            lines = file.read().splitlines()

            for line in lines: 
                reflector_name, reflector_letters = line.split(",")
                reflector = Reflector(reflector_name, reflector_letters)
                self.reflectors_data[reflector_name] = reflector


    def load_config_file(self, config_filename):

        with open(config_filename) as file: 
            lines = file.read().splitlines()

            # rotors
            self.n_rotors = int(lines[0])
            self.rotor_names = lines[1].split(" ")

            rotor_ring_settings = lines[2].split(" ")
            rotor_offsets = lines[3].split(" ")

            self.rotors = defaultdict()
            for i, rotor_name in enumerate(self.rotor_names):
                if rotor_name not in self.rotors_data: 
                    print("ERROR: There is no rotor with the name: {}".format(rotor_name))
                    exit()
                else: 
                    rotor = self.rotors_data[rotor_name]
                    rotor.load_config(rotor_ring_settings[i], rotor_offsets[i])
                    self.rotors[rotor_name] = rotor

            # plugboard
            self.n_plugboard_pairs = int(lines[4])
            self.plugboard = defaultdict()
            if self.n_plugboard_pairs > 0: 
                plugboard_pairs = lines[5].split(" ")
                for pair in plugboard_pairs: 
                    l1, l2 = pair[0], pair[1]
                    self.plugboard[l1] = l2
                    self.plugboard[l2] = l1

            # reflector
            self.reflector_name = lines[6]
            if self.reflector_name not in self.reflectors_data: 
                print("ERROR: There is no reflector with the name: {}".format(self.reflector_name))
                exit()
            else: 
                self.reflector = self.reflectors_data[self.reflector_name]


    def step_rotors(self):
        # the right rotor (last one in list) always rotates,
        # from there others rotate like a clock works
        # i.e. turn when the rotor to the right passes 
        #      through its turnover letter

        rotor_names_inverted = self.rotor_names[::-1]
        rotor_positions = []

        # most-right rotor
        right_rotor_name = rotor_names_inverted[0]
        right_rotor = self.rotors[right_rotor_name]
        turn_signal = right_rotor.step(turnover=True)
        rotor_positions.append(right_rotor.position)

        # the rest
        for rotor_name in rotor_names_inverted[1:]:
            rotor = self.rotors[rotor_name]
            turn_signal = rotor.step(turnover=turn_signal)
            rotor_positions.append(rotor.position)

        # update status
        self.rotor_positions = rotor_positions[::-1]


    def cipher_letter(self, letter):

        # advance rotors
        self.step_rotors()
        
        # ciphered letter
        ciphered_letter = ""
        
        # enter plugboard switch
        plugboard_letter = self.plugboard.get(letter, letter)

        # enter rotors (inwards - right to left)
        rotor_names_inverted = self.rotor_names[::-1]
        pin_in = ALPHABET.index(plugboard_letter)

        for rotor_name in rotor_names_inverted:
            rotor = self.rotors[rotor_name]
            pin_in = rotor.process_inwards(pin_in)

        # enter reflector
        pin_out = self.reflector.reflect(pin_in)

        # enter rotors (outwards - left to right)
        for rotor_name in self.rotor_names:
            rotor = self.rotors[rotor_name]
            pin_out = rotor.process_outwards(pin_out)

        # enter plugboard switch
        rotor_letter = ALPHABET[pin_out]
        plugboard_letter = self.plugboard.get(rotor_letter, rotor_letter)

        # calculate ciphered letter
        ciphered_letter = plugboard_letter
        
        return ciphered_letter

    def cipher_text(self, text):

        ciphered_text = ""

        for letter in text:
            ciphered_letter = self.cipher_letter(letter)
            ciphered_text += ciphered_letter

            print("ROTOR PANEL: \t", self.rotor_positions)
            print("CIPHER: \t {} -> {}\n".format(letter, ciphered_letter))

        return ciphered_text
    