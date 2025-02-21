from player import Player
import numpy as np

class noobBot(Player):
    def __init__(self):
        pass

    def give_hint(self, your_team, opponent_team, game_words, guess_status, team_words, opponent_words, neutral_words, assassin_word, experience):
       return "woof", int(1)

    def make_guess(self, hint, number, words, guess_status, experience):
        # make random valid guesses
        print("Hint: ", hint)
        print("Number: ", number)
        print("Words: ", words)
        print("Guess Status: ", guess_status)
        number_of_guesses = number + 1
        guesses = np.random.choice(words, number_of_guesses, replace=False)
        # convert into list
        guesses = guesses.tolist()
        return guesses