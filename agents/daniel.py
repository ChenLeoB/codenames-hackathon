from player import Player
import numpy as np

class Daniel(Player):
    def give_hint(self, game_words, guess_status, team_words, opponent_words, neutral_words, assassin_word):
        #TODO: validation would be one word and not directly in the game words
        #TODO: just queries LLM
        word, count = "", 0
        while True:
            # Create hint and count here
            word, count = "woof", 1

            # Continuously loops until valid hint and count are given
            if self.validate_hint(word, count, game_words):
                break
        return word, count

    def make_guess(self, hint, number, words, guess_status):
        #TODO: validation needs to be a word from the board
        #TODO: just queries LLM
        # make random valid guesses
        guesses = []
        while True:
            # Code for guessing goes here

            number_of_guesses = number + 1
            guesses = np.random.choice(words, number_of_guesses, replace=False)

            # While loop continues until valid guesses are given
            if self.validate_guess(guesses, number, words, guess_status):
                break
        return guesses