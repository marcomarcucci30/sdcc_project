import time

import mysql.connector as mysql
import names
import random
from datetime import datetime, timedelta


'''
Modulo che si occupa dell'instanziazione del database.
'''


def instantiateDatabase(host, host_cloud, user, passwd, area):
    db = mysql.connect(
        host=host,
        user=user,
        passwd=passwd,
        auth_plugin='mysql_native_password'
    )

    cursor = db.cursor()

    # Effettuo la creazione del database
    cursor.execute("CREATE DATABASE IF NOT EXISTS mydb")

    cursor.close()

    db.close()

    db = mysql.connect(
        host=host,
        user=user,
        passwd=passwd,
        database='mydb',
        auth_plugin='mysql_native_password'
    )

    # Eseguo le query per la creazione delle tabelle

    cursor = db.cursor()

    # Query per l'instanziazione di una tabella con le info riguardanti il cluster

    cursor.execute(
        "CREATE TABLE IF NOT EXISTS patient (id INTEGER, namePatient VARCHAR (100), surnamePatient"
        " VARCHAR (20), bday DATE, outcome INTEGER, area VARCHAR (20), PRIMARY KEY (id, area))")
    db.commit()

    cursor.execute(
        "CREATE TABLE IF NOT EXISTS measurements (id INTEGER,  stamp DATETIME, area VARCHAR (20), "
        "glucose INTEGER , bloodPressure INTEGER, insulin INTEGER, bmi INTEGER, skin INTEGER, age INTEGER, "
        "outcome INTEGER, PRIMARY KEY (id, stamp, area))")
    db.commit()

    cursor.execute(
        "CREATE TABLE IF NOT EXISTS joblib (id INTEGER, file LONGBLOB, PRIMARY KEY (id))")
    db.commit()

    if area != 'Cloud':
        fill_db(cursor, db, area, host_cloud, user, passwd)

    cursor.close()
    db.close()

    return 0


def fill_db(cursor, db, area, host_cloud, user, passwd):
    db_cloud = mysql.connect(
        host=host_cloud,
        user=user,
        passwd=passwd,
        database='mydb',
        auth_plugin='mysql_native_password'
    )

    # Eseguo le query per la creazione delle tabelle

    cursor_cloud = db_cloud.cursor()

    for i in range(0, 100):
        INSERT = "INSERT ignore INTO patient values(%s, %s, %s, %s, %s, %s);"

        name = names.get_first_name()
        surname = names.get_last_name()
        gen = str(gen_datetime())[0:10]
        bday = datetime.strptime(gen, '%Y-%m-%d')
        diabetes = random.randint(0, 1)
        cursor.execute(INSERT, (i, name, surname, bday, diabetes, area))
        db.commit()

        cursor_cloud.execute(INSERT, (i, name, surname, bday, diabetes, area))
        db_cloud.commit()



    cursor_cloud.close()
    db_cloud.close()
    return


def gen_datetime(min_year=1950, max_year=datetime.now().year):
    # generate a datetime in format yyyy-mm-dd hh:mm:ss.000000
    start = datetime(min_year, 1, 1, 00, 00, 00)
    years = max_year - min_year + 1
    end = start + timedelta(days=365 * years)
    return start + (end - start) * random.random()

