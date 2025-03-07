from player import Player
import numpy as np
from langchain_core.prompts import ChatPromptTemplate
from bentley.llm_proxy import MLServiceAzureChatOpenAI
from pymlrestclientV1_3 import MLClient
import os
from dotenv import load_dotenv

load_dotenv()

class redBot(Player):
    def __init__(self):
        self.auth_client = MLClient(
        base_url=os.getenv("ML_BASE_URL"),
        auth_uri=os.getenv("ML_AUTH_URI"),
        client_id=os.getenv("ML_CLIENT_ID"),
        client_secret=os.getenv("ML_CLIENT_SECRET"),
        scopes=os.getenv("ML_SCOPES"),
        application_type=os.getenv("ML_APPLICATION_TYPE"),)

        def get_token():
            return self.auth_client.token

        self.chat_llm = MLServiceAzureChatOpenAI(
            model_name="gpt-4o", # open AI chat model
            api_version="2024-02-01", # open AI api version
            url_prefix="dev-",
            azure_ad_token_provider=get_token, # callable function
            temperature=0,)

        self.getHintsPrompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system", """You are a helpful assistant that gives hint to your team for a game of Codenames. Where you belong to the team {your_team}, and your team is tasked with guessing these words {your_team_words}.
                    You are also faced with an opponent team {opposite_team}, which has a similar player giving hint based on their words {opposite_team_words}. And if your team player guesses one of these words, the other team gets and advantage. so you have to make sure that you don't hint towards their words.
                    Other than that there are also neutral words {neutral_words}, which are inconsequential for gaining advantage but if guessed causes a loss of turn for our team and thus very undesirable.
                    And there is one assassin word {assassin_word} which is of utmost importance as if this is guessed by our team based on your hint, the game instantly ends and we LOSE. As a result you have to be very careful to NEVER give a hint that may cause your team to guess this word.
                    Along with this you have also been given an list of experiences: {experience}, which are results of the previous rounds. And have been labeled so that you can use it to not repeat your own mistakes and better strategies your hints based on the hints and the guesses of the opponent teams.
                    Each of the experience is the format ("team": "Team name", "action": "Hint", "prompt": word, "count": count) for HINT, and ("team": "Team A", "action": "Guess", "prompt": word, "result": guessResult) for GUESS RESULT.
                    The "prompt" and "count" in the "action": Hint are "HINT" and "COUNT" of the guesses.
                    And the "prompt" and "result" in the "action": Guess are the guessed word and the result (Correct/ Incorrect - Neutral Word/ Incorrect - Opponents Word) for that guessed word.
                    You are supposed to give the hint in the form of 'Hint, Number' (example Education, 2) (do not add any other prompt like "Hint: Education, 2" etc) where 'number' is the number of words that can be guessed from the hint and 'hint' is the one word hint to guess the words based on your teams words"""
                )
            ]
        )

        self.getGuessPrompt =ChatPromptTemplate.from_messages(
            [
                (
                    "system", """You are a helpful assistant that guesses upto {number} of words in a game of Codenames out of the total {total_words} based on the clue/hint: {hint} given to you.
                    Along with this you have also been given an list of experiences: {experience}, which are results of the previous rounds. And have been labeled so that you can use it to not repeat your own mistakes and better strategies your hints based on the hints and the guesses of the opponent teams.
                    Each of the experience is the format ("team": "Team name", "action": "Hint", "prompt": word, "count": count) for HINT, and ("team": "Team A", "action": "Guess", "prompt": word, "result": guessResult) for GUESS RESULT.
                    The "prompt" and "count" in the "action": Hint are "HINT" and "COUNT" of the guesses.
                    And the "prompt" and "result" in the "action": Guess are the guessed word and the result (Correct/ Incorrect - Neutral Word/ Incorrect - Opponents Word) for that guessed word.
                    Give me the guesses in a form of a words separated by ',' and nothing else. For example: 'HORSE, LION, TIGER' based on the number: 3, hint/clue: 'Animals'.
                    And arrange the guesses in the descending order of their probability of being correct. For example if you are 90 percent sure that LION is one of your teams words, 75 percent sure that TIGER is and 40 percent sure that HORSE is,
                    Arrange the words as "LION, TIGER, HORSE" instead. And make sure the given words are all ONLY FROM THE {total_words} and not random."""
                )
            ]
        )

    def give_hint(self, your_team, opponent_team, game_words, guess_status, team_words, opponent_words, neutral_words, assassin_word, experience):
        formatted_prompt = self.getHintsPrompt.format_messages(your_team = your_team, your_team_words = team_words, opposite_team = opponent_team, opposite_team_words = opponent_words, assassin_word = assassin_word, neutral_words = neutral_words, experience = experience)
        res = self.chat_llm.invoke(formatted_prompt)
        getHint = res.content.split(', ')
        word, count = "", 0
        while True:
            # Create hint and count here
            word, count = getHint
            # Continuously loops until valid hint and count are given
            if self.validate_hint(word, int(count), game_words):
                break
        return word, count
        #TODO: validation would be one word and not directly in the game words
        #TODO: just queries LLM

    def make_guess(self, hint, number, words, guess_status, experience):
        formatted_prompt = self.getGuessPrompt.format_messages(number = number, hint = hint, total_words = words, experience = experience)
        res = self.chat_llm.invoke(formatted_prompt)
        getGuess = [guess.strip() for guess in res.content.split(',')]
        guesses = []
        while True:
            # Code for guessing goes here
            number_of_guesses = int(number) + 1
            guesses = getGuess
            # While loop continues until valid guesses are given
            if self.validate_guess(guesses, number, words, guess_status):
                break
        return guesses
        #TODO: validation needs to be a word from the board
        #TODO: just queries LLM