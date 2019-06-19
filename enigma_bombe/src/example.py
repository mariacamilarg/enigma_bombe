from enigma import EnigmaMachine
from bombe import BombeMachine

# -----------
# FILENAMES
# -----------
ex_path = "../data/"
ex_config_enigma = "example_config_enigma.txt"
ex_config_bombe = "example_config_bombe.txt"
ex_text_filename = "example_text.txt"

# -----------
# ENIGMA
# -----------

# creating machine
enigma_machine = EnigmaMachine()
enigma_machine.load_config_file(ex_path+ex_config_enigma)

# text to cipher
text = ""
with open(ex_path+ex_text_filename) as file: 
    text = file.read().splitlines()[0]
print("CLEAR TEXT:")
print(text + "\n")

# cipher it
ciphered_text = enigma_machine.cipher_text(text, print_display=False)
print("CIPHERED TEXT:")
print(ciphered_text + "\n")

# -----------
# BOMBE
# -----------
bombe_machine = BombeMachine(ex_path+ex_config_bombe)
bombe_machine.run()
