import argparse, sqlite3
from os.path import isfile, join


def load_args():
    """
    [Data Generation]
    Load arguments from user command input [attributes for data management]
    :return: parsed arguments
    """
    parser = argparse.ArgumentParser()
    parser.add_argument("--file_set_id",
                        help="File set to analyze",
                        default="000",
                        type=str,
                        required=True)
    args = parser.parse_args()
    return args

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


def get_breakpoint_article_id(db_root, db_name):
    # Connect to the database "map_result.db"
    conn = sqlite3.connect(join(db_root, db_name))
    # Create Cursor object so that we can execute SQL commands
    cur = conn.cursor()
    # Select all data entries from the table 
    cur.execute('SELECT * FROM map_result')
    # Display all data collected
    database_collection = cur.fetchall()
    print("Total Count: {count}".format(count=len(database_collection)))
    # Close the cursor and the database
    cur.close()
    conn.close()
    
#     if len(database_collection) > 0:
#         latest_record = database_collection[-1]
#         display(latest_record)

    return None

if __name__ == "__main__":
    
    args = load_args()
    
    # Paths for Database
    db_root = "./map_results"
    db_name = "map_result_{}.db".format(args.file_set_id)

    get_breakpoint_article_id(db_root, db_name)


