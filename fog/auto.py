import json
import time
from datetime import datetime
import requests
from requests import post

from config.config import retrieve_config
from database.query import check_instances, insert
import _thread as thread

date_time_str = '2020-09-01 08:15:27.243860'
TIMESTAMP = datetime.strptime(date_time_str, '%Y-%m-%d %H:%M:%S.%f')
area = ""
config = retrieve_config()


def filtering(content):
    """
    This function parses the measurements sent by IoTs and discards values out of range
    Args:
        content: a dictionary containing the measurement

    Returns: the same dictionary if ok, otherwise None

    """
    glucose = content["glucose"]
    blood = content["blood_pressure"]
    insulin = content["insulin"]
    bmi = content["bmi"]
    skin = content["skin"]

    print(glucose, blood, bmi, insulin, skin)

    if (glucose not in range(35, 500) or blood not in range(30, 120) or insulin not in range(6, 60) or
            bmi not in range(16, 40) or skin not in range(10, 99)):
        return None
    else:
        return content


def storage_handler():
    """
    It creates threads that control the number of measurements on fog DB
    Returns:

    """
    global area
    while True:
        time.sleep(10)
        if area != "":
            try:
                thread.start_new_thread(storage, ())
            except Exception as err:
                print("Error: unable to start thread ", err)


def storage():
    """
    It controls the number of measurements instance on fog DB and if it overcomes
    max_instances call the cloud to move the instances on cloud DB
    Returns:

    """
    global area
    global TIMESTAMP
    instances = check_instances(area)
    print("STORAGE 2 \n\n\n")
    if instances > config["max_instances"]:
        # contatta cloud db
        timestamp = TIMESTAMP
        url = config["cloud"]['elb']
        time.sleep(0.113)
        requests.post("http://" + url + "/storage", json={'timestamp': str(timestamp), 'area': area})
    return


def update_db(content):
    """
    It calls the query module to insert measurement sent by IoTs and send a request to the cloud when the DB overcomes
    the max count of measurements
    Args:
        content: a dictionary containing the measurement

    Returns:

    """
    global area
    global TIMESTAMP
    global config
    area = content['area']
    timestamp = datetime.now()
    print(timestamp)
    content.update({'time_stamp': timestamp})
    TIMESTAMP = timestamp
    insert(content)


