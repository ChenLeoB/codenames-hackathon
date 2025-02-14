import os
import numpy as np

print(" "*20 + "--- CODENAMES GAME WITH AI ---")
print("Please follow the instructions below to type in the settings for your game...")


team_a_file = str(input("Enter the name of your file: "))
team_a_class = str(input("Enter the name of your class: "))

team_b_file = str(input("Enter the name of your file: "))
team_b_class = str(input("Enter the name of your class: "))

players = " ".join([team_a_file, team_a_class, team_b_file, team_b_class])

mode = input("Please set the mode for this game. Press enter to skip [interactive / testing]: ")
mode = mode if mode != "" else 'interactive'

data_file = input("Choose the data file for this game. If no preference, press enter to skip [1. GloVe / 2. Word2Vec 3./ WordNet]: ")
data_file = int(data_file) if data_file != "" else 1

seed = input("Please enter the random seed for this game. If no preference, press enter to skip: ")
seed = int(seed) if seed!="" else np.random.randint(2**31 - 1)

cmd = 'python codenames.py -p {} -m {} -d {} -s {}'.format(players, mode, data_file, seed)
os.system(cmd)
