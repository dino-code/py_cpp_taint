from flask import Flask, jsonify, request, render_template, make_response
from flask_cors import CORS
import numpy as np
import matMult


app = Flask(__name__)
CORS(app)

@app.route('/', methods=['POST', 'GET'])
def hello():

    # if the request.method is a POST from the client (the website), then execute this code.
    if request.method == 'POST':

        # the POST request contains a form that the user submits. This code takes that data and places it in a dict.
#        data = request.form.to_dict()
        data = list(request.form.to_dict().values())
        data = [int(x) for x in data]

        mmat1 = data[0:9]
        mmat2 = data[9:18]
        
        print(mmat1, mmat2)
                    
        # perform matrix multiplication on the two matrices in C++ via my custom matMult module
        mat_mult = matMult.multiply(data)
        print('LOOK', mat_mult)
        
        response = make_response(render_template('index.html', data=mat_mult))
        # if there is a POST request, the website is returned along with data. To see how the data is manipulated,
        # you can go to the javascript code and look for {{ data }} because that's where the data ends up.
        return response

    # this just returns the visible website.
    return render_template('index.html')

def tamper_return(tampered_data):
    return render_template('index.html', data=tampered_data)
