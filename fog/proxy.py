from flask import Flask, Response, request
from requests import get, post

app = Flask('__main__')


@app.route('/', defaults={'path': ''},  methods=['POST', 'GET'])
def proxy(path):
    """
    Redirect requests to minikube load balancer service
    Args:
        path: the route

    Returns: the response of minikube pod

    """
    return get(f'{SITE_NAME}{path}').content


@app.route('/<path:path>',  methods=['POST', 'GET'])
def proxy_p(path):
    """
    Redirect requests to minikube load balancer service
    Args:
        path: the route

    Returns: the response of minikube pod

    """
    if path == 'favicon.ico':
        return 'no favicon'
    r = post(f'{SITE_NAME}{path}', json=request.get_json())
    return Response(r.content, mimetype="application/json")


@app.before_first_request
def init():
    """
    Retrieve ip and port of minikube load balancer service
    Returns:

    """
    f = open('/home/ubuntu/ec2-user/project/fog/configIpPortLoadBalancer.txt', 'r')
    global IP_LB, PORT_LB, SITE_NAME
    IP_LB = f.readline().replace('\n', '')
    PORT_LB = f.readline().replace('\n', '')
    f.close()
    SITE_NAME = 'http://' + IP_LB + ':' + PORT_LB + '/'


app.run(host='0.0.0.0', port=8080)
