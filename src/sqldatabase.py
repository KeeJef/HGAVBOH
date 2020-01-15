import sqlite3
from sqlite3 import Error


#This file might be used if storing the images in memory becomes annoying

sql_create_images_table = """ CREATE TABLE IF NOT EXISTS images (
                                    id integer PRIMARY KEY,
                                    public_key text NOT NULL,
                                    timestamp text,
                                    blockhash text,
                                    imagehash text,
                                    signature text,
                                    commit text, 
                                    votedfornode text,
                                    rawimagebytes text,
                                ); """
 
 
def create_connection(db_file):
    """ create a database connection to the SQLite database
        specified by db_file
    :param db_file: database file
    :return: Connection object or None
    """
    conn = None
    try:
        conn = sqlite3.connect(db_file)
        return conn
    except Error as e:
        print(e)
 
    return conn

def create_table(conn):
    """ create a table from the create_table_sql statement
    :param conn: Connection object
    :param create_table_sql: a CREATE TABLE statement
    :return:
    """
    try:
        c = conn.cursor()
        c.execute(sql_create_images_table)
    except Error as e:
        print(e)

def create_image(conn, imageentry):
    """
    Create a new image into the images table
    :param conn:
    :param project:
    :return: project id
    """
    sql = ''' INSERT INTO images(public_key,timestamp,blockhash,imagehash,signature,commit,votedfornode,rawimagebytes)
              VALUES(?,?,?,?,?,?,?,?) '''
    cur = conn.cursor()
    cur.execute(sql, imageentry)
    return cur.lastrowid
 
 
if __name__ == '__main__':
    create_connection(r"../assets/HGAVBOH.db")