from enigma import EnigmaMachine
from bombe import BombeMachine

# -----------
# FILENAMES
# -----------
ex_path = "../data/"
ex_config_enigma = "example_config_enigma.txt"
ex_config_bombe = "example_config_bombe.txt"
ex_text = "example_text.txt"
ex_text_ciphered = "example_text_ciphered.txt"
ex_plugboards = "example_plugboards.txt"

# -----------
# ENIGMA
# -----------
print("-----------")
print("ENIGMA")
print("-----------")

# creating machine
enigma_machine = EnigmaMachine()
enigma_machine.load_config_file(ex_path+ex_config_enigma)

# text to cipher
text = ""
with open(ex_path+ex_text, 'r') as file: 
    text = file.read().splitlines()[0]
print("Clear text:")
print(text + "\n")

# cipher it
ciphered_text = enigma_machine.cipher_text(text, print_display=False)
with open(ex_path+ex_text_ciphered, 'w') as file: 
    file.write(ciphered_text)
print("Ciphered Text:")
print(ciphered_text + "\n")

# -----------
# BOMBE
# -----------
print("-----------")
print("BOMBE")
print("-----------")

bombe_machine = BombeMachine(ex_path+ex_config_bombe)
possible_plugboards = bombe_machine.run()
n_possible_plugboards = len(possible_plugboards.keys()) #624

with open(ex_path+ex_plugboards, 'w') as file: 
    str_write = "Different possible plugboards: " + str(n_possible_plugboards)
    file.write(str_write) 

    for frozen_plugboard in possible_plugboards:
        str_write = "\n" + str(frozen_plugboard)
        file.write(str_write)

        rotor_positions = possible_plugboards[frozen_plugboard]
        for rp in rotor_positions:
            str_write = "\n- " + str(rp)
            file.write(str_write)
    
print("Bombe finished and it output the possible plugboards to the file: ", ex_path+ex_plugboards)