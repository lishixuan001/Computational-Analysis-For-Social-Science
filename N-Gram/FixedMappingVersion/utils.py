import os
from os import listdir
from os.path import isfile, join

import re
import sys
import time
from collections import Counter

import pandas as pd
import numpy as np

import csv
import zipfile

import sqlite3
import pickle

import logging
import argparse
import datetime
import sys



######################################################
#                    Load Arguments                  #
######################################################


def load_args():
    """
    [Data Generation]
    Load arguments from user command input [attributes for data management]
    :return: parsed arguments
    """
    mnist_data_path = '../mnistPC'
    parser = argparse.ArgumentParser()
    parser.add_argument("--file_set_id",
                        help="File set to analyze",
                        default="000",
                        type=str,
                        required=True)
    parser.add_argument("--cpu_count",
                        help="Number of CPUs used for Mapping",
                        default=8,
                        type=int,
                        required=False)
    parser.add_argument("--log_batch",
                        help="Batch size for logging progress",
                        default=100,
                        type=int,
                        required=False)
    parser.add_argument("--db_reset",
                        help="Drop and re-Init Table in Database",
                        default=False,
                        type=bool,
                        required=False)
    args = parser.parse_args()
    return args



######################################################
#                Environment Variables               #
######################################################

"""
Paths for Dictionaries
"""
dictionary_root = "./Dictionaries"
dictionary_path = {}
dictionary_name_list = [
    "Culture",
    "Demographic",
    "Relational",
]

for dictionary_name in dictionary_name_list:
    dictionary_path[dictionary_name] = join(dictionary_root, dictionary_name + ".csv")

"""
Paths for Articles
"""
zip_articles_root = "../Soc_MGT_OB_1980_2018"
extracted_articles_root = "../ExtractedZipFiles"

"""
File ID Iteration
"""
standard_folder = "metadata"
ngram_types = ["ngram1", "ngram2", "ngram3"]

"""
Load file ID differences
"""
with open("./df_diffs_sum.gz", "rb") as df_diffs_file:
    df_diffs_sum = pickle.load(df_diffs_file)



######################################################
#                   Default Methods                  #
######################################################


def setup_logger(name):
    now = datetime.datetime.now().strftime('%Y-%m-%d-%H:%M:%S')
    formatter = logging.Formatter(fmt='%(asctime)s %(levelname)-8s %(message)s',
                                  datefmt='%Y-%m-%d %H:%M:%S')
    handler = logging.FileHandler('log/{}.log'.format(now), mode='w')
    handler.setFormatter(formatter)

    screen_handler = logging.StreamHandler(stream=sys.stdout)
    screen_handler.setFormatter(formatter)

    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)
    logger.addHandler(handler)
    logger.addHandler(screen_handler)
    
    return logger


"""
Get name of an object
"""
def namestr(obj, namespace):
    return [name for name in namespace if namespace[name] is obj]

"""
Display with format
"""
def display(items, func=None, limit=None):
    # Print Variable Name
    print(namestr(items, globals()))
    # Print Content
    count = 0
    for item in items:
        # Consider Limit
        if limit is not None and count >= limit:
            return
        # Consider Exerted Function
        if func:
            item = func(item)
        # Print Each Item
        print("     {0}".format(item))
        count += 1


def report_progress(progress, total, avg_time='', lbar_prefix = '', rbar_prefix=''):
    percent = round(progress / float(total) * 100, 2)
    buf = "{0}|{1}| {2}{3}/{4} {5}% [{6}]".format(lbar_prefix, ('#' * round(percent)).ljust(100, '-'),
        rbar_prefix, progress, total, percent, avg_time)
    sys.stdout.write(buf)
    sys.stdout.write('\r')
    sys.stdout.flush()
    

    
######################################################
#                  File System Check                 #
######################################################


""" 
Assert the filename in format "receipt-id-989431-part-001"
where XXX stands for article set number
"""
def valid_file_set(filename):
    return re.match("^receipt-id-989431-part-(.+)$", filename)


""" Define function getting article set ID by the zip-file-name
Pattern: receipt-id-989431-part-XXX.zip
"""
def parse_article_set_id(filename):
    id_number_lst = re.findall("receipt-id-989431-part-(.+)$", filename)
    if len(id_number_lst) == 1:
        return id_number_lst[0]
    print("Parse_ID Error: Filename does not match pattern. ")
    return None



""" Define function getting article ID by the file-name
Pattern: journal-article-10.1086_210007-ngram1.txt
"""
def parse_article_id(filename):
    id_number_lst = re.findall("journal-article-(.+)-+", filename)
    if len(id_number_lst) == 1:
        return id_number_lst[0]
    id_number_lst = re.findall("journal-article-(.+)\.+", filename)
    if len(id_number_lst) == 1:
        return id_number_lst[0]
    print("Parse_ID Error: Filename does not match pattern. ")
    return None



def create_dictionary_dataframe():
    """
    Data
    """
    data = []

    # Iterate Through All Dictionaries
    for subject_path_pair in dictionary_path.items():
        # (Subject, Path) -> ('Culture', './Culture.csv')
        subject, path = subject_path_pair[0], subject_path_pair[1]
        # Iterate Through All Words In The Dictionary
        # Load The .CSV File
        with open(path, encoding='ISO-8859-1') as csv_file:
            # Define A Line In Data -> [subject, n-gram, words]
            dataline = []
            # We Do Not Split In Case When There're Multiple Words In A Row
            # Since We Store Words As One String In DataFrame
            rows = csv.reader(csv_file)
            for row in rows:
                n_number = len(row)
                if n_number <= 0:
                    continue
                words = " ".join(row)
                ngram_type = "ngram{n_number}".format(n_number=n_number)
                dataline = [subject, ngram_type, words]
                data.append(dataline)

    """
    Columns
    """
    columns = ["Subject", "N-Gram", "Words"]

    """
    Index
    """
    index = list(range(len(data)))

    """
    DataFrame
    """
    dataframe = pd.DataFrame(data, columns=columns, index=index)
    
    return dataframe


"""
For every file in ngram1/ folder, check the filename validity, 
extract the article ID, then search if same ID exist in ngram2/3 folders
- Expected filename format: journal-article-10.2307_00000000-ngram1.txt
@return: {article_id : [T/F, T/F, T/F]}
"""
def filter_by_filename(files_list):
    filtered_list = {}
    for filename in files_list:
        assert isinstance(filename, str)
        if filename.startswith("metadata"):
            continue
        # Get n_number
        n_number = int(re.findall("^ngram(.)/", filename)[0])
        # Check if the filename starts with "journal-article"
        filename = filename[len("ngram" + str(n_number) + "/"):]
        if not filename.startswith("journal-article"):
            continue
        # Get article id
        article_id = parse_article_id(filename)
        if article_id in filtered_list.keys():
            filtered_list[article_id][n_number - 1] = True
        else:   
            # Initialize existence
            existence = [False] * 3
            existence[n_number - 1] = True
            filtered_list[article_id] = existence
            
    return filtered_list
    

    
    
######################################################
#                Analysis Management                 #
######################################################


# Functions checking word attributes (single-letter, starts/ends with numebr)
def is_single_letter(word):
    assert isinstance(word, str)
    return len(word) <= 1

def starts_with_number(word):
    assert isinstance(word, str)
    try:
        return word[0].isdigit()
    except:
        return False

def ends_with_number(word):
    assert isinstance(word, str)
    try:
        return word[len(word) - 1].isdigit()
    except:
        return False

# Summary of check functions
check_funcs = [
    is_single_letter, 
    starts_with_number, 
    ends_with_number,
]



"""
@return: [["word1 word2 word3", 5], ["word4 word5 word6", 2], ...]
         freq_list containing all words (all-n-gram) with corresponding freq
"""
def get_freq_list(file_path):
    
    with open(file_path, mode="r", encoding="utf-8") as article_open:

        # Initiate freq_list -> [[words0, freq0], [words1, freq1]]
        freq_list = []

        # Read By Lines
        for line in article_open:
            
            # pair -> "["word1", "word2", "word3", "5"]
            pair = line.strip().split()
            assert len(pair) >= 2

            # Separate word/freq
            words, freq = pair[:-1], pair[-1]
            assert freq.isdigit()
            
            check_words = [check_func(word) for word in words for check_func in check_funcs]
            
            if any(check_words):
                continue

            # Words -> "word1 word2 word3"
            words = " ".join(words)

            # Append new pair to freq_list
            freq_list.append([words, freq])
    
    return freq_list


def filter_file_ids(file_ids, loaded_ids, file_set_id):
    # Resume history loading
    if len(loaded_ids) > 0:
        for loaded_id in loaded_ids:
            file_ids.remove(loaded_id)

    # Remove banned file_ids
    banned_ids = df_diffs_sum[df_diffs_sum["set_id"]==file_set_id]["np_diff_ids"].tolist()[0].tolist()
    for banned_id in banned_ids:
        file_ids.remove(banned_id)
        
    return file_ids
    
######################################################
#                Database Interactions               #
######################################################

def clear_db_table(logger, db_root, db_name):
    # Connect to the database "map_result_000.db"
    conn = sqlite3.connect(join(db_root, db_name))
    # Create Cursor object so that we can execute SQL commands
    cur = conn.cursor()
    try:
        # Clear Table
        clear_table = "drop table map_result"
        cur.execute(clear_table)
        conn.commit()
        logger.info("Table Dropped")
        
    except Exception as e:
        logger.warning("[Exception] => [{}]".format(e))
    
    cur.close()
    conn.close()
    
    
def init_db_table(logger, db_root, db_name):
    # Connect to the database "map_result_000.db"
    conn = sqlite3.connect(join(db_root, db_name))
    # Create Cursor object so that we can execute SQL commands
    cur = conn.cursor()
    # Create table
    create_table = 'create table if not exists map_result ' \
        '(set_id text, file_id text, ' \
        'n1_culture real, n1_demographic real, n1_relational real, ' \
        'n2_culture real, n2_demographic real, n2_relational real, ' \
        'n3_culture real, n3_demographic real, n3_relational real, ' \
        'culture_rate real, demographic_rate real, relational_rate real, classification text) '
    cur.execute(create_table)

    # Commit the changes and close
    conn.commit()
    cur.close()
    conn.close()
    logger.info("Table Init Success")


def get_loaded_article_ids(logger, db_root, db_name):
    
    logger.info("Connecting to DB")
    
    # Connect to the database "map_result_000.db"
    conn = sqlite3.connect(join(db_root, db_name))
    # Create Cursor object so that we can execute SQL commands
    cur = conn.cursor()
    # Select all data entries from the table 
    cur.execute('SELECT file_id FROM map_result')
    # Display all data collected
    database_collection = cur.fetchall()
    
    loaded_ids = list()
    if len(database_collection) > 0:
        loaded_ids = [data_collection[0] for data_collection in database_collection]

        if len(loaded_ids) != len(set(loaded_ids)):
            logger.info("--> Duplicates Detected in DB, Cleaning Up")
            
            for file_id in set(loaded_ids):
                loaded_ids.remove(file_id)
            num_duplicates = len(loaded_ids)
            
            for file_id in loaded_ids:
                cur.execute("DELETE FROM map_result WHERE file_id=(?)", (file_id,))

            cur.execute('SELECT file_id FROM map_result')
            database_collection = cur.fetchall()
            loaded_ids = [data_collection[0] for data_collection in database_collection]
            
            assert len(loaded_ids) == len(set(loaded_ids))
            
            logger.info("--> Cleaned Up Duplicates [{}], Remaining [{}]".format(num_duplicates, len(loaded_ids)))
    

    # Close the cursor and the database
    conn.commit()
    cur.close()
    conn.close()
    
    return loaded_ids



