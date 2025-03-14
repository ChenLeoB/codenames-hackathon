import numpy as np
from wordBase import WordBase, Word
import time
import enchant
import re


class Player:

    def __init__(self, team, role, seed):
        #delete this line because it...
        self.role = role
        self.team = team
        self.seed = seed
    
    def give_hint(self, game_words, guess_status, team_words, opponent_words, neutral_words, assassin_word):
        return
    
    def make_guess(self, hint, number, game_words, guess_status):
        return

    def validate_hint(self, word, count, game_words):
        d = enchant.Dict("en_US")

        #checks if hint is a valid word
        if not d.check(word):
            message = "Please check that your hint is a valid word and attempt again."
            print(message)
            time.sleep(1)
            return False, message
        
        for game_word in game_words:
            # if clue word contains a board word, return False
            lowercase_word = word.lower()
            if lowercase_word.find(game_word.lower()) != -1:
                message = "Please check that your hint does not contain a word on the board and attempt again."
                print(message)
                return False, message
            
        if count <=0:
            message = "Invalid Count! :{count}\nPlease try again."
            print(message)
            time.sleep(1)
            return False, message
        return True, "Valid Hint"
    
    def validate_guess(self, guesses, number, game_words, guess_status):
        if len(guesses) > int(number) + 1:
            message = "The maximum number of guesses allowed is {}, please try again.".format(int(number) + 1)
            print(message)
            time.sleep(1)
            return False, message
        else:
            for word in guesses:
                if word.upper() not in game_words:
                    message = "Sorry, the word \"{}\" you just inputted is not on the board, please try again.".format(word)
                    print(message)
                    time.sleep(1)
                    return False, message
                # if guess_status[np.argwhere(game_words == word.upper())[0]] != 0:
                #     message = "Sorry, the word \"{}\" you just inputted has already been guessed, please try again.".format(word)
                #     print(message)
                #     time.sleep(1)
                #     return False, message
        return True, "Valid Guess"


class randomPlayer():
    def __init__(self, name):
        self.name = name
    
    def give_hint(self, game_words, guess_status, team_words, opponent_words, neutral_words, assassin_word):
        return "woof", 1
    
    def make_guess(self, hint, number, game_words, guess_status):
        # make random valid guesses
        number_of_guesses = number + 1
        words_not_guessed = game_words[np.where(guess_status == 0)]
        guesses = np.random.choice(words_not_guessed, number_of_guesses, replace=False)
        return guesses
    
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