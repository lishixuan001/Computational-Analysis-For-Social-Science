
# coding: utf-8

# In[10]:


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

import re
import sys
import time
from collections import Counter

import csv
import zipfile
import pickle


# In[11]:


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


# In[12]:


"""
Report Progress
"""
def report_progress(progress, total, avg_time='', lbar_prefix = '', rbar_prefix=''):
    percent = round(progress / float(total) * 100, 2)
    buf = "{0}|{1}| {2}{3}/{4} {5}% [{6}]".format(lbar_prefix, ('#' * round(percent)).ljust(100, '-'),
        rbar_prefix, progress, total, percent, avg_time)
    sys.stdout.write(buf)
    sys.stdout.write('\r')
    sys.stdout.flush()


# In[13]:


db_root = "./map_results"
new_db_root = "./new_results"

db_name_list = list()
for db_name in listdir(db_root):
    db_name_list.append(db_name)

db_columns = ["set_id", "file_id", 
               "ngram1_culture", "ngram1_demographic", "ngram1_relational", 
               "ngram2_culture", "ngram2_demographic", "ngram2_relational", 
               "ngram3_culture", "ngram3_demographic", "ngram3_relational", 
               "culture_rate", "demographic_rate", "relational_rate", 
               "classification"]

new_columns = ["set_id", "file_id", 
               "n1_culture", "n1_demographic", "n1_relational", "n1_article",
               "n2_culture", "n2_demographic", "n2_relational", "n2_article",
               "n3_culture", "n3_demographic", "n3_relational", "n3_article",
               "culture_count", "demographic_count", "relational_count", "article_count"]

ngram_types = ["ngram1", "ngram2", "ngram3"]

extracted_articles_root = "../ExtractedZipFiles"

class_types = ["culture", "demographic", "relational"]

# display(sorted(db_name_list))


# In[14]:


def load_db(db_name):
    conn = sqlite3.connect(join(db_root, db_name))
    cur = conn.cursor()
    cur.execute('SELECT * FROM map_result')
    data = cur.fetchall()
    cur.close()
    conn.close()
    index = list(range(len(data)))
    df_database = pd.DataFrame(data, columns=db_columns, index=index)
    return df_database


# In[15]:


"""
@return: [["word1 word2 word3", 5], ["word4 word5 word6", 2], ...]
         freq_list containing all words (all-n-gram) with corresponding freq
"""
def get_article_lines(file_path):
    try:
        with open(file_path, mode="r", encoding="utf-8") as article_open:
            return len(article_open.readlines())
    except Exception as e:
        print("Error Reading File [{}] \nException: [{}]".format(file_path, e))


# In[16]:


def init_db_table(db_name):
    
    # Connect to the database "map_result.db"
    conn = sqlite3.connect(join(new_db_root, db_name))
    # Create Cursor object so that we can execute SQL commands
    cur = conn.cursor()
    # Create table
    create_table = 'create table if not exists map_result '         '(set_id text, file_id text, '         'n1_culture real, n1_demographic real, n1_relational real, n1_article real, '         'n2_culture real, n2_demographic real, n2_relational real, n2_article real, '         'n3_culture real, n3_demographic real, n3_relational real, n3_article real, '         'culture_count real, demographic_count real, relational_count real, article_count real) '
    cur.execute(create_table)

    # Commit the changes and close
    conn.commit()
    cur.close()
    conn.close()


# In[7]:


def update_db(db_id):
    
    db_name = "map_result_{}.db".format(db_id)
    new_db_name = "map_results_{}.db".format(db_id)
    
    print("Start Updating DB: {}".format(db_id))
    
    conn = sqlite3.connect(join(new_db_root, new_db_name))
    cur = conn.cursor()
    
    df_database = load_db(db_name)
    data = []
    total = df_database.shape[0]
    for index, row in df_database.iterrows():
        dataline = []
        set_id = row["set_id"]
        file_id = row["file_id"]
        dataline.append(set_id)
        dataline.append(file_id)
        
        init_db_table(new_db_name)
        
        if file_id in get_loaded_article_ids(new_db_name):
            continue

        article_file_set_name = "receipt-id-989431-part-{set_id}".format(set_id=set_id)
        file_set_path = join(extracted_articles_root, article_file_set_name)

        for ngram_type in ngram_types:
            folder_path = join(file_set_path, ngram_type)
            file_name = "journal-article-{file_id}-{ngram_type}.txt".format(file_id=file_id, 
                                                                              ngram_type=ngram_type)
            file_path = join(folder_path, file_name)
            num_article_lines = get_article_lines(file_path)
            ngram_info = [int(row["_".join([ngram_type, class_type])] * num_article_lines) 
                          for class_type in class_types]
            ngram_info.append(num_article_lines)
            dataline.extend(ngram_info)
        # Sum Culture/Demographics/Relational Count
        dataline.append(dataline[2] + dataline[6] + dataline[10])
        dataline.append(dataline[3] + dataline[7] + dataline[11])
        dataline.append(dataline[4] + dataline[8] + dataline[12])
        dataline.append(dataline[5] + dataline[9] + dataline[13])
        data.append(dataline)
        report_progress(index, total)

        insert_value = "insert into map_result values ('{set_id}', '{file_id}', "                            "{n1_culture}, {n1_demographic}, {n1_relational}, {n1_article}, "                            "{n2_culture}, {n2_demographic}, {n2_relational}, {n2_article}, "                            "{n3_culture}, {n3_demographic}, {n3_relational}, {n3_article}, "                            "{culture_count}, {demographic_count}, {relational_count}, "                            "'{article_count}')".format(set_id=dataline[0], file_id=dataline[1], 
                                                         n1_culture=dataline[2], n1_demographic=dataline[3], 
                                                         n1_relational=dataline[4], n1_article=dataline[5], 
                                                         n2_culture=dataline[6], n2_demographic=dataline[7], 
                                                         n2_relational=dataline[8], n2_article=dataline[9],
                                                         n3_culture=dataline[10], n3_demographic=dataline[11], 
                                                         n3_relational=dataline[12], n3_article=dataline[13],
                                                         culture_count=dataline[14], demographic_count=dataline[15],
                                                         relational_count=dataline[16], article_count=dataline[17])
        cur.execute(insert_value)
        conn.commit()

    cur.close()
    conn.close()
            

            
def get_loaded_article_ids(db_name):
   
    # Connect to the database "map_result_000.db"
    conn = sqlite3.connect(join(new_db_root, db_name))
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
            print("--> Duplicates Detected in DB, Cleaning Up")
            
            for file_id in set(loaded_ids):
                loaded_ids.remove(file_id)
            num_duplicates = len(loaded_ids)
            
            for file_id in loaded_ids:
                cur.execute("DELETE FROM map_result WHERE file_id=(?)", (file_id,))

            cur.execute('SELECT file_id FROM map_result')
            database_collection = cur.fetchall()
            loaded_ids = [data_collection[0] for data_collection in database_collection]
            
            assert len(loaded_ids) == len(set(loaded_ids))
            
            print("--> Cleaned Up Duplicates [{}], Remaining [{}]".format(num_duplicates, len(loaded_ids)))
    

    # Close the cursor and the database
    conn.commit()
    cur.close()
    conn.close()
    
    return loaded_ids



update_db("008")

