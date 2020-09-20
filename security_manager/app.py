from flask import Flask, request
import requests, json
import ast
from main_server import model_aggregation
from datetime import datetime
import glob

app = Flask(__name__)


@app.route('/')
def hello():
    return "Security manager running !"


@app.route('/clientstatus', methods=['GET', 'POST'])
def client_status():
    if request.method == 'POST':
        client_port = request.json['client_id']
        client_host = request.json['client_host']

        with open('clients.txt', 'a+') as f:
            f.write(client_host + ':' + str(client_port) + '/\n')

        print(client_port)

        if client_port:
            serverack = {'server_ack': '1'}
            # response = requests.post( url, data=json.dumps(serverack), headers={'Content-Type': 'application/json'} )
            return str(serverack)
        else:
            return "Client status not OK!"
    else:
        return "Client GET request received!"


@app.route('/cmodel', methods=['POST'])
def get_model():
    if request.method == 'POST':
        file = request.files['model'].read()
        fname = request.files['json'].read()
        # cli = request.files['id'].read()

        fname = ast.literal_eval(fname.decode("utf-8"))
        cli = fname['id'] + '\n'
        fname = fname['fname']

        # with open('clients.txt', 'a+') as f:
        # 	f.write(cli)

        now = datetime.now()
        now = str(now).replace(" ", "-").replace(":", "-").replace(".", "-")

        print(fname)
        wfile = open("client_models/" + str(fname).split(".")[0] + "-" + now + "." + str(fname).split(".")[1], 'wb')
        wfile.write(file)

        return "Model received!"
    else:
        return "No file received!"


@app.route('/aggregate_models')
def perform_model_aggregation():
    model_aggregation()
    return 'Model aggregation done!\nGlobal model written to persistent storage.'


@app.route('/send-model-to-clients')
def send_agg_to_clients():
    clients = ''
    with open('clients.txt', 'r') as f:
        clients = f.read()
    clients = clients.split('\n')

    for c in clients:
        if c != '':
            # file = glob.glob("persistent_storage/*.h5")[0]
            file = open("persistent_storage/agg_model.h5", 'rb')
            data = {'fname': 'agg_model.h5'}
            files = {
                'json': ('json_data', json.dumps(data), 'application/json'),
                'model': ('agg_model.h5', file, 'application/octet-stream')
            }

            print(c + 'aggmodel')
            req = requests.post(url=c + 'update-model', files=files)
            print(req.status_code)

    # print(req.text)
    return "Aggregated model sent !"


if __name__ == '__main__':
    app.run(host='localhost', port=8000, debug=False, use_reloader=True)
