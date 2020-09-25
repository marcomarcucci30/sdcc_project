import json
import threading
import time

from database.query import retrieve_patients, retrieve_measure, check_id, insert_patient_db
lock = threading.Lock()


def retrieve_rows(area_to_connect, area_belong_to):
    """
    This function retrieve the patients list calling the query module and creates a json array
    Args:
        area_to_connect: area of the node
        area_belong_to: area of the patient

    Returns: a json array containing the patients

    """
    rows = retrieve_patients(area_to_connect, area_belong_to)
    if not rows:
        return json.dumps([])
    # tuple to json
    contents = []
    for row in rows:
        content = {
            'id': row[0],
            'namePatient': row[1],
            'surnamePatient': row[2],
            'bday': str(row[3]),
            'outcome': row[4],
            'area': row[5]
        }
        contents.append(content)
    return json.dumps(contents)


def retrieve_row_measure(area_to_connect, area_belong_to, _id):
    """
    This function retrieve the patient infos calling the query module and creates a json object
    Args:
        area_to_connect: area of the node
        area_belong_to: area of the patient
        _id: id of the patient

    Returns: a json object containing the infos

    """
    row = retrieve_measure(area_to_connect, area_belong_to, _id)
    # tuple to json
    # id, stamp, area, glucose , bloodPressure, insulin, bmi, skin, age, outcome
    if row is None:
        return json.dumps([])
    content = {
        'id': row[0],
        'stamp': str(row[1]),
        'area': row[2],
        'glucose': row[3],
        'bloodPressure': row[4],
        'insulin': row[5],
        'bmi': row[6],
        'skin': row[7],
        'age': row[8],
        'outcome': row[9]
    }
    return json.dumps(content)


def insert_patient(area_belong_to, js):
    """
    This function retrieves the next id assigning it to to the patient is going to insert to
    Args:
        area_belong_to: area of the patient
        js: patient data in JSON format

    Returns: True if successful

    """
    try:
        lock.acquire()
        _id = check_id(area_belong_to)
        if _id == -1:
            return False
        js['id'] = _id + 1
        if not insert_patient_db(area_belong_to, js):
            return False
    finally:
        lock.release()
    time.sleep(0.113)
    insert_patient_db('Cloud', js)
    return True
