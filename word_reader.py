import os

#TODO: make it so that we are just reading from a txt file and then we can add it into a list here

#read from words.txt (same directory as this file) and store in list
words = []
with open('words.txt', 'r') as f:
    for line in f:
        words.append(line.strip())
