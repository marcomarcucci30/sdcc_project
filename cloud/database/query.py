import base64
import pathlib

import joblib
import mysql.connector as mysql
import json

from config.config import retrieve_config

config = retrieve_config()

CHECK_INSTANCES = "SELECT COUNT(*) FROM measurements WHERE stamp < %s"
INSERT = "INSERT ignore INTO measurements (id, stamp, area, glucose , bloodPressure, insulin, bmi, skin, age, outcome) " \
         "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
RETRIEVE_ROWS = "SELECT * FROM measurements WHERE stamp < %s"
DELETE_ROWS = "delete from measurements where stamp < %s"
CHECK_TOTAL = "SELECT COUNT(*) FROM measurements"
CHECK_JOBLIB = "SELECT count(*) FROM joblib"
UPDATE_JOBLIB = "UPDATE joblib set id = 0, file = %s"
INSERT_JOBLIB = "INSERT INTO joblib values (0, %s)"


def update_joblib(area):
    """
    function that takes care of sending the result of the tuning to the fog

    Args:
        area: fog area

    Returns:

    """
    db = connect(area)
    cursor = db.cursor()
    cursor.execute(CHECK_JOBLIB)
    rows = cursor.fetchone()[0]
    with open('/home/ubuntu/ec2-user/project/cloud/best_classifier.joblib', 'rb') as f:
        blob = base64.b64encode(f.read())
    if rows != 0:
        cursor.execute(UPDATE_JOBLIB, (blob,))
    else:
        cursor.execute(INSERT_JOBLIB, (blob,))
    db.commit()
    cursor.close()
    db.close()


def connect(area):
    """
    function that returns the connection to the fog or cloud database

    Args:
        area: fog or cloud area

    Returns: Database connection

    """
    if area == "Cloud":
        db = mysql.connect(
            host=config['cloud']['db'],
            user=config['user'],
            passwd=config['passwd'],
            database=config['database'],
            auth_plugin='mysql_native_password',
            buffered=True
        )
    else:
        db = mysql.connect(
            host=config['fog']['db'][area],
            user=config['user'],
            passwd=config['passwd'],
            database=config['database'],
            auth_plugin='mysql_native_password',
            buffered=True
        )
    return db


def check_for_ml():
    """
    function that returns the number of measurements in the Cloud Database

    Returns: number of rows

    """
    db = connect('Cloud')
    cursor = db.cursor()
    cursor.execute(CHECK_TOTAL)
    rows = cursor.fetchone()[0]
    cursor.close()
    db.close()
    return rows


def retrieve_rows(timestamp, area):
    """
    function that returns the measurements prior to a given time in the database of a given fog

    Args:
        timestamp: time to be considered for query
        area: fog area

    Returns: number of rows

    """
    db = connect(area)
    cursor = db.cursor()
    cursor.execute(RETRIEVE_ROWS, (timestamp,))
    rows = cursor.fetchall()
    cursor.close()
    db.close()
    return rows


def check_rows(timestamp, area):
    """
    function that returns the number of measurements prior to a given time in the database of a given fog to
    compare with a fixed number

    Args:
        timestamp: time to be considered for query
        area: fog area

    Returns: True if number of rows is greater than a fixed number, False otherwise

    """
    db = connect(area)
    cursor = db.cursor()
    cursor.execute(CHECK_INSTANCES, (timestamp,))
    rows = cursor.fetchone()[0]
    cursor.close()
    db.close()
    if rows >= config["max_instances"]:
        return True
    return False


def insert_rows(rows):
    """
    function that deletes the measurements before a given moment from the fog database

    Args:
        rows: list of measurements

    Returns: True if successful, False otherwise

    """
    db = connect('Cloud')
    cursor = db.cursor()
    try:
        for row in rows:
            content = {
                'id': row[0],
                'timestamp': row[1],
                'area': row[2],
                'glucose': row[3],
                'blood_pressure': row[4],
                'insulin': row[5],
                'bmi': row[6],
                'skin': row[7],
                'age': row[8],
                'outcome': row[9]
            }

            val = (
                content["id"], content["timestamp"], content["area"], content["glucose"], content["blood_pressure"],
                content["insulin"],
                content["bmi"], content["skin"], content["age"], content["outcome"])
            cursor.execute(INSERT, val)

    except Exception as err:
        print("OS error: {0}".format(err))
        db.rollback()
        return False
    finally:
        db.commit()
        cursor.close()
        db.close()
    return True


def delete_rows(timestamp, area):
    """
    function that deletes

    Args:
        timestamp: time to be considered for query
        area: fog's area
    Returns: True if successful, False otherwise

    """
    db = connect(area)
    cursor = db.cursor()
    try:
        cursor.execute(DELETE_ROWS, (timestamp,))
        db.commit()
    except Exception as err:
        print("OS error: {0}".format(err))
        db.rollback()
        return False
    finally:
        cursor.close()
        db.close()
    return True


def main():
    return


