# Computational Analysis of Social Science Research
> Dictionary Mapping based Bag Of Words text analysis for social sciences documents

## 1 Project Layout
```
Project
│   
│   README.md
│   Project_Background_and_Overview.pdf
│   
└───Dictionary Mapping/
│   └───.ipynb_checkpoints/
│   └───__pycache__/
│       │   utils.cpython-36.pyc
│       │   
│   └───Dictionaries/
│       │   Culture.csv
│       │   Demographic.csv
│       │   Relational.csv
│       │   
│   └───N-Gram/
│       │   Mapping.py
│       │   utils.py
│       │   update_map_result.py
│       │   visualization.py
│       │   CheckDatabase.py
│       │   DatabaseManagement.ipynb
│       │   FileExtraction.ipynb
│       │   FilesCheck.ipynb
│       │   command.txt
│       │   
│   └───MetaData/
│       │   ParseMetaFiles.ipynb
│       │   fixed-xml-decode-access-zip-no-uncompress-new1.ipynb
│       │   journal titles & subjects 10-15 edited.csv
│       │   match_titile.ipynb
│       │   
│   └───engagement_results/
│       │   engagement_results_001.db
│       │   engagement_results_002.db
│       │   ...
│       │   engagement_results_014.db
│       │   
│   └───map_results/
│       │   map_results_001.db
│       │   map_results_002.db
│       │   ...
│       │   map_results_014.db
│       │   
│   └───metadata_results/
│       │   merged.pickle
│       │   part1.pickle
│       │   part2.pickle
│       │   ...
│       │   part14.pickle
│       │   
│   └───imgs/
│       │   avg_rate.png
│       │   
│   └───log/
│       │   2019-02-23-08:29:12.log
│       │   2019-02-23-09:01:24.log
│       │   ...
│   
└───Stats Learned Mapping/
│   └───.ipynb_checkpoints/
│       │   ...
│   └───Results_1/
│       │   journal-article-10.2307_145203-ngram1.txt
│       │   journal-article-10.2307_145208-ngram1.txt
│       │   ...
│       │   
│   └───Results_2/
│       │   journal-article-10.2307_145203-ngram2.txt
│       │   journal-article-10.2307_145208-ngram2.txt
│       │   ...
│       │   
│   └───Results_3/
│       │   journal-article-10.2307_145203-ngram3.txt
│       │   journal-article-10.2307_145208-ngram3.txt
│       │   ...
│       │   
│   │   Management-1-Uncompress.ipynb
│   │   Management-2-Uncompress.ipynb
│   │   Management-3-Uncompress.ipynb
│   │   Management-1-SQLite.ipynb
│   │   Map_Ngram_1.ipynb
│   │   Merge_Info.ipynb
│   │   journals.zip
│   │   ngram.db
│   
└───WordEmbedding/
    └───HuffmanEncoding/
        │   Huffman_Encoding.py
        │   
    └───N-Gram/
        └───.idea.
        └───Content Summary/
        │   AugurationSpeech.txt
        │   summary.py
        │   
        └───Github-NGram/
            README.md
            Ngrams.py
            movies.txt
```

## 2. Data Path
Databases are stored in "*_results" directories. Databases that ends with '.db' are SQLiteDB, that ends with '.pickle' are Python Pickle storages. 

## 3. Contribution
Leader: Professor Heather A. Haveman [University of California, Berkeley]   
Undergraduate Researchers:   
  1. N-Gram Analysis: Shixuan (Wayne) Li; Yijun Long   
  2. Metadata Analysis: Jahnavi Singh; Poorvi Acharya    
  3. Subject Matching: Wendi Zhang   


  


