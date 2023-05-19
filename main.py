import string
import pandas as pd
import csv
import requests
import datetime as datetime
from datamuse import Datamuse
from num2words import num2words
# https://api.datamuse.com/words?sl=i%27ll
# https://wordsapiv1.p.rapidapi.com/words/aberration/syllables | This costs money after 2500 requests
# https://github.com/gmarmstrong/python-datamuse/
# https://www.datamuse.com/api/#md
#
# https://www.onelook.com/thesaurus/?s=&f_ns=6&sortby=le0&sorttopn=1000
# https://www.howmanysyllables.com

offset = 0 # Default: 0

# Retrieves the word from the Datamuse API to get the number of syllables.
def get_word_syllables(word: str) -> int:
    """Gets the syllable count of a word.

    :param word: The word to get the syllables for.
    :return: integer for the amount of syllables.
    """

    #print(f"Word: {word}") #LOGGING
    api = Datamuse()
    results = api.words(sl=word)
    #print(f"API returned results: {results}") #LOGGING
    #print(f"Type: {type(results)}") #LOGGING
    if list(filter(lambda x : x['word'] == word, results)): # Check to see if the word itself is in the list.
        result = list(filter(lambda x : x['word'] == word, results))[0]
    else: # get the word with the highest score.
        result = max(results, key=lambda x:x['score'])
    #print(f"Selected: {result} {type(result)}") #LOGGING
    if result:
        return result['numSyllables']
    else:
        return 0


# Get the sentence's syllables
def get_sentence_syllables(sentences: str, format_option: int) -> list:
    """Gets the syllable count in a phrase, sentence, or group of lines.

    :param sentences: The phrase, sentence, or group of lines to get the syllables for.
    :param format_option: Whether we are encoding or decoding a string - to be passed into the format_api_sentence call.
    :return: a list of syllables per line/sentence.
    """

    syllables = list()
    #print(f"Passed in the following:\n----\n{sentences}\n----")
    formatted_sentences = format_api_sentence(sentences, format_option)
    #print(formatted_sentences, type(formatted_sentences)) #LOGGING
    sentences = formatted_sentences.split("\n")
    for sentence in sentences:
        sentence_syllables = 0  # Initialize the sentence syllable counter
        #print(f"Sending the following sentence to Datamuse: \"{sentence}\"") #LOGGING
        for word in sentence.split():
            sentence_syllables += get_word_syllables(word)
        #print(f"The sentence \"{sentence}\" has a total of {sentence_syllables} syllables.")
        syllables.append(sentence_syllables)
        #print(syllables)
    return syllables


# Removes punctuation and changes any numeric number into the correct english word.
def format_api_sentence(sentence: str, option: int) -> str:
    """Formats a sentence to be sent to the Datamuse API.

    :param sentence: The sentence we need to format.
    :param option: Whether we are encoding(2) or decoding(1) a message.
    :return: a string of the formatted sentence.
    """

    if option == 1: # DECODE
        decode_punctuation = string.punctuation.replace("'", "").replace("-", "") # required to not remove ' and - from the sentence.
        new_sentence = sentence.translate(str.maketrans('', '', decode_punctuation)) # remove any punctuation defined in decode_punctuation.
        for word in new_sentence.split(" "):
            if word.isnumeric(): # change numeric values into the english words.
                new_sentence = new_sentence.replace(word, num2words(word))
        return new_sentence.lower()
    elif option == 2: # ENCODE
        new_sentence = sentence.translate(str.maketrans('', '', string.punctuation)) # remove all punctuation.
        for word in new_sentence.split(" "):
            if word.isnumeric(): # change numeric values into the english words.
                new_sentence = new_sentence.replace(word, num2words(word))
        return new_sentence.upper()

# Decodes a message.
def decode(input_message: str) -> str:
    """Decodes a message according to the codex on the system.

    :param input_message: The message we want to decode.
    :return: a str of the decoded message.
    """

    decoded_message = str()
    syllables_list = []
    if not input_message or len(input_message) < 1:
        input_message = "haven't done it\n" \
                        "singularity\n" \
                        "forty-five"

    for sentence in input_message.split("\n"):
        sentence = sentence.rstrip("\r")
        #print(f"sentence: {sentence}")
        syllables_list.append(get_syllables_for_sentence(sentence))

    #print(f"syllables_list: {syllables_list}")

    # Get the corresponding letters according to the codex
    with open('codex.txt', encoding="utf8") as f:
        codex_lines = f.readlines()
        codex_list = [l.strip("\n") for l in codex_lines]
    #print(f"Codex List: {codex_list}") #LOGGING
    for num in syllables_list:
        #print(f"{num} syllables = {codex_list[num - (1 + offset)]}") #LOGGING
        decoded_message += codex_list[num - (1 + offset)]
        #print(codex_list[num - 1])
    #print(f"Decoded Message:\n  {decoded_message}")
    #print(type(decoded_message))
    return decoded_message


# Encodes a message
def encode(input_message: str) -> str:
    """Encodes a message according the codex on the system.

    :param input_message: The message we want to encode.
    :return: a str of the encoded message.
    """
    print("ENCODING...")
    syllables = list()
    encoded_message = str()
    words = list()

    if not input_message or len(input_message) < 1:
       input_message = "test message"

    # Format the message
    formatted_message = format_api_sentence(input_message, 2)

    # Get the corresponding letters according to the codex.
    with open('codex.txt') as f:
        codex_lines = f.readlines()
        codex_list = [l.strip("\n") for l in codex_lines]
    #print(codex_list)

    # Get the syllables needed for each line of the encoded message.
    for c in formatted_message:
        if c == " ":
            continue
        #print(codex_list.index(c))
        syllables.append(codex_list.index(c) + (1 + offset))
        #print(syllables)

    #1. get words for the syllable count of a line.
    for num in syllables:
        num = int(num)
        word = get_words_for_syllables(num)
        words.append(word)
        #print(word)
        #print(words)

    #2. build the message.
    for line in words:
        encoded_message = encoded_message + "\n" + line
    #print(encoded_message)
    return encoded_message


def get_words_for_syllables(total_syllables: int) -> str:
    """Gets a word or words for a provided number of syllables.

    :param total_syllables: The number of syllables needed to be fulfilled.
    :return: str - A space separated string of words.
    """

    # Use pandas to read the list of words to find a word to use.
    df = pd.read_csv('phoneticDictionary_cleaned_20230515.csv')
    syllables_used = 0
    words = ""

    # While we still have syllables to use, get another word.
    while syllables_used < total_syllables:
        print(f"\nTotal syllables: {total_syllables}")
        print(f"Syllables used: {syllables_used}")

        # Create a dataframe for words with a syllable count compatible with the number of syllables left.
        df_matching_syllables = df.loc[df['syl'] <= (total_syllables - syllables_used)]
        #print(df_matching_syllables)

        # Get a random sample of rows from the dataframe.
        row = df_matching_syllables.sample()
        #print(f"Row selected:\n{row}")
        #print(row['syl'].values[0])

        # Add the word to the return string.
        words += row['word'].values[0] + " "
        syllables_used += row['syl'].values[0]
        #print(row['word'].values[0])
    return words.rstrip(" ")


def get_syllables_for_sentence(sentence: str) -> int:
    """Gets the syllable count for a sentence.

    :param sentence: The sentence to get the syllables for.
    :return: int - The amount of syllables in the sentence.
    """

    df = pd.read_csv('phoneticDictionary_cleaned_20230515.csv')
    words = sentence.split(' ')
    syllables = 0

    #print(words)
    for word in words:
        df_matching_word = df.loc[df['word'] == word]
        syllables += df_matching_word['syl'].values[0]
        #print(syllables, type(syllables), len(df_matching_word['syl']), df_matching_word['syl'].values[0])

    return syllables


def clean_dictionary():
    """Cleans the data in phoneticDictionary.csv and puts it into new_clean.csv

    This will remove words that start with an apostrophe, contain a period, or are contained in the list twice.
    Provides a clean dataset to use named "phoneticDictionary_cleaned_{date}.csv

    :return:
    """
    print('cleaning the dictionary.')
    new_filename = f"phoneticDictionary_cleaned_{datetime.datetime.now().strftime('%Y%m%d')}.csv"
    print(new_filename)
    with open('phoneticDictionary.csv', 'r', encoding='utf8') as in_file, open(new_filename, 'w', encoding='utf8', newline='') as out_file:
        seen = set()
        reader = csv.DictReader(in_file)
        writer = csv.writer(out_file)

        writer.writerow(['id', 'word', 'phon', 'syl', 'start', 'end'])
        for row in reader:
            word = row['word'] # Get the word for the row

            # If the word is a duplicate, starts with "'", or contains "." skip it.
            if word in seen or word.startswith("'") or "." in word:
                continue

            # Write the row to the new file & add it to the list of seen words.
            writer.writerow([
                row['id'],
                row['word'],
                row['phon'],
                row['syl'],
                row['start'],
                row['end']
            ])
            seen.add(word)


def validate_word(word: str) -> bool:
    """Checks to ensure the word chosen is a valid word.

    Makes a request to the WordsAPI to see if the provided word returns a valid result.
    We are only allowed 2,500 requests per day for free.

    :param word: The word to check
    :return: bool: True if the word is valid
    """

    url = f"https://wordsapiv1.p.rapidapi.com/words/{word}/syllables"

    with open('credentials.txt', 'r', encoding="utf8") as f:
        for line in f:
            if line.startswith('"X-RapidAPI-Key":'):
                api_key = (line.split(":")[1].split('"')[1])

    headers = {
        "X-RapidAPI-Key": api_key,
        "X-RapidAPI-Host": "wordsapiv1.p.rapidapi.com"
    }

    response = requests.get(url, headers=headers)
    global words_api_counter
    words_api_counter += 1

    print(response.json(), response.status_code)
    if response.status_code != 200:
        print('bad resp')
        return False
    else:
        print('good resp')
        return True


if __name__ == '__main__':
    print("Calling __main__")
    offset = 0 # Default: 0
    words_api_counter = 0
    #encode() # Completed
