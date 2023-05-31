import string
import pandas as pd
import csv
import requests
import datetime as datetime
from datamuse import Datamuse
from num2words import num2words
from typing import Union
import logging
# https://api.datamuse.com/words?sl=i%27ll
# https://wordsapiv1.p.rapidapi.com/words/aberration/syllables | This costs money after 2500 requests
# https://github.com/gmarmstrong/python-datamuse/
# https://www.datamuse.com/api/#md
#
# https://www.onelook.com/thesaurus/?s=&f_ns=6&sortby=le0&sorttopn=1000
# https://www.howmanysyllables.com

offset = 0  # Default: 0
log_filename = "./logs/encode-message_" + datetime.datetime.now().strftime("%Y%m%d") + ".log"
logging.basicConfig(filename=log_filename, format="%(asctime)s.%(msecs)03d |:| %(levelname)s |:| %(message)s", level=logging.INFO, datefmt="%m/%d/%Y %H:%M:%S")
log = logging.getLogger()


# Retrieves the word from the Datamuse API to get the number of syllables.
def get_word_syllables(word: str) -> int:
    """Gets the syllable count of a word.

    :param (str) word: The word to get the syllables for.
    :return (int): The amount of syllables.
    """

    log.info(f"get_word_syllables: {word}")
    api = Datamuse()
    results = api.words(sl=word)
    log.info(f"API returned results: {results}")
    if list(filter(lambda x: x['word'] == word, results)):  # Check to see if the word itself is in the list.
        result = list(filter(lambda x: x['word'] == word, results))[0]
    else:  # get the word with the highest score.
        result = max(results, key=lambda x: x['score'])
    log.info(f"Selected: {result} {type(result)}")
    if result:
        return result['numSyllables']
    else:
        return 0


# Get the sentence's syllables
def get_sentence_syllables(sentences: str, format_option: int) -> list:
    """Gets the syllable count in a phrase, sentence, or group of lines.

    :param (str) sentences: The phrase, sentence, or group of lines to get the syllables for.
    :param (int) format_option: Whether we are encoding or decoding a string - to be passed into the format_api_sentence call.
    :return (list): Number of syllables per line/sentence.
    """

    syllables = list()
    log.info(f"get_sentence_syllables - Passed in the following:\n----\n{sentences}\n----")
    formatted_sentences = format_sentence(sentences, format_option)
    log.info(formatted_sentences, type(formatted_sentences))
    sentences = formatted_sentences.split("\n")
    for sentence in sentences:
        sentence_syllables = 0  # Initialize the sentence syllable counter
        log.debug(f"Sending the following sentence to Datamuse: \"{sentence}\"")
        for word in sentence.split():
            sentence_syllables += get_word_syllables(word)
        log.info(f"The sentence \"{sentence}\" has a total of {sentence_syllables} syllables.")
        syllables.append(sentence_syllables)
    return syllables


# Removes punctuation and changes any numeric number into the correct english word.
def format_sentence(sentence: str, option: int) -> str:
    """Formats a sentence to be sent to the Datamuse API.

    :param (str) sentence: The sentence we need to format.
    :param (int) option: Whether we are encoding (2) or decoding (1) a message.
    :return (str): The formatted sentence.
    """

    log.info(f"format_api_sentence - {option}: 1 = Decode, 2 = Encode")

    if option == 1:  # DECODE
        decode_punctuation = string.punctuation.replace("'", "").replace("-", "")  # required to not remove ' and - from the sentence.
        new_sentence = sentence.translate(str.maketrans('', '', decode_punctuation))  # remove any punctuation defined in decode_punctuation.
        for word in new_sentence.split(" "):
            if word.isnumeric():  # change numeric values into the english words.
                new_sentence = new_sentence.replace(word, num2words(word))
        return new_sentence.lower()
    elif option == 2:  # ENCODE
        new_sentence = sentence.translate(str.maketrans('', '', string.punctuation))  # remove all punctuation.
        for word in new_sentence.split(" "):
            if word.isnumeric():  # change numeric values into the english words.
                new_sentence = new_sentence.replace(word, num2words(word))
        return new_sentence.upper()


# Decodes a message.
def decode(input_message: str) -> str:
    """Decodes a message according to the codex on the system.

    :param (str) input_message: The message we want to decode.
    :return (str): The decoded message.
    """

    log.info("DECODING...")
    decoded_message = str()
    syllables_list = []
    spaces = []
    if not input_message or len(input_message) < 1:
        input_message = "haven't done it\n" \
                        "singularity.\n" \
                        "forty-five"

    input_message_list = [s for s in input_message.split("\n") if s.strip()]  # Create a list of the sentences provided.
    for ind, sentence in enumerate(input_message_list):
        sentence = sentence.rstrip("\r")
        if sentence.endswith("."):
            spaces.append(ind)
            sentence = sentence.rstrip(".")
        try:
            syllables_list.append(get_syllables_for_sentence(sentence))
        except IndexError:
            decoded_message = "Message could not be decoded."
    log.info(f"Decode sentence space positions: {spaces}")
    #print(f"decode syllables: {syllables_list}")

    # Get the corresponding letters according to the codex
    with open('codex.txt', encoding="utf8") as f:
        codex_lines = f.readlines()
        codex_list = [line.strip("\n") for line in codex_lines]
    log.debug(f"decode - Codex List: {codex_list}")
    if None in syllables_list:
        return "Message could not be decoded."
    for ind, num in enumerate(syllables_list):
        corrected_num = (num - 1 - offset) % 26
        log.debug(f"{num} syllables = {codex_list[corrected_num]}")
        if ind in spaces:
            decoded_message += codex_list[corrected_num] + " "
        else:
            decoded_message += codex_list[corrected_num]
    log.info("Returning decoded message.")
    return decoded_message


# Encodes a message
def encode(input_message: str) -> str:
    """Encodes a message according the codex on the system.

    :param (str) input_message: The message we want to encode.
    :return (str): The encoded message.
    """
    log.info("ENCODING.")
    syllables = list()
    spaces = list()
    encoded_message = str()
    words = list()

    if not input_message or len(input_message) < 1:
        input_message = "test message"

    # Format the message
    formatted_message = format_sentence(input_message, 2)

    # Get the corresponding letters according to the codex.
    with open('codex.txt') as f:
        codex_lines = f.readlines()
        codex_list = [line.strip("\n") for line in codex_lines]
    log.info(f"encode - Got the Codex: {codex_list}")

    # Get the syllables needed for each line of the encoded message.
    for i, c in enumerate(formatted_message):
        if c == " ":
            spaces.append(i - (1 + len(spaces)))
            continue
        syllables.append((codex_list.index(c) + 1 + offset) % 26)
    log.info(f"Encode sentence space positions: {spaces}")
    #print(f"formatted msg:{formatted_message}")

    # 1. get words for the syllable count of a line.
    for num in syllables:
        num = int(num)
        word = get_words_for_syllables(num)
        words.append(word)

    # 2. build the message.
    for ind, line in enumerate(words):
        #print(f"words, index line {ind} {line}")
        if ind in spaces:
            line = line + "."
        encoded_message = encoded_message + "\n" + line
    log.info("encode - Returning encoded message.")
    return encoded_message


def get_words_for_syllables(total_syllables: int) -> str:
    """Gets a word or words for a provided number of syllables.

    :param (int) total_syllables: The number of syllables needed to be fulfilled.
    :return (str): A space separated string of words.
    """

    log.info(f"get_words_for_syllables: {total_syllables}")
    # Use pandas to read the list of words to find a word to use.
    df = pd.read_csv('datasets/phoneticDictionary_cleaned_20230515.csv')
    syllables_used = 0
    words = ""

    # While we still have syllables to use, get another word.
    while syllables_used < total_syllables:
        log.info(f"Syllables used so far: {syllables_used}")

        # Create a dataframe for words with a syllable count compatible with the number of syllables left.
        df_matching_syllables = df.loc[df['syl'] <= (total_syllables - syllables_used)]

        # Get a random sample of rows from the dataframe.
        row = df_matching_syllables.sample()

        # Add the word to the return string.
        words += row['word'].values[0] + " "
        syllables_used += row['syl'].values[0]
    log.info(f"get_words_for_syllables - got words: {words}")
    return words.rstrip(" ")


def get_syllables_for_sentence(sentence: str) -> Union[int, None]:
    """Gets the syllable count for a sentence.

    :param (str) sentence: The sentence to get the syllables for.
    :return (int): The amount of syllables in the sentence.
    """

    log.info(f"get_syllables_for_sentence: \"{sentence}\" ")
    df = pd.read_csv('datasets/phoneticDictionary_cleaned_20230515.csv')
    words = sentence.lower().split(' ')
    syllables = 0

    for word in words:
        df_matching_word = df.loc[df['word'] == word]
        if df_matching_word.empty:
            return None
        syllables += df_matching_word['syl'].values[0]

    return syllables


def clean_dictionary():
    """Cleans the data in datasets/phoneticDictionary.csv and puts it into new_clean.csv

    This will remove words that start with an apostrophe, contain a period, or are contained in the list twice.
    Provides a clean dataset to use named "phoneticDictionary_cleaned_{date}.csv

    :return:
    """
    log.info('cleaning the dictionary.')
    new_filename = f"datasets/phoneticDictionary_cleaned_{datetime.datetime.now().strftime('%Y%m%d')}.csv"
    log.info(f"Cleaned Dictionary Name: {new_filename}")
    with open('datasets/phoneticDictionary.csv', 'r', encoding='utf8') as in_file, open(new_filename, 'w', encoding='utf8', newline='') as out_file:
        seen = set()
        reader = csv.DictReader(in_file)
        writer = csv.writer(out_file)

        writer.writerow(['id', 'word', 'phon', 'syl', 'start', 'end'])
        for row in reader:
            word = row['word']  # Get the word for the row

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


# Legacy function. Not currently in use.
def validate_word(word: str) -> bool:
    """Checks to ensure the word chosen is a valid word.

    Makes a request to the WordsAPI to see if the provided word returns a valid result.
    We are only allowed 2,500 requests per day for free.

    :param (str) word: The word to check
    :return (bool): True if the word is valid
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

    log.debug(f"Response/Status: {response.json()}, {response.status_code}")
    if response.status_code != 200:
        log.info('bad resp')
        return False
    else:
        log.info('good resp')
        return True


if __name__ == '__main__':
    log.info("Calling __main__")
    offset = 0  # Default: 0
    words_api_counter = 0
    print(encode("love pooping killers"))
    print(decode(encode("love pooping killers")))
