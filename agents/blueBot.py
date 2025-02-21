from player import Player
import numpy as np
from langchain_core.prompts import ChatPromptTemplate
from bentley.llm_proxy import MLServiceAzureChatOpenAI
from pymlrestclientV1_3 import MLClient

class blueBot(Player):
    def __init__(self):
        self.auth_client = MLClient(
        base_url="http://dev-connect-ml-service-eus.bentley.com",
        auth_uri="https://qa-ims.bentley.com",
        client_id="codenames-hackathon",
        client_secret="gAj5TPt6d/ig+KoWVcmvHP+I9znW66r6pdNVAu3AIjUqovX5fw5Km7QQWkg+0Wtq/QrtoHtXWce6I3NdnLZ+8w==",
        scopes="aiml:llm-proxy",
        application_type="service",)

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
                    "system", """You are a helpful assistant that gives hints for a game of Codenames based on your team: {your_team}, your team words: {your_team_words}, 
                    and avoiding any hint that will hint towards the opposite team: {opposite_team}, their words: {opposite_team_words} and the specifically avoiding the assassin word: {assassin_word}.
                    Give the hint in the form of 'Hint, Number' (example Education, 2) (do not add any other prompt like "Hint: Education, 2" etc) where 'number' is the number of words that can be guessed from the hint and 'hint' is the one word hint to guess the words based on your teams words"""
                )
            ]
        )

        self.getNewHintPrompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system", """You are a helpful assistant that gives hints for a game of Codenames based on your team: {your_team}, your team words: {your_team_words}, 
                    and avoiding any hint that will hint towards the opposite team: {opposite_team}, their words: {opposite_team_words} and the specifically avoiding the assassin word: {assassin_word}.
                    Give the hint in the form of 'Hint, Number' (example Education, 2) (do not add any other prompt like "Hint: Education, 2" etc) where 'number' is the number of words that can be guessed from the hint and 'hint' is the one word hint to guess the words based on your teams word
                    You have previously given an invalid hint, "{previous_clue}", and received the following messsage: "{invalid_message}". Give another hint in the same form.
                    """
                )
            ]
        )

        self.getGuessPrompt =ChatPromptTemplate.from_messages(
            [
                (
                    "system", """You are a helpful assistant that guesses upto {number} of words in a game of Codenames out of the total {total_words} based on the clue/hint: {hint} given to you.
                    Give me the guesses in a form of a words separated by ',' and nothing else. For example: 'Horse, Lion, Tiger' based on the number: 3, hint/clue: 'Animals'."""
                )
            ]
        )

        self.getNewGuessPrompt =ChatPromptTemplate.from_messages(
            [
                (
                    "system", """You are a helpful assistant that guesses upto {number} of words in a game of Codenames out of the total {total_words} based on the clue/hint: {hint} given to you.
                    Give me the guesses in a form of a words separated by ',' and nothing else. For example: 'Horse, Lion, Tiger' based on the number: 3, hint/clue: 'Animals'.
                    You have previously given the following invalid guess(es), "{previous_guess}", and received the following error messsage(s): "{invalid_message}". Give another guess in the same form with these error messages in mind."""
                )
            ]
        )

    def give_hint(self, your_team, opponent_team, game_words, guess_status, team_words, opponent_words, neutral_words, assassin_word, experience):
        formatted_prompt = self.getHintsPrompt.format_messages(your_team = your_team, your_team_words = team_words, opposite_team = opponent_team, opposite_team_words = opponent_words, assassin_word = assassin_word)
        res = self.chat_llm.invoke(formatted_prompt)
        getHint = res.content.split(', ')
        word, count = getHint
        
        while True:
            # Continuously loops until valid hint and count are given
            valid, message = self.validate_hint(word, int(count), game_words)
            if valid:
                break
            # Create hint and count here
            formatted_prompt = self.getNewHintPrompt.format_messages(your_team = your_team, 
                                                                     your_team_words = team_words, 
                                                                     opposite_team = opponent_team, 
                                                                     opposite_team_words = opponent_words, 
                                                                     assassin_word = assassin_word,
                                                                     previous_clue = res.content,
                                                                     invalid_message = message)
            res = self.chat_llm.invoke(formatted_prompt)
            getHint = res.content.split(', ')
            word, count = getHint
        return word, count
        #TODO: validation would be one word and not directly in the game words
        #TODO: just queries LLM

    def make_guess(self, hint, number, words, guess_status, experience):
        formatted_prompt = self.getGuessPrompt.format_messages(number = number, hint = hint, total_words = words)
        res = self.chat_llm.invoke(formatted_prompt)
        guesses = [guess.strip() for guess in res.content.split(',')]
        all_guesses = guesses
        messages = []
        while True:
            # Code for guessing goes here
            valid, message = self.validate_guess(guesses, number, words, guess_status)
            messages.append(message)
            # While loop continues until valid guesses are given
            if valid:
                break
            # Create guesses here
            formatted_prompt = self.getNewGuessPrompt.format_messages(number = number, 
                                                                      hint = hint, 
                                                                      total_words = words,
                                                                      previous_guess = ", ".join(all_guesses),
                                                                      invalid_message = "\", \"".join(messages))
            res = self.chat_llm.invoke(formatted_prompt)
            guesses = [guess.strip() for guess in res.content.split(',')]
            all_guesses.extend(guesses)

        return guesses
        #TODO: validation needs to be a word from the board
        #TODO: just queries LLM