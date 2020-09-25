from datetime import datetime, timedelta
from random import randint
import random

import names
from locust import HttpUser, tag, task, between
from config.config import retrieve_config

config = retrieve_config()


def gen_datetime(min_year=1950, max_year=datetime.now().year):
    # generate a datetime in format yyyy-mm-dd hh:mm:ss.000000
    start = datetime(min_year, 1, 1, 00, 00, 00)
    years = max_year - min_year + 1
    end = start + timedelta(days=365 * years)
    return start + (end - start) * random.random()


class WebUser(HttpUser):
    areas = ['Area A', 'Area B', 'Area C']
    HTTP = 'http://'
    host = HTTP + "127.0.0.1:8001" # just to avoid error
    wait_time = between(1, 10)  # todo: che dobbiamo fare qua

    @tag('signin')
    @task
    def patient_page(self):
        """
        function that tests the request for the main page of the application
        Returns:

        """
        area_to_connect = random.choice(self.areas)
        host = config['fog']['elb'][area_to_connect]
        self.client.post(self.HTTP+host)
        return

    @tag('index')
    @task
    def index(self):
        """
        function that tests the request for the index page of the application
        Returns:

        """
        area_belong_to = random.choice(self.areas)
        area_to_connect = random.choice(self.areas)
        host = config['fog']['elb'][area_to_connect]
        json = {"area_to_connect": area_to_connect, "area_belong_to": area_belong_to}
        self.client.post(self.HTTP+host+"/get_patients_x", json=json)
        return

    @tag('measurements')
    @task
    def measurements(self):
        """
        function that tests the request for the patient page of the application
        Returns:

        """
        id_patient = randint(0, 100)
        area_belong_to = random.choice(self.areas)
        area_to_connect = random.choice(self.areas)
        host = config['fog']['elb'][area_to_connect]
        json = {"area_to_connect": area_to_connect, "area_belong_to": area_belong_to, "id": id_patient}
        self.client.post(self.HTTP+host+"/measuremetsX", json=json)
        return

    @tag('add_patient')
    @task
    def add_patient(self):
        """
        function that tests the request for adding a patient
        Returns:

        """
        area_belong_to = random.choice(self.areas)
        area_to_connect = random.choice(self.areas)
        host = config['fog']['elb'][area_to_connect]
        name = names.get_first_name()
        surname = names.get_last_name()
        gen = str(gen_datetime())[0:10]
        bday = str(datetime.strptime(gen, '%Y-%m-%d'))
        outcome = random.randint(0, 1)
        json = {'name': name, 'surname': surname, 'bday': bday, 'area': area_belong_to, 'outcome': outcome,
                'area_to_connect': area_to_connect}
        self.client.post(self.HTTP+host+"/add_patientX", json=json)
        return

    @tag('evaluation')
    @task
    def evaluation(self):
        """
        function that tests a patient's evaluation request
        Returns:

        """
        area_to_connect = random.choice(self.areas)
        host = config['fog']['elb'][area_to_connect]
        blood_pressure = randint(30, 119)
        bmi = randint(16, 39)
        glucose = randint(35, 499)
        insulin = randint(6, 59)
        skin = randint(10, 98)
        gen = str(gen_datetime())[0:10]
        bday = str(datetime.strptime(gen, '%Y-%m-%d'))
        json = {"glucose": glucose, 'bloodPressure': blood_pressure, 'insulin': insulin, 'bmi': bmi, 'skin': skin,
                'bday': bday, 'area': area_to_connect}
        self.client.post(self.HTTP+host+"/evaluation", json=json)
        return
