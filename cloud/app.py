import faulthandler
import sys
import time

from flask import Flask, request
import _thread as thread

from database.query import retrieve_rows, check_rows, insert_rows, delete_rows
from tuning import tuning_handler

app = Flask(__name__)


# route for database storage
@app.route('/storage', methods=['POST'])
def storage_handler():
    print(request.is_json)
    content = request.get_json()
    timestamp = content["timestamp"]
    area = content['area']
    time.sleep(0.113)
    if not check_rows(timestamp, area):
        return "check_failed"
    time.sleep(0.113)
    rows = retrieve_rows(timestamp, area)
    if not insert_rows(rows):
        return "insert_failed"
    time.sleep(0.113)
    if not delete_rows(timestamp, area):
        delete_rows(timestamp, "Cloud")
        return
    return 'Updated'


# route ping
@app.route('/ping', methods=['POST', 'GET'])
def ping():
    return "Pong\n"


if __name__ == '__main__':
    faulthandler.enable()
    faulthandler.dump_traceback(file=sys.stderr, all_threads=True)
    try:
        thread.start_new_thread(tuning_handler, ())
    except:
        print("Error: unable to start thread")
    app.run(host='0.0.0.0', port=8080)  # todo porta 8080
