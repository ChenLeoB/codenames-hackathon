import os
import numpy as np

print(" "*20 + "--- CODENAMES GAME WITH AI ---")
print("Please follow the instructions below to type in the settings for your game...")


team_a_file = str(input("Enter the name of your file for Team A: "))
team_a_class = str(input("Enter the name of your class for Team A: "))

team_b_file = str(input("Enter the name of your file for Team B: "))
team_b_class = str(input("Enter the name of your class for Team B: "))

players = " ".join([team_a_file, team_a_class, team_b_file, team_b_class])

mode = input("Please set the mode for this game. Press enter to skip [interactive / testing/ batch]: ")
mode = mode if mode != "" else 'interactive'

# data_file = input("Choose the data file for this game. If no preference, press enter to skip [1. GloVe / 2. Word2Vec 3./ WordNet]: ")
# data_file = int(data_file) if data_file != "" else 1
data_file = 1

seed = input("Please enter the random seed for this game. If no preference, press enter to skip: ")
seed = int(seed) if seed!="" else np.random.randint(2**31 - 1)

number_batch = 0
if mode == 'batch':
    number_batch = input("Please enter the number of games you want to play. If no preference, press enter to skip: ")
    number_batch = int(number_batch) if number_batch!="" else 100    

cmd = 'python codenames.py -p {} -m {} -d {} -s {} -n {}'.format(players, mode, data_file, seed, number_batch)
os.system(cmd)
