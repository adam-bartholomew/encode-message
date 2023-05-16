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
def get_sentence_syllables(sentences: str) -> list:
    """Gets the syllable count in a phrase, sentence, or group of lines.

    :param sentences: The phrase, sentence, or group of lines to get the syllables for.
    :return: a list of syllables per line/sentence.
    """

    syllables = list()
    print(f"Passed in the following:\n----\n{sentences}\n----")
    formatted_sentences = format_api_sentence(sentences, 1)
    #print(formatted_sentences, type(formatted_sentences)) #LOGGING
    sentences = formatted_sentences.split("\n")
    for sentence in sentences:
        sentence_syllables = 0  # Initialize the sentence syllable counter
        #print(f"Sending the following sentence to Datamuse: \"{s}\"") #LOGGING
        for word in sentence.split():
            sentence_syllables += get_word_syllables(word)
        print(f"The sentence \"{sentence}\" has a total of {sentence_syllables} syllables.")
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
        decode_punctuation = string.punctuation.replace("'", "").replace("-", "") # required to not remove '' and - from the sentence.
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
def decode():
    """Decodes a message according to the codex on the system.

    :return:
    """

    return_message = str()
    input_message = "haven't done it\n" \
               "singularity\n" \
                "forty-five"

    syllables = get_sentence_syllables(input_message)

    # Get the corresponding letters according to the codex
    with open('codex.txt') as f:
        codex_lines = f.readlines()
        codex_list = [l.strip("\n") for l in codex_lines]
    #print(f"Codex List: {codex_list}") #LOGGING
    for num in syllables:
        #print(f"{i} syllables = {codex_list[num - (1 + offset)]}") #LOGGING
        return_message += codex_list[num - (1 + offset)]
    #print(codex_list[sentence_syllables - 1])
    print(f"Decoded Message:\n  {return_message}")


# Encodes a message
def encode():
    """Encodes a message according the codex on the system.

    :return:
    """
    print("ENCODING...")
    syllables = list()
    encoded_message = str()
    words = list()
    input_message = "I'm dumb 2"

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
    print(encoded_message)

# //TODO: Need to rethink/redo this part. Maybe use a word list, grab a random word and check it's syllables on the datamuse api.
def get_words_for_syllables(total_syllables: int) -> str:
    df = pd.read_csv('phoneticDictionary_cleaned_20230515.csv')
    syllables_used = 0
    words = ""
    while syllables_used < total_syllables:
        print(f"\nTotal syllables: {total_syllables}")
        print(f"Syllables used: {syllables_used}")
        df_matching_syllables = df.loc[df['syl'] <= (total_syllables - syllables_used)]
        #print(df_matching_syllables)
        row = df_matching_syllables.sample()
        print(f"Row selected:\n{row}")
        #print(row['syl'].values[0])
        words += row['word'].values[0] + " "
        syllables_used += row['syl'].values[0]
        #print(row['word'].values[0])
    return words.rstrip(" ")


def clean_dictionary():
    """Cleans the data in phoneticDictionary.csv and puts it into new_clean.csv

    This will remove words that start with an apostrophe, contain a period, or are contained in the list twice.
    Provides a clean dataset to use named "phoneticDictionary_cleaned_{date}.csv

    :return:
    """
    print('clean the dictionary')
    new_filename = f"phoneticDictionary_cleaned_{datetime.datetime.now().strftime('%Y%m%d')}.csv"
    print(new_filename)
    with open('phoneticDictionary.csv', 'r', encoding='utf8') as in_file, open(new_filename, 'w', encoding='utf8', newline='') as out_file:
        seen = set()
        reader = csv.DictReader(in_file)
        writer = csv.writer(out_file)

        writer.writerow(['id', 'word', 'phon', 'syl', 'start', 'end'])
        for row in reader:
            word = row['word']
            if word in seen or word.startswith("'") or "." in word: # If the word is a duplicate, starts with "'", or contains "." skip it.
                continue
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
    """Checks to ensure the word chosen is valid.

    Makes a request to the WordsAPI to see if the provided word returns a valid result.
    We are only allowed 2,500 requests per day for free.

    :param word: The word to check
    :return: bool: True if the word is valid
    """

    url = f"https://wordsapiv1.p.rapidapi.com/words/{word}/syllables"

    with open('credentials.txt', 'r') as f:
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
    encode() # Completed
