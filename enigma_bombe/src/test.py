from enigma import EnigmaMachine, ALPHABET, N_LETTERS
from bombe import BombeMachine

# -----------
# FILENAMES
# -----------
ex_path = "../data/"
ex_config_enigma = "test_config_enigma.txt"
ex_text_filename = "test_text.txt"

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
ciphered_text = ""
for i, letter in enumerate(text):
    enigma_machine.step_rotors()
    panel = ""
    for rotor_name in enigma_machine.rotor_names:
        rotor = enigma_machine.rotors[rotor_name]
        display = (rotor.position + rotor.ring_setting) % N_LETTERS
        panel += "{}({}) ".format(ALPHABET[display], display)
    print(panel)
    ciphered_text += enigma_machine.cipher_letter_bombe(letter)
print("\nCIPHERED TEXT:")
print(ciphered_text + "\n")
