from machine import EnigmaMachine

# example filenames
ex_path = "../data/"
ex_config_filename = "example_config.txt"
ex_text_filename = "example_text.txt"

# creating machine
enigma_machine = EnigmaMachine(ex_path+ex_config_filename)

print(enigma_machine.rotor_offsets)

# text to cipher
text = ""
with open(ex_path+ex_text_filename) as file: 
    text = file.read()
print(text)

# cipher it
ciphered_text = enigma_machine.cipher_text(text)
print(ciphered_text)