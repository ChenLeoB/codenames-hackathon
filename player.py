import numpy as np
from wordBase import WordBase, Word
import time
import re


class Player:

    def __init__(self, player_type, teammate_type, word_base, game_words, guess_status, team, role, seed):
        self.game_words = game_words
        self.guess_status = guess_status
        self.role = role
        # Assign word belongings
        if team == 'a':
            self.team_words = game_words[:9]
            self.opponent_words = game_words[9:17]
        else:
            self.team_words = game_words[9:17]
            self.opponent_words = game_words[:9]
        self.neutral_words = game_words[17:24]
        self.assassin_word =  game_words[24]
        # Initiate Player instances
        if player_type == 'ai':
            self.player = AI(teammate_type, word_base, seed)
        else:
            self.player = Human(word_base)
    
    def give_hint(self):
        return self.player.give_hint(
            self.game_words,
            self.guess_status,
            self.team_words,
            self.opponent_words,
            self.neutral_words,
            self.assassin_word
        )
    
    def make_guess(self, hint, number):
        return self.player.make_guess(hint, number, self.game_words, self.guess_status)
    
class BasicLLM():
    def __init__(self, word_base):
        #TODO: no need this 
        self.word_base = word_base
    
    def give_hint(self, game_words, guess_status, team_words, opponent_words, neutral_words, assassin_word):
        #TODO: validation would be one word and not directly in the game words
        #TODO: just queries LLM
    
    def make_guess(self, hint, number, game_words, guess_status):
        #TODO: validation needs to be a word from the board
        #TODO: just queries LLM
        

class Human():
    def __init__(self, word_base):
        self.word_base = word_base
    
    def give_hint(self, game_words, guess_status, team_words, opponent_words, neutral_words, assassin_word):
        while True:
            user_input = input("It\'s your turn to give a hint. Please type in the word and number of your hint, separated by a single space: ")
            if len(re.findall('^[A-Za-z]+ [0-9]$', user_input)) == 0:
                print("Please check the format of your input and attempt again.")
                continue
            word, count = user_input.split()
            if word not in self.word_base.get_dictionary_words():
                print("Sorry, the word \"{}\" you just inputed is not in our current word base, please try another word.".format(word))
                time.sleep(1)
            else:
                break
        word_obj = self.word_base.get_dictionary_words()[np.where([x==word for x in self.word_base.get_dictionary_words()])[0][0]]
        return word_obj, int(count)
    
    def make_guess(self, hint, number, game_words, guess_status):
        while True:
            guesses = input("Please type in your guesses in order separated by a single space. The maximum number of guesses allowed is {}: ".format(number + 1))
            guesses = guesses.split()
            valid_input = True
            if len(guesses) > number + 1:
                print("The maximum number of guesses allowed is {}, please try again.".format(number + 1))
            else:
                for word in guesses:
                    if word not in game_words or guess_status[np.argwhere(game_words == word)[0]] != 0:
                        print("Sorry, the word \"{}\" you just inputted is not on the board, please try again.".format(word))
                        valid_input = False
                if valid_input == True:
                    break
        return guesses
    
