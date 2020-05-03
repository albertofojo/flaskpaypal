from flask import Flask, render_template, jsonify, request
import requests
import json
import paypal_manager

app = Flask(__name__)

# Routes


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/api/paypal/order/create', methods=['POST'])
def paypal_create_order():

    # TODO: Receive this data from... anywhere
    order_units = [{
        "currency_code": "EUR",
        "amount_value": 19.90,
        "payee_email_address": "one-single-person@personal.example.com",
        "description": "COOLEST T-SHIRT OF THE WORLD",
        "custom_id": "PAN467PAQ",
        "reference_id": "ORDER345535_01"
    },
        {
        "currency_code": "EUR",
        "amount_value": 9.90,
        "payee_email_address": "one-single-person@personal.example.com",
        "description": "COOL T-SHIRT, BUT LESS COOL THAN THE OTHER",
        "custom_id": "CAM389MKL",
        "reference_id": "ORDER345535_02"
    }]

    return paypal_manager.create_order(order_units)


@app.route('/api/paypal/order/<order_id>/capture', methods=['POST'])
def capture_order(order_id):

    return paypal_manager.capture_order(order_id)


if __name__ == '__main__':
    app.run(debug=True)
