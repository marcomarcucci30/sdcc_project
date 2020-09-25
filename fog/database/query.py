import base64

import mysql.connector as mysql
import datetime

from config.config import retrieve_config

CHECK_INSTANCES = "SELECT COUNT(*) FROM measurements"
INSERT = "INSERT ignore INTO measurements (id, stamp, area, glucose , bloodPressure, insulin, bmi, skin, age, outcome) " \
         "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
RETRIEVE_AGE = "SELECT bday, outcome FROM patient where id = %s AND area = %s"
RETRIEVE_PATIENTS = "SELECT * FROM patient where area = %(area)s"
RETRIEVE_MEASURE = "SELECT * FROM measurements where area = %s and id = %s order by stamp desc"
READ_JOBLIB = "SELECT * FROM joblib"
CHECK_ID = "SELECT id FROM patient order by id desc;"
INSERT_PATIENT = "INSERT ignore INTO patient values(%s, %s, %s, %s, %s, %s);"


def retrieve_joblib(area):
    """
    Used by a fog node to retrieve the classifier which allows for evaluation of the patient
    Args:
        area: the area of the fog node

    Returns: the decoded classifier

    """
    db = connect(area)
    cursor = db.cursor(buffered=True)
    cursor.execute(READ_JOBLIB)
    res = cursor.fetchone()
    cursor.close()
    db.close()
    if res is None:
        return None
    res = res[1]
    dec = base64.b64decode(res)
    return dec


def retrieve_measure(area_to_connect, area_belong_to, iD):
    """
    To display the info of a patient in the web interface, this function allows to retrieve from the
    fog node DB, such info
    Args:
        area_to_connect: area of the node
        area_belong_to: area of the patient
        iD: id of the patient

    Returns: the updated info of the patient

    """
    db = connect(area_to_connect)
    cursor = db.cursor(buffered=True)
    cursor.execute(RETRIEVE_MEASURE, (area_belong_to, iD))
    instance = cursor.fetchone()
    cursor.close()
    db.close()
    return instance


def retrieve_patients(area_to_connect, area_belong_to):
    """
    To display the patient list in the web interface, this function allows to retrieve from the
    fog node DB, such info
    Args:
        area_to_connect: area of the node
        area_belong_to: area of the patient

    Returns: all the patient and their info

    """
    db = connect(area_to_connect)
    cursor = db.cursor()
    cursor.execute(RETRIEVE_PATIENTS, {"area": area_belong_to})
    instances = cursor.fetchall()
    cursor.close()
    db.close()
    return instances


def connect(area):
    """
    A simple function for DB connection
    Args:
        area: area of the DB

    Returns: the connection

    """
    json_object = retrieve_config()
    if area == "Cloud":
        db = mysql.connect(
            host=json_object['cloud']['db'],
            user=json_object['user'],
            passwd=json_object['passwd'],
            database=json_object['database'],
            auth_plugin='mysql_native_password',
            buffered=True
        )
    else:
        db = mysql.connect(
            host=json_object['fog']['db'][area],
            user=json_object['user'],
            passwd=json_object['passwd'],
            database=json_object['database'],
            auth_plugin='mysql_native_password',
            buffered=True
        )
    return db


def check_instances(area):
    """
    It allows to retrieve the number of measurements received from IoTs
    Args:
        area: area of the DB

    Returns: the number of measurements

    """
    db = connect(area)
    cursor = db.cursor()
    cursor.execute(CHECK_INSTANCES)
    instances = cursor.fetchone()[0]
    cursor.close()
    db.close()
    return instances


def insert(content):
    """
    This function allows to update the fog node DB when a measurement arrives from IoTs
    Args:
        content: a dictionary containing the measurement

    Returns: the same dictionary whit the field of age, computed in this function

    """
    db = connect(content['area'])
    cursor = db.cursor()
    cursor.execute(RETRIEVE_AGE, (content["id"], content["area"]))
    results = cursor.fetchone()
    bday = results[0]
    outcome = results[1]
    age = calculateAge(datetime.datetime.strptime(str(bday), '%Y-%m-%d'))
    content.update({'age': age})
    content.update({'outcome': outcome})
    try:
        val = (
            content["id"], content['time_stamp'], content["area"], content["glucose"], content["blood_pressure"],
            content["insulin"],
            content["bmi"], content["skin"], content["age"], content["outcome"])
        cursor.execute(INSERT, val)
    except Exception as err:
        print("OS error: {0}".format(err))
        # db.rollback()
        return False
    finally:
        db.commit()
        cursor.close()
        db.close()

    return True


def calculateAge(birthDate):
    """
    A simple function to compute the age of a patient
    Args:
        birthDate: the birth date

    Returns: the age

    """
    today = datetime.date.today()
    age = today.year - birthDate.year - ((today.month, today.day) < (birthDate.month, birthDate.day))
    return age


def main():
    db = connect('area')
    cursor = db.cursor()
    cursor.execute('SELECT glucose, bloodPressure, insulin, bmi, skin, age FROM measurements')
    print(cursor.fetchall())


def insert_patient_db(area_belong_to, js):
    """
    This function insert the patient in the DB
    Args:
        area_belong_to: area of the patient
        js: patient data in JSON format

    Returns: True if successful

    """
    cursor = None
    db = None
    try:
        db = connect(area_belong_to)
        cursor = db.cursor()
        cursor.execute(INSERT_PATIENT, (js['id'], js['name'], js['surname'], js['bday'], js['outcome'], js['area']))
        db.commit()
    except Exception as err:
        print(err)
        return False
    finally:
        cursor.close()
        db.close()
    return True


def check_id(area_belong_to):
    """
    It retrieves the highest patient id
    Args:
        area_belong_to: area of the patient

    Returns: the highest id

    """
    cursor = None
    db = None
    try:
        db = connect(area_belong_to)
        cursor = db.cursor(buffered=True)
        cursor.execute(CHECK_ID)
        results = cursor.fetchone()
        _id = results[0]
    except Exception as err:
        print(err)
        return -1
    finally:
        cursor.close()
        db.close()
    return _id


