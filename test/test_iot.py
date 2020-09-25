from random import randint

from locust import HttpUser, tag, task, between, constant

from config.config import retrieve_config

config = retrieve_config()


class IotUser(HttpUser):
    areas = ['Area A', 'Area B', 'Area C']
    HTTP = 'http://'
    host = HTTP + "127.0.0.1:8001"  # just to avoid error
    wait_time = constant(30)
    n_patient = config['initial_patient'] - 1

    @tag('iotA')
    @task
    def iot_a(self):
        """
        function that simulates the sending of diagnostic data to the Fog A node
        Returns:

        """
        area = 'Area A'
        host = config['fog']['elb'][area]

        id_patient = randint(0, self.n_patient)
        blood_pressure = randint(30, 119)
        bmi = randint(16, 39)
        glucose = randint(35, 499)
        insulin = randint(6, 59)
        skin = randint(10, 98)

        json = {"blood_pressure": blood_pressure, "bmi": bmi, "glucose": glucose,
                "id": id_patient, "insulin": insulin, "skin": skin, "area": area}
        self.client.post(self.HTTP+host+"/iot", json=json)
        return

    @tag('iotB')
    @task
    def iot_b(self):
        """
        function that simulates the sending of diagnostic data to the Fog A node
        Returns:

        """
        area = 'Area B'
        host = config['fog']['elb'][area]

        id_patient = randint(0, self.n_patient)
        blood_pressure = randint(30, 119)
        bmi = randint(16, 39)
        glucose = randint(35, 499)
        insulin = randint(6, 59)
        skin = randint(10, 98)

        json = {"blood_pressure": blood_pressure, "bmi": bmi, "glucose": glucose,
                "id": id_patient, "insulin": insulin, "skin": skin, "area": area}
        self.client.post(self.HTTP + host + "/iot", json=json)
        return

    @tag('iotC')
    @task
    def iot_c(self):
        """
        function that simulates the sending of diagnostic data to the Fog A node
        Returns:

        """
        area = 'Area C'
        host = config['fog']['elb'][area]

        id_patient = randint(0, self.n_patient)
        blood_pressure = randint(30, 119)
        bmi = randint(16, 39)
        glucose = randint(35, 499)
        insulin = randint(6, 59)
        skin = randint(10, 98)

        json = {"blood_pressure": blood_pressure, "bmi": bmi, "glucose": glucose,
                "id": id_patient, "insulin": insulin, "skin": skin, "area": area}
        self.client.post(self.HTTP + host + "/iot", json=json)
        return
