import pathlib
import threading
import time
from database.query import check_for_ml, update_joblib
from machine_learning import training_best_configuration
import _thread as thread

joblib_path = pathlib.Path(__file__).parent / 'best_classifier.joblib'


def tuning_handler():
    while True:
        time.sleep(60)
        try:
            thread.start_new_thread(tuning, ())
        except:
            print("Error: unable to start thread")


def tuning():
    print(threading.current_thread().ident)
    if check_for_ml() > 1000:
        training_best_configuration.main()
        update_joblib('Area A')
        update_joblib('Area B')
        update_joblib('Area C')


if __name__ == '__main__':
    print(threading.current_thread().ident)
