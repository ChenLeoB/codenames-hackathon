from langchain_core.prompts import ChatPromptTemplate
from bentley.llm_proxy import MLServiceAzureChatOpenAI
from pymlrestclientV1_3 import MLClient
# from azure.ai.ml import MLClient

auth_client = MLClient(
    base_url="http://dev-connect-ml-service-eus.bentley.com",
    auth_uri="https://qa-ims.bentley.com",
    client_id="codenames-hackathon",
    client_secret="gAj5TPt6d/ig+KoWVcmvHP+I9znW66r6pdNVAu3AIjUqovX5fw5Km7QQWkg+0Wtq/QrtoHtXWce6I3NdnLZ+8w==",
    scopes="aiml:llm-proxy",
    application_type="service",
)

def get_token():
    return auth_client.token

chat_llm = MLServiceAzureChatOpenAI(
    model_name="gpt-4o", # open AI chat model
    api_version="2024-02-01", # open AI api version
    url_prefix="dev-",
    azure_ad_token_provider=get_token, # callable function
    temperature=0,
    )

prompt1 = ChatPromptTemplate.from_messages(
    [
        (
            "system", """You are a helpful assistant that gives hints for a game of Codenames based on your team: {your_team}, your team words: {your_team_words}, 
            and avoiding any hint that will hint towards the opposite team: {opposite_team}, their words: {opposite_team_words} and the specifically avoiding the assassin word: {assassin_word}.
            Give the hint in the form of 'Number:Hint' where 'number' is the number of words that can be guessed from the hint and 'hint' is the one word hint to guess the words based on your teams words"""
        )
    ]
)

def get_hint(yourTeam: str, yourTeamWords: str, oppositeTeam: str, oppositeTeamWords: str, assassinWord: str):
    formatted_prompt = prompt1.format_messages(your_team = yourTeam, your_team_words = yourTeamWords, opposite_team = oppositeTeam, opposite_team_words = oppositeTeamWords, assassin_word = assassinWord)
    res = chat_llm.invoke(formatted_prompt)
    return res.content

yourTeam = "Red"
yourTeamWords = "BATTERY, GOLD" 
oppositeTeam =  "Blue"
oppositeTeamWords = "CASTLE"
assassinWord = "DOG"

res1 = get_hint(yourTeam, yourTeamWords, oppositeTeam, oppositeTeamWords, assassinWord)
print(res1)

prompt2 = ChatPromptTemplate.from_messages(
    [
        (
            "system", """You are a helpful assistant that guesses upto {number} of words in a game of Codenames out of the total {total_words} based on the clue/hint: {hint} given to you.
            Give me the guesses in a form of a words separated by ',' and nothing else. For example: 'Horse, Lion, Tiger' based on the number: 3, hint/clue: 'Animals'."""
        )
    ]
)

def get_guesses(number: str, hint: str, totalWords: str):
    formatted_prompt = prompt2.format_messages(number = number, hint = hint, total_words = totalWords)
    res = chat_llm.invoke(formatted_prompt)
    return res.content

parts = res1.split(":")
number = parts[0]
hint = parts[1]
totalWords = yourTeamWords + oppositeTeamWords + assassinWord + "TASTE, PLASTIC, CHEESE, CHECK"

res2 = get_guesses(number, hint, totalWords)
print(res2)