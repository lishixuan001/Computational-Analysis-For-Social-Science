from os.path import join 
import sqlite3 
import pickle 
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from statistics import mean 


meta_root = "../Metadata/"
data_root = "./map_results/"


def load_meta(id):
    """
    Load Metadata from Pickles
    """
    meta_file_name = "part{id}.pickle".format(id=id)
    meta_file_path = join(meta_root, meta_file_name)

    with open(meta_file_path, 'rb') as meta_file:
        metadata = pickle.load(meta_file)
        
    return metadata 


def load_data(id):
    """
    Load Map Results Data from Sqlite
    """
    db_name = "map_results_{id}.db".format(id=str(id).zfill(3))
    
    conn = sqlite3.connect(join(data_root, db_name))
    cur = conn.cursor()
    cur.execute("SELECT * FROM map_result")
    
    database_collection = cur.fetchall()
    columns = ["set_id", "file_id",
               "n1_culture", "n1_demographic", "n1_relational", "n1_article",
               "n2_culture", "n2_demographic", "n2_relational", "n2_article",
               "n3_culture", "n3_demographic", "n3_relational", "n3_article",
               "culture_count", "demographic_count", "relational_count", "article_count"]
    index = list(range(len(database_collection)))
    
    df_database = pd.DataFrame(database_collection, columns=columns, index=index)
    df_database['file_id'] = df_database['file_id'].apply(lambda x: x.split('_')[-1])

    conn.commit()
    cur.close()
    conn.close()

    return df_database 


def load_full_data():
    map_results = []
    for id in range(1, 15):
        map_results.append(load_data(id))
    return pd.concat(map_results)



def collect_data():
    """
    Collect Data for Three Classes
    """
    culture_data = dict()
    demographic_data = dict()
    relational_data = dict()

    map_full_results = load_full_data()
    
    for id in range(1, 15):
        
        print("Start Process Set [{}] ...".format(id))
        
        metadata = load_meta(id)
        map_results = load_data(id)

        invalid_year = 0
        invalid_id = 0
        for index, row in metadata.iterrows():
            year = row['year']
            article_id = row['article_id']
            
            try:
                year = int(year) // 10 * 10
                article_id = article_id.split('/')[-1]
                
                data_row = map_results.loc[map_results['file_id'] == article_id]
                if data_row.empty:
                    data_row = map_full_results.loc[map_full_results['file_id'] == article_id]

                if not data_row.empty:
                    culture_count = int(data_row['culture_count'])
                    demographic_count = int(data_row['demographic_count']) 
                    relational_count = int(data_row['relational_count'])
                    article_count = int(data_row['article_count'])
                    
                    culture_rate = culture_count / article_count
                    demographic_rate = demographic_count / article_count
                    relational_rate = relational_count / article_count

                    culture_element = culture_rate
                    demographic_element = demographic_rate
                    relational_element = relational_rate

                    if year not in culture_data.keys():
                        culture_data[year] = list([culture_element])
                        demographic_data[year] = list([demographic_element])
                        relational_data[year] = list([relational_element])
                    else:
                        culture_data[year].append(culture_element)
                        demographic_data[year].append(demographic_element)
                        relational_data[year].append(relational_element)
                else:
                    invalid_id += 1

            except Exception as e:
                invalid_year += 1

            if index % 500 == 0:
                print("---> Processed [{}]".format(index))
            

        print("===> Set [{}] Finished, Invalid Year [{}], Invalid ID [{}]\n".format(id, invalid_year, invalid_id))

    return culture_data, demographic_data, relational_data
    

if __name__ == '__main__':
    
    culture_data, demographic_data, relational_data = collect_data()
    
    sorted_keys = sorted(list(culture_data.keys()))
    culture_data = [mean(culture_data[k]) for k in sorted_keys]
    demographic_data = [mean(demographic_data[k]) for k in sorted_keys]
    relational_data = [mean(relational_data[k]) for k in sorted_keys]

    plt.title("Visualization")
    
    x_axis = sorted_keys
    plt.plot(x_axis, culture_data, label='Culture')
    plt.plot(x_axis, demographic_data, label='Demographic')
    plt.plot(x_axis, relational_data, label='Relational')

    plt.legend()
    plt.xlabel("Year")
    plt.ylabel("Count")
    plt.xticks(rotation=270)

    plt.savefig("./imgs/avg_rate.png")
    
    print("=== Visualization Generated ===")



