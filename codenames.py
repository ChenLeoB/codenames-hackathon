import numpy as np
import json
from termcolor import colored, cprint
from player import Player, randomPlayer, Human
from word_reader import all_game_words
import argparse
import time
import importlib
import os

#TODO we can remove data_file

class Codenames:
    def __init__(self, players, mode, data_file, seed, output_file):
        self.mode = mode
        self.seed = seed
        self.output_file = output_file
        np.random.seed(self.seed)
        # All game words from word_reader.py
        self.all_game_words = all_game_words
        self.initiate_game()
        self.initiate_players(players)

    def initiate_game(self):
        # TODO: modify this so that we are just getting 25 random words from our word list from the txt
        # Randomly choose 25 words and assign to teams (9 -> red,8 -> blue,7 -> neutral,1 -> assassin)
        self.game_words = np.random.choice(self.all_game_words, 25, replace=False)
        self.guess_status = np.zeros(25)
        # TODO: is this dangerous? if player see this they can just always guess depending on the order
        self.word_team = [1] * 9 + [2] * 8 + [3] * 7 + [4]
        # Resuffle for random display
        self.display_order = np.random.choice(range(25), 25, replace=False)
        return None
    
    def initiate_players(self, players):
        # print(players)
        module = importlib.import_module('agents.' + players[0])
        team_a = getattr(module, players[1])

        # className = getattr(module, team_a_class)
        # todo remove word_base
        # self.ta_ms = team_a('a', 'spymaster', self.seed)
        # self.ta_gs = team_a('a', 'guesser', self.seed)
        self.ta_ms = team_a()
        self.ta_gs = team_a()


        module = importlib.import_module('agents.' + players[2])
        team_b = getattr(module, players[3])
        # self.tb_ms = team_b('b', 'spymaster', self.seed)
        # self.tb_gs = team_b('b', 'guesser', self.seed)
        self.tb_ms = team_b()
        self.tb_gs = team_b()
        return None
        
    def display_board(self, status_ref, team, turn):
        color = 'red' if team == 'A' else 'cyan'
        os.system('cls' if os.name in ('nt', 'dos') else 'clear')
        cprint("*" * 85, color)
        cprint("*" + " " * 35 + "TEAM {} TURN {}".format(team, turn) + " " * 35 + "*", color)
        cprint("*" * 85, color)
        color_ref = {0: 'yellow', 1: 'red', 2: 'cyan', 3: 'yellow', 4: 'magenta'}
        for i in range(5):
            for j in range(5):
                word = self.game_words[self.display_order[i*5+j]]
                color = color_ref[status_ref[self.display_order[i*5+j]]]
                if self.guess_status[self.display_order[i*5+j]] != 0:
                    cprint(word.center(17), color, 'on_{}'.format(color), end='')
                else:
                    cprint(word.center(17), color, end='')
            print("\n")
        return None
    
    def check_game_end(self, team, turn):
        other_team = {'A': 'B', 'B': 'A'}
        if 0 not in self.guess_status[:9]:
            self.display_board(self.guess_status, team, turn)
            print("GAME OVER IN {} TURNS! TEAM A wins this one by finding out all their words!".format(turn))
            return True
        if 0 not in self.guess_status[9:17]:
            self.display_board(self.guess_status, team, turn)
            print("GAME OVER IN {} TURNS! TEAM B wins this one by finding out all their words!".format(turn))
            return True
        if self.guess_status[-1] != 0:
            self.display_board(self.guess_status, team, turn)
            print("GAME OVER IN {} TURNS! TEAM {} wins this one as TEAM {} revealed the assassin word!".format(turn, other_team[team], team))
            return True
        return False

    # def record_statistics(self, turn, assassin):
    #     with open(self.output_file, 'a') as f:
    #         f.write(",".join([turn, assassin, self.word_base.get_data_file_name(), str(self.seed)]) + "\n")
    #     return None

    def get_turn_words(self, guess_words, words):
        temp = [word for word in words if word not in guess_words]
        return temp

    
    def play(self):
        turn = 1
        assassin = False
        self.guesses = []
        while True:
            # TEAM A GIVE HINT
            self.display_board(self.word_team, 'A', turn)
            time.sleep(4 * (self.mode=='interactive'))
            team_a_words = self.get_turn_words(self.guesses, self.game_words[:9])
            team_b_words = self.get_turn_words(self.guesses, self.game_words[9:17])
            neutral_words = self.get_turn_words(self.guesses, self.game_words[17:24])
            assasin_word = self.get_turn_words(self.guesses, self.game_words[24])
            word, count = self.ta_ms.give_hint('A', 'B', self.game_words, self.guess_status, team_a_words, team_b_words, neutral_words, assasin_word)
            
            # TEAM A GUESS
            self.display_board(self.guess_status, 'A', turn)
            print("TEAM A Spymaster: My hint is {}: {}".format(word, count))
            words_not_guessed = self.game_words[np.where(self.guess_status == 0)]
            getGuessA = self.ta_gs.make_guess(word, count, words_not_guessed, self.guess_status)
            guess = getGuessA
            for word in guess:
                time.sleep(2 * (self.mode=='interactive'))
                print("TEAM A Guesser: I guess \"{}\" is our word".format(word))
                idx_in_game_words = np.argwhere(self.game_words == word)
                time.sleep(1.5 * (self.mode=='interactive'))
                if idx_in_game_words < 9:
                    print("TEAM A Spymaster: That is correct!")
                    self.guess_status[idx_in_game_words] = 1
                elif idx_in_game_words < 17:
                    print("TEAM A Spymaster: That is incorrect... It is the opponents' word...")
                    self.guess_status[idx_in_game_words] = 2
                    break
                elif idx_in_game_words < 24:
                    print("TEAM A Spymaster: That is incorrect... It is a neutral word...")
                    self.guess_status[idx_in_game_words] = 3
                    break
                else:
                    print("TEAM A Spymaster: That is incorrect... It is the assassin word...")
                    self.guess_status[idx_in_game_words] = 4
                    assassin = True
                    break

            self.guesses += getGuessA
            
            # TEAM A FINISH
            if self.check_game_end('A', turn):
                break
            print("END OF TURN")
            time.sleep(2 * (self.mode=='interactive'))

            # TEAM B GIVE HINT
            self.display_board(self.word_team, 'B', turn)
            time.sleep(4 * (self.mode=='interactive'))

            team_a_words = self.get_turn_words(self.guesses, self.game_words[:9])
            team_b_words = self.get_turn_words(self.guesses, self.game_words[9:17])
            neutral_words = self.get_turn_words(self.guesses, self.game_words[17:24])
            assasin_word = self.get_turn_words(self.guesses, self.game_words[24])

            word, count = self.tb_ms.give_hint('B', 'A', self.game_words, self.guess_status, team_b_words, team_a_words, neutral_words, assasin_word)
            
            # TEAM B GUESS
            self.display_board(self.guess_status, 'B', turn)
            print("TEAM B Spymaster: My hint is {}: {}".format(word, count))
            words_not_guessed = self.game_words[np.where(self.guess_status == 0)]
            getGuessB = self.tb_gs.make_guess(word, count, words_not_guessed, self.guess_status)
            guess = getGuessB
            for word in guess:
                time.sleep(2 * (self.mode=='interactive'))
                print("TEAM B Guesser: I guess \"{}\" is our word".format(word))
                idx_in_game_words = np.argwhere(self.game_words == word)
                time.sleep(1.5 * (self.mode=='interactive'))
                if idx_in_game_words < 9:
                    print("TEAM B Spymaster: That is incorrect... It is the opponents' word...")
                    self.guess_status[idx_in_game_words] = 1
                    break
                elif idx_in_game_words < 17:
                    print("TEAM B Spymaster: That is correct!")
                    self.guess_status[idx_in_game_words] = 2
                elif idx_in_game_words < 24:
                    print("TEAM B Spymaster: That is incorrect... It is a neutral word...")
                    self.guess_status[idx_in_game_words] = 3
                    break
                else:
                    print("TEAM B Spymaster: That is incorrect... It is the assassin word...")
                    self.guess_status[idx_in_game_words] = 4
                    assassin = True
                    break
            # TEAM B FINISH
            if self.check_game_end('B', turn):
                break
            print("END OF TURN")
            time.sleep(2 * (self.mode=='interactive'))

            turn += 1

            self.guesses += getGuessB
        
        # Wrap up and Recording
        print("For reproducibility, the random seed used in this game is {}.".format(self.seed))
        # if self.output_file != None:
        #     self.record_statistics(str(turn), str(assassin))

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-p', '--players', type=str, nargs='+', help='list of player types [1. Human / 2. AI]')
    parser.add_argument('-m', '--mode', type=str, default='interactive', help='mode of the game (interactive / testing)')
    parser.add_argument('-d', '--data_file', type=int, default=1, help='dataset used by AI in the game (1. cosine_wiki_30k / 2. wup_wiki_30k)')
    parser.add_argument('-s', '--seed', type=int, default=np.random.randint(2**31 - 1), help='random seed used in this game (0 - 2^31-1)')
    parser.add_argument('-o', '--output_file', type=str, default=None, help='the file to record statistics')
    opt = parser.parse_args()

    game = Codenames(
        opt.players,
        opt.mode,
        opt.data_file,
        opt.seed,
        opt.output_file
    )

    game.play()