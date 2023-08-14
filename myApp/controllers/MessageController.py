import string
import pandas as pd
import csv
import requests
from datetime import datetime, date
from datamuse import Datamuse
from num2words import num2words
from typing import Union
import logging
import random
import time
# https://api.datamuse.com/words?sl=i%27ll
# https://wordsapiv1.p.rapidapi.com/words/aberration/syllables | This costs money after 2500 requests
# https://github.com/gmarmstrong/python-datamuse/
# https://www.datamuse.com/api/#md
#
# https://www.onelook.com/thesaurus/?s=&f_ns=6&sortby=le0&sorttopn=1000
# https://www.howmanysyllables.com

# Log file configuration
log_filename = "./logs/encode-message_" + datetime.now().strftime("%Y%m%d") + ".log"
logging.basicConfig(filename=log_filename, format="%(asctime)s.%(msecs)03d |:| %(levelname)s |:| %(message)s", level=logging.INFO, datefmt="%m/%d/%Y %H:%M:%S")
log = logging.getLogger()

syllable_dict = {}
word_dict = {}


# Create a dictionary from the syllable dataset
def load_data_dicts(filename="./myApp/datasets/phoneticDictionary_cleaned_20230515.csv"):
    """ Load the data dict from an external file.

    :return:
    """
    log.info("Creating syllable dictionary.")
    df = pd.read_csv(filename)
    for index, row in df.iterrows():
        w_syl = int(row['syl'])
        d_word = row['word']
        if w_syl not in syllable_dict:
            syllable_dict[w_syl] = []
        syllable_dict[w_syl].append(d_word)

        if d_word not in word_dict:
            word_dict[d_word] = w_syl


# Get the codex
with open('./myApp/codex.txt') as codex:
    codex_list = [line.strip() for line in codex]


# Retrieves the word from the Datamuse API to get the number of syllables.
def get_word_syllables(word: str) -> int:
    """Gets the syllable count of a word.

    :param (str) word: The word to get the syllables for.
    :return (int): The amount of syllables.
    """

    log.info(f"get_word_syllables: {word}")
    datamuse = Datamuse()
    results = datamuse.words(sl=word)
    log.info(f"API returned results: {results}")

    # Check to see if the word is in the list. If not, take the highest score.
    if list(filter(lambda x: x['word'] == word, results)):
        result = list(filter(lambda x: x['word'] == word, results))[0]
    else:
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
    :param (int) format_option: Whether we are encoding (2) or decoding (1) a string.
    :return (list): Number of syllables per line/sentence.
    """

    syllables = list()
    log.info(f"get_sentence_syllables - Passed in the following:\n----\n{sentences}\n----")
    formatted_sentences = format_sentence(sentences, format_option)
    log.info(formatted_sentences, type(formatted_sentences))
    sentences = formatted_sentences.split("\n")
    for sentence in sentences:
        sentence_syllables = 0
        log.debug(f"Sending the following sentence to Datamuse: \"{sentence}\"")
        for word in sentence.split():
            sentence_syllables += get_word_syllables(word)
        log.info(f"The sentence \"{sentence}\" has a total of {sentence_syllables} syllables.")
        syllables.append(sentence_syllables)
    return syllables


# Remove punctuation and change any numeric number into the correct english word.
def format_sentence(sentence: str, option: int) -> str:
    """Formats a sentence to be sent to the Datamuse API.

    :param (str) sentence: The sentence we need to format.
    :param (int) option: Whether we are encoding (2) or decoding (1) a message.
    :return (str): The formatted sentence.
    """

    log.info(f"format_api_sentence - {option}: 1 = Decode, 2 = Encode")

    if option == 1:  # DECODE
        decode_punctuation = string.punctuation.replace("'", "").replace("-", "")  # don't remove ' and - from the sentence.
        new_sentence = sentence.translate(str.maketrans('', '', decode_punctuation))  # remove any punctuation defined in decode_punctuation.
        for word in new_sentence.split(" "):
            if word.isnumeric():  # change numeric values into the english words.
                new_sentence = new_sentence.replace(word, num2words(word))
        return new_sentence.lower()
    elif option == 2:  # ENCODE
        new_sentence = sentence.translate(str.maketrans('', '', string.punctuation))  # remove all punctuation.
        for word in new_sentence.split(" "):
            if word.isnumeric():  # change numeric values into the english words.
                new_sentence = new_sentence.replace(word, num2words(word)).replace("-", " ")
        return new_sentence.upper().replace(",", "")


# Decode a message.
def decode(input_message: str) -> tuple:
    """Decodes a message according to the codex on the system.

    :param (str) input_message: The message we want to decode.
    :return (tuple): Element at index 0 is the response code: 0 - Bad, 1 - Good.
                        Element at index 1 is the response message.
    """
    start = time.time()
    log.info("DECODING...")

    # Check for any non-ascii characters.
    if any(not c.isascii() for c in input_message):
        error_message = "Only English is supported at this time. Your message contained non-ASCII characters."
        log.error(error_message)
        return 0, error_message

    input_message_list = [s for s in input_message.split("\n") if s.strip()]  # Create a list of the sentences provided.
    log.info(input_message_list)

    decode_offset = decode_offset_date(input_message_list.pop(0))
    if isinstance(decode_offset, str):
        return 0, f"Message could not be decoded. {decode_offset}"

    decoded_parts = []

    for sentence in input_message_list:
        if sentence.endswith("."):
            sentence = sentence.rstrip(".")
            decoded_parts.append(get_decoded_sentence(sentence, decode_offset) + " ")
        else:
            decoded_parts.append(get_decoded_sentence(sentence, decode_offset))

    decoded_message = ''.join(decoded_parts)
    log.info(f"Returning decoded message in {(time.time()-start) * 10**3} ms:\n{decoded_message}")
    return 1, decoded_message


def get_decoded_sentence(sentence: str, decode_offset: int) -> str:
    """ Decode a single sentence.

    :param (str) sentence: The sentence to decode.
    :param (str) decode_offset: The offset to use.
    :return (str): The decoded sentence.
    """
    try:
        syllables = get_syllables_for_sentence(sentence)
        corrected_num = (syllables - 1 - decode_offset) % 26
        return codex_list[corrected_num]
    except IndexError:
        return ""


# Encodes a message
def encode(input_message: str, encode_offset: int) -> tuple:
    """Encodes a message according to the codex on the system.

    :param (str) input_message: The message we want to encode.
    :param (int) encode_offset: The message offset used to encode.
    :return (tuple): A tuple containing an integer status code (0 for failure, 1 for success) and the encoded message.
    """
    start = time.time()
    log.info("ENCODING.")

    # Ensure input_message is not empty
    if not input_message:
        input_message = "test message"

    encoded_message = build_offset_date(encode_offset)

    formatted_message = format_sentence(input_message, 2)
    log.info(f"Formatted Message: {formatted_message}")

    # Check for any non-ascii characters.
    if any(not c.isascii() for c in formatted_message):
        error_message = "Only English is supported at this time. Your message contained non-ASCII characters."
        log.error(error_message)
        return 0, error_message

    spaces = [i - (1 + sum(1 for char in formatted_message[:i] if char == " ")) for i, c in enumerate(formatted_message) if c == " "]

    syllables = [(codex_list.index(c) + 1 + encode_offset) % 26 or 26 for c in formatted_message.replace(" ", "")]

    words = [get_words_for_syllables(int(num)) for num in syllables]

    lines = []
    for ind, line in enumerate(words):
        if ind in spaces:
            line = line + "."
        lines.append(line)

    encoded_message += "\n" + "\n".join(lines)
    log.info(f"Returning encoded message in {(time.time()-start) * 10**3} ms:\n{encoded_message}")
    return 1, encoded_message


def get_words_for_syllables(total_syllables: int) -> str:
    """Gets a word or words for a provided number of syllables.

    :param (int) total_syllables: The number of syllables needed to be fulfilled.
    :return (str): A space separated string of words.
    """
    log.info(f"get_words_for_syllables: {total_syllables}")

    words = []

    while total_syllables > 0:
        available_syllables = [syl for syl in syllable_dict if syl <= total_syllables]
        if not available_syllables:
            break
        chosen_syl = random.choice(available_syllables)
        chosen_word = random.choice(syllable_dict[chosen_syl])
        words.append(chosen_word)
        total_syllables -= chosen_syl

    result = ' '.join(words)
    log.info(f"get_words_for_syllables - got words: {result}")
    return result


def get_syllables_for_sentence(sentence: str) -> Union[int, None]:
    """Gets the syllable count for a sentence.

    :param (str) sentence: The sentence to get the syllables for.
    :return (int|None): The amount of syllables in the sentence.
    """
    log.info(f"get_syllables_for_sentence: \"{sentence}\"")

    syllables = 0

    for word in sentence.lower().split(' '):
        if word in word_dict.keys():
            syllables += word_dict[word]
        else:
            return None

    return syllables


# noinspection PyTypeChecker
def clean_data_file():
    """Cleans the data in datasets/phoneticDictionary.csv and puts it into new_clean.csv

    This will remove words that start with an apostrophe, contain a period, or are contained in the list twice.
    Provides a clean dataset to use named "phoneticDictionary_cleaned_{date}.csv

    :return:
    """
    log.info('cleaning the dictionary.')
    new_filename = f"./myApp/datasets/phoneticDictionary_cleaned_{datetime.now().strftime('%Y%m%d')}.csv"
    log.info(f"Cleaned Dictionary Name: {new_filename}")
    with open('./myApp/datasets/phoneticDictionary.csv', 'r', encoding='utf8') as in_file, open(new_filename, 'w', encoding='utf8', newline='') as out_file:
        seen = set()
        reader = csv.DictReader(in_file)
        writer = csv.writer(out_file)

        writer.writerow(['id', 'word', 'phon', 'syl', 'start', 'end'])
        for line in reader:
            word = line['word']  # Get the word for the line

            if word in seen or word.startswith("'") or "." in word:
                continue

            writer.writerow([line['id'], line['word'], line['phon'], line['syl'], line['start'], line['end']])
            seen.add(word)


# Legacy function. Not currently in use.
def validate_word(word: str) -> bool:
    """Checks to ensure the word chosen is a valid word.

    Makes a request to the WordsAPI to see if the provided word returns a valid result.
    We are only allowed 2,500 requests per day for free.

    :param (str) word: The word to check.
    :return (bool): True if the word is valid.
    """

    url = f"https://wordsapiv1.p.rapidapi.com/words/{word}/syllables"

    with open('./credentials.txt', 'r', encoding="utf8") as f:
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


def build_offset_date(int_offset: int) -> str:
    """Builds a date string for the beginning of the encoded message to communicate the offset.

    The offset is represented in the date by the day - month.

    :param (int) int_offset: The integer offset value.
    :return: (str): The date portion of the encoded message.
    """
    if not isinstance(int_offset, int) or int_offset < 0:
        return "Offset must be an integer less than 26 and greater than or equal to 0."

    date_msg = None
    while date_msg is None:
        int_month = random.randint(1, 12)
        int_day = int_offset + int_month
        if int_day < 1 or int_day > 31:
            log.info(f"build_offset_date: bad date - month:{int_month}, day:{int_day}")
        elif (int_month == 2 and int_day > 29) or (int_month in [4, 6, 9, 11] and int_day > 30) or (int_month in [1, 3, 5, 7, 8, 10, 12] and int_day > 31):
            log.info(f"build_offset_date: bad date - month:{int_month}, day:{int_day}")
        else:
            date_msg = date(date.today().year, int_month, int_day).strftime("%A, %B %d, %Y")
            log.info(f"build_offset_date: good date - {date_msg}")
    return str(date_msg)


def decode_offset_date(offset_date: str) -> Union[int, str]:
    """Calculates the message offset of the encoded message.

    :param offset_date: The date string that is the first line of the encoded message.
    :return: (int) or (str): The integer offset, or a message if the integer offset could not be calculated.
    """
    try:
        log.info(f"decode_offset_date: param \"offset_date\" - {datetime.strptime(offset_date, '%A, %B %d, %Y')}")
        dt = datetime.strptime(offset_date, '%A, %B %d, %Y')
    except ValueError:
        return "The message must begin with a date following this format: Monday, January 1, 1990"
    return dt.day - dt.month


if __name__ == '__main__':
    log.info("Calling __main__")
    words_api_counter = 0
