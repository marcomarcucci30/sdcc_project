import json
import pathlib
from flask import Flask, render_template, request, redirect, url_for, jsonify, session
import pandas as pd
from requests import post, get
from config.config import retrieve_config

app = Flask(__name__)
app.secret_key = 'ciao'
config = retrieve_config()
outcome = 2
name = ""
surname = ""
bday = ""
area = ""


@app.route('/', methods=["GET", "POST"])
def signin():
    """
    Function which gets the string related to the selected
    radio button in 'index.html', either for the area to
    which the user belongs and the one he wants to
    connect to.
    Then it passes these strings through session.

    Returns:
        A response object that redirects the client
        to the overview location, if the request method
        is a 'POST';
        The 'signin' template if the method is a 'GET'.
    """
    if request.method == 'POST':
        if request.form['radio_1'] == 'Area A':
            area_1 = 'Area A'
        elif request.form['radio_1'] == 'Area B':
            area_1 = 'Area B'
        elif request.form['radio_1'] == 'Area C':
            area_1 = 'Area C'
        if request.form['radio_2'] == 'Area A':
            area_2 = 'Area A'
        elif request.form['radio_2'] == 'Area B':
            area_2 = 'Area B'
        elif request.form['radio_2'] == 'Area C':
            area_2 = 'Area C'
        session['area_1'] = area_1
        session['area_2'] = area_2
        return redirect(url_for('index'))
    if request.method == 'GET':
        return render_template('signin.html')


@app.route('/patient_page', methods=["GET", "POST"])
def patient_page():
    """
    Function which retrieves the patient identification
    data from 'index.html' in the 'POST' method; then,
    either in the 'POST' and in the 'GET' method, it
    obtains the domain name of the fog load balancer
    for the given connection area from the 'config' file.
    It, then, retrieves the clinical situation for the
    selected patient as response from posting the specific
    areas to the domain name previously obtained and to
    the 'measurementsX' route.

    Returns:
        Thw 'patient_page' template with the necessary
        variables for the template context.
    """
    global _id, name, surname, area, config
    area_to_connect = session['area_2']
    if request.method == 'POST':
        area = request.form['area']
        _id = request.form['id']
        name = request.form['namePatient']
        surname = request.form['surnamePatient']
        dns = config['fog']['elb'][area_to_connect]
        response = post("http://" + dns + "/measurementsX", json={"area_to_connect": area_to_connect,
                                                                  "area_belong_to": area, "id": _id})
        measurement = response.content
        measurement = json.loads(measurement)
        return render_template('patient_page.html', id=_id, namePatient=name, surnamePatient=surname,
                               glucose=measurement['glucose'], bloodPressure=measurement['bloodPressure'],
                               insulin=measurement['insulin'], bmi=measurement['bmi'],
                               skin=measurement['skin'], age=measurement['age'],
                               outcome=measurement['outcome'],
                               area=area)

    if request.method == 'GET':
        dns = config['fog']['elb'][area_to_connect]
        response = post("http://" + dns + "/measurementsX", json={"area_to_connect": area_to_connect,
                                                                  "area_belong_to": area, "id": _id})
        measurement = response.content
        print(measurement)
        measurement = json.loads(measurement)
        print(measurement)
        return render_template('patient_page.html', id=_id, namePatient=name, surnamePatient=surname,
                               glucose=measurement['glucose'], bloodPressure=measurement['bloodPressure'],
                               insulin=measurement['insulin'], bmi=measurement['bmi'],
                               skin=measurement['skin'], age=measurement['age'],
                               outcome=measurement['outcome'],
                               area=area)


@app.route('/index', methods=["GET", "POST"])
def index():
    """
   Function which retrieves both the areas selected
   by the user through session; then, it obtains the
   domain name of the fog load balancer for the given
   connection area from the 'config' file.
   It, then, retrieves the patients for the selected
   area as response from posting the specific areas
   to the domain name previously obtained and to
   the 'patientsX' route.

   Returns:
       Thw 'index' template with the necessary
       variables for the template context.
   """
    global config
    area_belong_to = session['area_1']
    area_to_connect = session['area_2']
    print(area_belong_to, area_to_connect)
    dns = config['fog']['elb'][area_to_connect]
    print('{"Area_belong_to": "' + area_belong_to + '"}')
    print('{"Area_to_connect": "' + area_to_connect + '"}')
    print("http://" + dns + "/patientsX", )

    patients = post("http://" + dns + "/patientsX", json={"area_to_connect": area_to_connect,
                                                          "area_belong_to": area_belong_to})
    print(patients.content)
    # post to fog
    temp, column_names = get_table(patients.content)
    return render_template('index.html', area=area_to_connect, records=temp, colnames=column_names)


@app.route('/evaluation', methods=["GET", "POST"])
def evaluation():
    """
    Function which gets all the identification data
    and the clinical situation of the patient inserted
    in the 'evaluation.html' form. The clinical data are,
    then, sent via post, to the specific domain name and
    to the 'evaluation' route, in order to be used for the
    machine learning, which result is finally passed as a
    variable for the template context.

    Returns:
        The 'evaluation' template with the necessary
        variables for the template context.
    """
    global name, surname, bday, area, outcome, config
    if request.method == 'POST':
        if request.form["subButton"] == 'evaluate':
            if "name" in request.form:
                _name = request.form["name"]
                if _name is not None:
                    name = _name
            if "surname" in request.form:
                _surname = request.form["surname"]
                if _surname is not None:
                    surname = _surname
            if "bday" in request.form:
                _bday = request.form["bday"]
                if _bday is not None:
                    bday = _bday
            if request.form['optradio'] == 'Area A':
                area = 'Area A'
            elif request.form['optradio'] == 'Area B':
                area = 'Area B'
            elif request.form['optradio'] == 'Area C':
                area = 'Area C'

            if "glucose" in request.form:
                _glucose = request.form["glucose"]
                if _glucose is not None:
                    glucose = _glucose
            if "bloodPressure" in request.form:
                _bloodPressure = request.form["bloodPressure"]
                if _bloodPressure is not None:
                    bloodPressure = _bloodPressure
            if "insulin" in request.form:
                _insulin = request.form["insulin"]
                if _insulin is not None:
                    insulin = _insulin
            if "bmi" in request.form:
                _bmi = request.form["bmi"]
                if _bmi is not None:
                    bmi = _bmi
            if "skin" in request.form:
                _skin = request.form["skin"]
                if _skin is not None:
                    skin = _skin

            patient = json.dumps({'name': name, 'surname': surname, 'bday': bday, 'area': area})
            feature = json.dumps(
                {'glucose': glucose, 'bloodPressure': bloodPressure, 'insulin': insulin, 'bmi': bmi, 'skin': skin})
            area_to_connect = session['area_2']
            dns = config['fog']['elb'][area_to_connect]
            result = post("http://" + dns + "/evaluation", json={"glucose": glucose, 'bloodPressure': bloodPressure,
                                                                 'insulin': insulin, 'bmi': bmi, 'skin': skin,
                                                                 'bday': bday, 'area': area_to_connect})
            res = json.loads(result.content)
            outcome = res['result']
            print(outcome)
            if outcome == 1:
                res = 'Diabetic'
            elif outcome == 0:
                res = 'Healthy'
            else:
                res = 'Prediction not available, try later.'
            # glucose, bloodPressure, insulin, bmi, skin, age
            print(json.dumps({'patient': patient, 'feature': feature}))
            return render_template('evaluation.html', area=area, name=name, surname=surname, date=bday, glucose=glucose,
                                   bloodPressure=bloodPressure, insulin=insulin, bmi=bmi, skin=skin,
                                   result=res)
        elif request.form["subButton"] == 'add':
            if outcome != 2:
                area_to_connect = session['area_2']
                dns = config['fog']['elb'][area_to_connect]
                result = post("http://" + dns + "/add_patientX", json={'name': name, 'surname': surname, 'bday': bday,
                                                                       'area': area, 'outcome': outcome,
                                                                       'area_to_connect': area_to_connect})
                if json.loads(result.content):
                    print('Patient added')
                    return render_template('evaluation.html', error="Patient added")
                else:
                    print("Unable to add patient, retry")
                    return render_template('evaluation.html', error="Unable to add patient, retry")
            return render_template('evaluation.html')

    if request.method == 'GET':
        return render_template('evaluation.html')


def get_table(json1):
    """
    Function that takes the json containing all
    the patients identification data and converts
    it into a dataframe; this is, then, converted
    into a list of {column -> value}.

    Args:
        json1: which contains the patients' id, name,
        surname, birthday, outcome and area.

    Returns:
        A list of {column -> value} and the column
        values.
    """
    print(json1)
    df = pd.DataFrame(eval(json1))
    temp = df.to_dict('records')
    column_names = df.columns.values
    return temp, column_names


# route elb
@app.route('/ping', methods=['POST', 'GET'])
def ping():
    """
    A simple route to ping the node, used by ELB
    Returns: a string for success

    """
    return "Pong\n"


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8080)
