import os
from os import listdir
from os.path import isfile, join

import pandas as pd
import numpy as np

import time
import errno
import sqlite3
import logging

import multiprocessing
from utils import *


######################################################
#                Environment Variables               #
######################################################

"""
Article Set List & Load Dictionary 
"""
# Get filtering results
# articles_file_set_list = sorted([filename for filename in os.listdir(extracted_articles_root) if valid_file_set(filename)])

# Load dictionary
dataFrame_dictionary = create_dictionary_dataframe()
# Set up logger
logger = setup_logger("Mapping")
    
    

######################################################
#                 Mapping Operations                 #
######################################################

"""
Mapping words in the freq_list to the dictionaries and get the match rates
@return: [Culture_Rate, Demographic_Rate, Relational_Rate]
"""
def get_mapping_rate(file_path, ngram_type):
    """
    :param file_path: complete directory path of the file
    :param ngram_type: "ngram1" /OR/ "ngram2" /OR/ "ngram3"
    :return: Mapping_Rates, Success => [Culture_Rate, Demographic_Rate, Relational_Rate], True
                                    => [None, None, None], False
    """
    
    try:
        # If filepath does not exist
        if not isfile(file_path):
            raise FileNotFoundError(errno.ENOENT, os.strerror(errno.ENOENT), file_path)
        
        # Get frequent list
        freq_list = get_freq_list(file_path)
    

        # Initialize the match_counts => {"Culture" : 0, ...} 
        match_counts = {}
        for subject in dictionary_name_list:
            match_counts[subject] = 0

        # Iterate Through Each Word In freq_list 
        # -> [["word1 word2 word3", freq],ssh  ...]
        for words_freq_pair in freq_list:
            words, freq = words_freq_pair

            # Check Through Every Subject Dictionary
            for subject in dictionary_name_list:
                selected_dictionary = dataFrame_dictionary[(dataFrame_dictionary['Subject'] == subject) & 
                                              (dataFrame_dictionary['N-Gram'] == ngram_type)]
                if selected_dictionary['Words'].str.contains(words).any():
                    match_counts[subject] += 1

        match_rates = [
            match_counts["Culture"] / len(freq_list),
            match_counts["Demographic"] / len(freq_list),
            match_counts["Relational"] / len(freq_list),
        ]
        
        return match_rates, True
        
    except Exception as e:
        return e, False


def manage_file(file_id, file_set_id, file_set_path):

    dataline = []
    dataline.append(file_set_id)
    dataline.append(file_id)

    # Iterate through all folders
    # -> ["ngram1", "ngram2", "ngram3"]
    cdr_rates = list([0, 0, 0])
    for ngram_type in ngram_types:
        folder_path = join(file_set_path, ngram_type)

        file_name = "journal-article-{file_id}-{ngram_type}.txt".format(file_id=file_id, 
                                                                          ngram_type=ngram_type)
        file_path = join(folder_path, file_name)

        # culture_rate, demographic_rate, relational_rate = [0.15, 0.093, 0.125]
        cdr_ngram_rates, success = get_mapping_rate(file_path, ngram_type) 
        if success:
            cdr_rates = [sum(pair) for pair in zip(cdr_rates, cdr_ngram_rates)]
        else:
            logger.warning("[Exception] => [{message}] - "\
                           "[FileSetID: {file_set_id}], [FileID: {file_id}]".format(message=cdr_ngram_rates,
                                                                                    file_set_id=file_set_id,
                                                                                    file_id=file_id,
                                                                                    ngram_type=ngram_type))
            return None
        dataline.extend(cdr_ngram_rates)
    # Add general prediction probabilities
    dataline.extend(cdr_rates)

    # Get prediction
    prediction = dictionary_name_list[cdr_rates.index(max(cdr_rates))]
    dataline.append(prediction)

    return dataline

    
"""
The function runs the mapping algorithm and stores every result into the database
@param break_point: the article_id of the last article the last time we finished running the function
"""
def create_mapping_operation(article_file_set_name, loaded_ids=[], cpu_count=8, log_batch=100):
    
    # Connect to the database "map_result_000.db"
    conn = sqlite3.connect(join(db_root, db_name))
    # Create Cursor object so that we can execute SQL commands
    cur = conn.cursor()
    
    logger.info("Processing Mapping")

    # In case of non-closing database cursor which left db open
    try:
        # Extract Data Set ID
        # -> "014"
        file_set_id = parse_article_set_id(article_file_set_name)
        file_set_path = join(extracted_articles_root, article_file_set_name)

        logger.info("Loading File Set: [{file_set_id}]".format(file_set_id=file_set_id))

        # Get file IDs from "metadata" folder
        # -> ["10.1086_210007", "10.1086_1038856", ...]
        file_ids = [parse_article_id(filename) for filename in listdir(join(file_set_path, standard_folder))]
        file_ids = filter_file_ids(file_ids, loaded_ids, file_set_id)

        num_loaded = len(loaded_ids)
        if num_loaded > 0:
            logger.info("--> Detect Loaded [{num_loaded}], Resume Mapping".format(num_loaded=num_loaded))

        logger.info("Async Processing")

        # Init for multiprocessing 
        pool = multiprocessing.Pool(cpu_count)
        results = [pool.apply_async(manage_file, (file_id, file_set_id, file_set_path)) for file_id in file_ids]

        start = time.time()
        count, batch_count = 0, 1

        logger.info("Collecting Results")
        for result in results:

            dataline = result.get()
            if dataline is None:
                continue

            # Write the dataline into the database
            insert_value = "insert into map_result values ('{set_id}', '{file_id}', "\
                            "{n1_culture}, {n1_demographic}, {n1_relational}, "\
                            "{n2_culture}, {n2_demographic}, {n2_relational}, "\
                            "{n3_culture}, {n3_demographic}, {n3_relational}, "\
                            "{culture_rate}, {demographic_rate}, {relational_rate}, "\
                            "'{classification}')".format(set_id=dataline[0], file_id=dataline[1], 
                                                         n1_culture=dataline[2], n1_demographic=dataline[3], 
                                                         n1_relational=dataline[4], n2_culture=dataline[5], 
                                                         n2_demographic=dataline[6], n2_relational=dataline[7],
                                                         n3_culture=dataline[8], n3_demographic=dataline[9], 
                                                         n3_relational=dataline[10], culture_rate=dataline[11], 
                                                         demographic_rate=dataline[12], relational_rate=dataline[13], 
                                                         classification=dataline[14])
            cur.execute(insert_value)
            conn.commit()

            # Update Progress
            count += 1
            avg_time = (time.time() - start) / count
            if count == batch_count * log_batch:
                batch_count += 1
                logger.info("--> Processed: {count}; Average Time: {avg_time}".format(count=count+num_loaded,
                                                                                  avg_time=avg_time))

            # Progress Bar
            # report_progress(count + num_loaded, total, avg_time)

                
    except Exception as e:
        print("Error Message: {}\n".format(e))
        cur.close()
        conn.close()
        return
        
    # Close the database and cursor
    cur.close()
    conn.close()
    
    return

        

if __name__ == "__main__":
    # Load Arguments
    args = load_args()
    
    # Define File Set
    file_set_id = args.file_set_id
    article_file_set_name = "receipt-id-989431-part-{}".format(file_set_id)
    
    # Path for database
    db_root = "./map_results"
    db_name = "map_result_{}.db".format(file_set_id)
    
    # Check if reset table in db
    if args.db_reset:
        permission_code = input("Please input authorization code: ")
        if permission_code == "jstor":
            clear_db_table(logger, db_root, db_name)
            init_db_table(logger, db_root, db_name)
    
    # Get loaded ids
    loaded_ids = get_loaded_article_ids(logger, db_root, db_name)
    
    # Mapping 
    create_mapping_operation(article_file_set_name=article_file_set_name,
                             loaded_ids=loaded_ids, 
                             cpu_count=args.cpu_count,
                             log_batch=args.log_batch)
    
