import numpy as np
import json
from termcolor import colored, cprint
from player import Player, randomPlayer, Human
from word_reader import all_game_words
import argparse
import time
import importlib
import os
import datetime


class Codenames:
    def __init__(self, players, mode, seed, output_file):
        print("Starting a new game of Codenames on seed {}...".format(seed))
        self.mode = mode
        self.seed = seed
        self.output_file = output_file
        np.random.seed(self.seed)
        # All game words from word_reader.py
        self.all_game_words = all_game_words
        self.initiate_game()
        self.initiate_players(players)

    def initiate_game(self):
        # Randomly choose 25 words and assign to teams (9 -> red,8 -> blue,7 -> neutral,1 -> assassin)
        self.game_words = np.random.choice(self.all_game_words, 25, replace=False)
        self.guess_status = np.zeros(25)
        self.word_team = [1] * 9 + [2] * 8 + [3] * 7 + [4]
        # Resuffle for random display
        self.display_order = np.random.choice(range(25), 25, replace=False)
        return None
    
    def initiate_players(self, players):
        module = importlib.import_module('agents.' + players[0])
        team_a = getattr(module, players[1])

        self.ta_ms = team_a()
        self.ta_gs = team_a()


        module = importlib.import_module('agents.' + players[2])
        team_b = getattr(module, players[3])

        self.tb_ms = team_b()
        self.tb_gs = team_b()
        return None
        
    def display_board(self, status_ref, team, turn):
        if (self.mode == 'batch'):
            return None
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
    
    def check_game_end(self, team, turn, logFile):
        other_team = {'A': 'B', 'B': 'A'}
        if 0 not in self.guess_status[:9]:
            self.display_board(self.guess_status, team, turn)
            print("GAME OVER IN {} TURNS! TEAM A wins this one by finding out all their words!".format(turn))
            self.write_to_log(logFile, "GAME OVER IN {} TURNS! TEAM A wins this one by finding out all their words!".format(turn))
            return True, 'A'
        if 0 not in self.guess_status[9:17]:
            self.display_board(self.guess_status, team, turn)
            print("GAME OVER IN {} TURNS! TEAM B wins this one by finding out all their words!".format(turn))
            self.write_to_log(logFile, "GAME OVER IN {} TURNS! TEAM B wins this one by finding out all their words!".format(turn))
            return True, 'B'
        if self.guess_status[-1] != 0:
            self.display_board(self.guess_status, team, turn)
            print("GAME OVER IN {} TURNS! TEAM {} wins this one as TEAM {} revealed the assassin word!".format(turn, other_team[team], team))
            self.write_to_log(logFile, "GAME OVER IN {} TURNS! TEAM {} wins this one as TEAM {} revealed the assassin word!".format(turn, other_team[team], team))
            return True, other_team[team]
        return False, None

    def get_turn_words(self, guess_words, words):
        temp = [word for word in words if word not in guess_words]
        return temp

    def create_log_file(self):
        if not os.path.exists("Logs"):
            os.makedirs("Logs")
        timeStamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        logFileName = os.path.join("Logs", f"log_{timeStamp}.txt")
        return logFileName

    def write_to_log(self, logFile, message):
        with open(logFile, "a") as f:
            timeStamp = datetime.datetime.now().strftime("%Y-%m-%d_%H:%M:%S")
            f.write(f"[{timeStamp}] {message}\n")

    
    def play(self):
        turn = 1
        assassin = False
        self.guesses = []
        logFile = self.create_log_file()
        self.write_to_log(logFile, "For reproducibility, the random seed used in this game is {}.".format(self.seed))
        self.experience = []

        while True:
            # TEAM A GIVE HINT
            self.display_board(self.word_team, 'A', turn)
            time.sleep(4 * (self.mode=='interactive'))
            team_a_words = self.get_turn_words(self.guesses, self.game_words[:9])
            team_b_words = self.get_turn_words(self.guesses, self.game_words[9:17])
            neutral_words = self.get_turn_words(self.guesses, self.game_words[17:24])
            assasin_word = self.get_turn_words(self.guesses, self.game_words[24])
            word, count = self.ta_ms.give_hint('A', 'B', self.game_words, self.guess_status, team_a_words, team_b_words, neutral_words, assasin_word, self.experience)
            self.write_to_log(logFile, "Team A Hint For Turn {}:{}:{}".format(turn, word, count))
            self.experience += [{"team": "Team A", "action": "Hint", "prompt": word, "count": count}]
            # TEAM A GUESS
            self.display_board(self.guess_status, 'A', turn)
            print("TEAM A Spymaster: My hint is {}: {}".format(word, count))
            words_not_guessed = self.game_words[np.where(self.guess_status == 0)]
            getGuessA = self.ta_gs.make_guess(word, count, words_not_guessed, self.guess_status, self.experience)
            guess = getGuessA
            for word in guess:
                word = word.upper()
                time.sleep(2 * (self.mode=='interactive'))
                print("TEAM A Guesser: I guess \"{}\" is our word".format(word))
                idx_in_game_words = np.argwhere(self.game_words == word)
                time.sleep(1.5 * (self.mode=='interactive'))
                guessResult = ""
                self.guesses += [word]
                if idx_in_game_words < 9:
                    print("TEAM A Spymaster: That is correct!")
                    self.guess_status[idx_in_game_words] = 1
                    guessResult = "Correct"
                    self.write_to_log(logFile, "Team A Guess:{}. With result:{}".format(word, guessResult))
                    self.experience += [{"team": "Team A", "action": "Guess", "prompt": word, "result": guessResult}]
                elif idx_in_game_words < 17:
                    print("TEAM A Spymaster: That is incorrect... It is the opponents' word...")
                    self.guess_status[idx_in_game_words] = 2
                    guessResult = "Incorrect - Opponents Word"
                    self.write_to_log(logFile, "Team A Guess:{}. With result:{}".format(word, guessResult))
                    self.experience += [{"team": "Team A", "action": "Guess", "prompt": word, "result": guessResult}]
                    break
                elif idx_in_game_words < 24:
                    print("TEAM A Spymaster: That is incorrect... It is a neutral word...")
                    self.guess_status[idx_in_game_words] = 3
                    guessResult = "Incorrect - Neutral Word"
                    self.write_to_log(logFile, "Team A Guess:{}. With result:{}".format(word, guessResult))
                    self.experience += [{"team": "Team A", "action": "Guess", "prompt": word, "result": guessResult}]
                    break
                else:
                    print("TEAM A Spymaster: That is incorrect... It is the assassin word...")
                    self.guess_status[idx_in_game_words] = 4
                    assassin = True
                    guessResult = "Incorrect - Assassin Word"
                    self.write_to_log(logFile, "Team A Guess:{}. With result:{}".format(word, guessResult))
                    self.experience += [{"team": "Team A", "action": "Guess", "prompt": word, "result": guessResult}]
                    break
            
            # TEAM A FINISH
            game_ended, winner = self.check_game_end('A', turn, logFile)
            if game_ended:
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
            word, count = self.tb_ms.give_hint('B', 'A', self.game_words, self.guess_status, team_b_words, team_a_words, neutral_words, assasin_word, self.experience)
            self.write_to_log(logFile, "Team B Hint For Turn {}:{}:{}".format(turn, word, count))
            self.experience += [{"team": "Team A", "action": "Hint", "prompt": word, "count": count}]
            # TEAM B GUESS
            self.display_board(self.guess_status, 'B', turn)
            print("TEAM B Spymaster: My hint is {}: {}".format(word, count))
            words_not_guessed = self.game_words[np.where(self.guess_status == 0)]
            getGuessB = self.tb_gs.make_guess(word, count, words_not_guessed, self.guess_status, self.experience)
            guess = getGuessB
            for word in guess:
                word = word.upper()
                time.sleep(2 * (self.mode=='interactive'))
                print("TEAM B Guesser: I guess \"{}\" is our word".format(word))
                idx_in_game_words = np.argwhere(self.game_words == word)
                time.sleep(1.5 * (self.mode=='interactive'))
                guessResult = ""
                self.guesses += [word]
                if idx_in_game_words < 9:
                    print("TEAM B Spymaster: That is incorrect... It is the opponents' word...")
                    self.guess_status[idx_in_game_words] = 1
                    guessResult = "Incorrect - Opponents Word"
                    self.write_to_log(logFile, "Team B Guess:{}. With result:{}".format(word, guessResult))
                    self.experience += [{"team": "Team A", "action": "Guess", "prompt": word, "result": guessResult}]
                    break
                elif idx_in_game_words < 17:
                    print("TEAM B Spymaster: That is correct!")
                    self.guess_status[idx_in_game_words] = 2
                    guessResult = "Correct"
                    self.write_to_log(logFile, "Team B Guess:{}. With result:{}".format(word, guessResult))
                    self.experience += [{"team": "Team A", "action": "Guess", "prompt": word, "result": guessResult}]
                elif idx_in_game_words < 24:
                    print("TEAM B Spymaster: That is incorrect... It is a neutral word...")
                    self.guess_status[idx_in_game_words] = 3
                    guessResult = "Incorrect - Neutral Word"
                    self.write_to_log(logFile, "Team B Guess:{}. With result:{}".format(word, guessResult))
                    self.experience += [{"team": "Team A", "action": "Guess", "prompt": word, "result": guessResult}]
                    break
                else:
                    print("TEAM B Spymaster: That is incorrect... It is the assassin word...")
                    self.guess_status[idx_in_game_words] = 4
                    assassin = True
                    guessResult = "Incorrect - Assassin Word"
                    self.write_to_log(logFile, "Team B Guess:{}. With result:{}".format(word, guessResult))
                    self.experience += [{"team": "Team A", "action": "Guess", "prompt": word, "result": guessResult}]
                    break
            # TEAM B FINISH
            game_ended, winner = self.check_game_end('B', turn, logFile)
            if game_ended:
                break
            print("END OF TURN")
            time.sleep(2 * (self.mode=='interactive'))

            turn += 1
        
        self.write_to_log(logFile, "{}".format(self.experience))
        # Wrap up and Recording
        print("For reproducibility, the random seed used in this game is {}.".format(self.seed))
        return winner

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-p', '--players', type=str, nargs='+', help='list of player types [1. Human / 2. AI]')
    parser.add_argument('-m', '--mode', type=str, default='interactive', help='mode of the game (interactive / testing/ batch)')
    parser.add_argument('-s', '--seed', type=int, default=np.random.randint(2**31 - 1), help='random seed used in this game (0 - 2^31-1)')
    parser.add_argument('-n', '--number_batch', type=int, default=100, help='number of games to play in batch mode')
    parser.add_argument('-o', '--output_file', type=str, default=None, help='the file to record statistics')
    opt = parser.parse_args()

    if opt.mode == 'batch':
        teamA_name = opt.players[0]
        teamB_name = opt.players[2]
        teamA_wins = 0
        teamB_wins = 0
        for i in range(opt.number_batch):
            if i % 2 == 0:
                players = opt.players
            else:
                players = [opt.players[2], opt.players[3], opt.players[0], opt.players[1]]
            game = Codenames(
                players,
                opt.mode,
                np.random.randint(2**31 - 1),
                opt.output_file
            )
            winning_team = game.play()
            if (winning_team == 'A' and i % 2 == 0) or (winning_team == 'B' and i % 2 == 1):
                teamA_wins += 1
            else:
                teamB_wins += 1
        print("\n" + "*" * 50)
        print("Batch Mode Results:")
        print("TEAM {} won {} times".format(teamA_name, teamA_wins))
        print("TEAM {} won {} times".format(teamB_name, teamB_wins))
        print("*" * 50 + "\n")
        exit()

    game = Codenames(
        opt.players,
        opt.mode,
        opt.seed,
        opt.output_file
    )

    game.play()