import ConfigParser
from mysql.connector import MySQLConnection, Error
import logging

logging.basicConfig(
    filename="dblogs.log",
    filemode='w',
    level=logging.DEBUG,
    format="%(asctime)s:%(levelname)s:%(message)s"
    # format="%(message)s;"
    )


def read_db_config(filename='config.ini', section='mysql'):
    """ Read database configuration file and return a dictionary object
    :param filename: name of the configuration file
    :param section: section of database configuration
    :return: a dictionary of database parameters
    """
    # create parser and read ini configuration file
    parser = ConfigParser.ConfigParser()
    parser.read(filename)

    # get section, default to mysql
    db = {}
    if parser.has_section(section):
        items = parser.items(section)
        for item in items:
            db[item[0]] = item[1]
    else:
        raise Exception('{0} not found in the {1} file'.format(section, filename))

    return db


def connect():
    """ Connect to MySQL database """

    db_config = read_db_config()

    try:
        print('Connecting to MySQL database...')
        conn = MySQLConnection(**db_config)

        if conn.is_connected():
            print('connection established.')
        else:
            print('connection failed.')

    except Error as error:
        print(error)

    finally:
        conn.close()
        print('Connection closed.')


def query_with_fetchone(query):
    try:
        dbconfig = read_db_config()
        conn = MySQLConnection(**dbconfig)
        cursor = conn.cursor()
        cursor.execute(query)

        row = cursor.fetchone()

        while row is not None:
            print(row)
            row = cursor.fetchone()

    except Error as e:
        print(e)

    finally:
        cursor.close()
        conn.close()


def query_with_fetchall(query):
    try:
        dbconfig = read_db_config()
        conn = MySQLConnection(**dbconfig)
        cursor = conn.cursor()
        cursor.execute(query)
        rows = cursor.fetchall()

        # print('Total Row(s):', cursor.rowcount)
        # for row in rows:
        #     print(row)
        return rows

    except Error as e:
        print(e)

    finally:
        cursor.close()
        conn.close()


def iter_row(cursor, size=10):
    while True:
        rows = cursor.fetchmany(size)
        if not rows:
            break
        for row in rows:
            yield row


def query_with_fetchmany(query):
    try:
        dbconfig = read_db_config()
        conn = MySQLConnection(**dbconfig)
        cursor = conn.cursor()

        cursor.execute(query)
        # logging.debug(query)
        for row in iter_row(cursor, 10):
            print(row)

    except Error as e:
        print(e)

    finally:
        cursor.close()
        conn.close()


def insert_partnercountbyrange(pid, rangeid, datethru, count, uniques, traittype):
    query = "INSERT INTO `dexreporting`.`rdPartnerCountsByRange` (`PID`, `RangeID`, `DateThru`, `Count`, `Uniques`," \
            " `TraitType`)" \
            " VALUES (%s, %s, %s, %s, %s, %s)"
    args = (pid, rangeid, datethru, count, uniques, traittype)

    try:
        db_config = read_db_config()
        conn = MySQLConnection(**db_config)

        cursor = conn.cursor()
        cursor.execute(query, args)

        if cursor.lastrowid:
            print('last insert id', cursor.lastrowid)
        else:
            print('last insert id not found')

        conn.commit()
    except Error as error:
        print("Error : " + str(error))

    finally:
        cursor.close()
        conn.close()


def insert_multiple(query, datalist):
    # query = "INSERT INTO `dexreporting`.`rdPartnerCountsByRange` (`PID`, `RangeID`, `DateThru`, `Count`, `Uniques`," \
    #         " `TraitType`)" \
    #         " VALUES (%s, %s, %s, %s, %s, %s)"

    try:
        db_config = read_db_config()
        conn = MySQLConnection(**db_config)

        cursor = conn.cursor()
        cursor.executemany(query, datalist)

        conn.commit()
    except Error as e:
        print('Error:', e)

    finally:
        cursor.close()
        conn.close()


def execute(query, args):
    db_config = read_db_config()

    try:
        # connect to the database server
        conn = MySQLConnection(**db_config)

        # execute the query
        cursor = conn.cursor()
        cursor.execute(query, args)

        # accept the change
        conn.commit()
        # logging.debug(query % args)
        # print(query % args)
    except Error as error:
        # log query here
        logging.error(error)
        # logging.error(query % args)

    finally:
        cursor.close()
        conn.close()


def fetch(query, args):
    db_config = read_db_config()

    try:
        # connect to the database server
        conn = MySQLConnection(**db_config)

        # execute the query
        cursor = conn.cursor()
        cursor.execute(query, args)
        rows = cursor.fetchall()
        # logging.debug(query % args)
        return rows

    except Error as error:
        logging.error(error)
        # logging.error(query % args)

    finally:
        cursor.close()
        conn.close()


if __name__ == '__main__':
    query_with_fetchmany("SELECT * FROM genrepredictor.Level1Prediction")
    # insert_partnercountbyrange(1194, 30, '2018-03-22', 1969007, 102458, 0)
    # insert_multiple_partnercountbyrange([(1194, 7, '2018-03-20', 1969007, 102458, 3),
    #                                      (1194, 7, '2018-03-19', 1969007, 102458, 3),
    #                                      (1194, 7, '2018-03-18', 1969007, 102458, 10),
    #                                      (1194, 7, '2018-03-17', 1969007, 102458, 11)])
