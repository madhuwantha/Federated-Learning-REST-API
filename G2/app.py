from flask import Flask, request
import json
import requests
import ast
from model_train import train

app = Flask(__name__)

server_url = 'http://localhost:8000/'
this_host = 'http://localhost'
this_port = 8002


@app.route('/')
def hello():
    return "Gateway 2."


@app.route('/sendstatus', methods=['GET'])
def send_status():
    api_url = server_url + 'clientstatus';

    data = {'client_id': this_port, 'client_host': this_host}
    print(data)

    r = requests.post(url=api_url, json=data)
    print(r, r.status_code, r.reason, r.text)
    if r.status_code == 200:
        print("yeah")

    return "Status OK sent !"


@app.route('/send-model')
def send_model():
    file = open("local_model/mod.npy", 'rb')
    data = {'fname': 'model.npy', 'id': this_host + ':' + str(this_port)}
    files = {
        'json': ('json_data', json.dumps(data), 'application/json'),
        'model': ('model.npy', file, 'application/octet-stream')
    }

    req = requests.post(url=server_url + 'cmodel',
                        files=files)
    # print(req.text)
    return "Model sent !"


@app.route('/update-model', methods=['POST'])
def get_agg_model():
    if request.method == 'POST':
        file = request.files['model'].read()
        fname = request.files['json'].read()

        fname = ast.literal_eval(fname.decode("utf-8"))
        fname = fname['fname']
        print(fname)

        wfile = open("model_update/" + fname, 'wb')
        wfile.write(file)

        return "Model received!"
    else:
        return "No file received!"


@app.route('/modeltrain')
def model_train():
    train()
    return "Model trained successfully!"


if __name__ == '__main__':
    app.run(host='localhost', port=8002, debug=False, use_reloader=True)
