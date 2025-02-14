from player import Player
import numpy as np

class Daniel(Player):
    def give_hint(self, game_words, guess_status, team_words, opponent_words, neutral_words, assassin_word):
        #TODO: validation would be one word and not directly in the game words
        #TODO: just queries LLM
        return "woof", 1

    def make_guess(self, hint, number, words, guess_status):
        #TODO: validation needs to be a word from the board
        #TODO: just queries LLM
        # make random valid guesses
        number_of_guesses = number + 1
        guesses = np.random.choice(words, number_of_guesses, replace=False)
        return guesses