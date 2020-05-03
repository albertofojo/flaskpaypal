import requests
import json
import urllib.parse
from http import HTTPStatus
from flask import jsonify

# Paypal credentials

# TODO: Replace client-id and client-secret with your credentials
_client_id = "client-id"
_client_secret = "client-secret"

# Paypal URLs

_paypal_server = "https://api.sandbox.paypal.com"


def get_paypal_url(url_mode: str, order_id: str = None) -> str:
    if (url_mode == "TOKEN"):
        return urllib.parse.urljoin(_paypal_server, '/v1/oauth2/token')
    if (url_mode == "ORDERS"):
        if order_id is None:
            return urllib.parse.urljoin(_paypal_server, '/v2/checkout/orders')
        else:
            return urllib.parse.urljoin(_paypal_server, f"/v2/checkout/orders/{order_id}/capture")


def get_token():

    d = {"grant_type": "client_credentials"}
    h = {"Accept": "application/json", "Accept-Language": "en_US"}

    r = requests.post(get_paypal_url("TOKEN"),
                      data=d,
                      auth=(_client_id, _client_secret),
                      headers=h)

    return r.json()['access_token']


def build_create_order_request_body(order_units):
    """Method to create body with a custom PAYEE (receiver)
       Info: https://developer.paypal.com/docs/api/orders/v2/

       You can patch these attributes and objects to complete these operations:
          intent — replace.
          purchase_units — replace, add.
          purchase_units[].custom_id — replace, add, remove.
          purchase_units[].description — replace, add, remove.
          purchase_units[].payee.email — replace.
          purchase_units[].shipping.name — replace, add.
          purchase_units[].shipping.address — replace, add.
          purchase_units[].soft_descriptor — replace, remove.
          purchase_units[].amount — replace.
          purchase_units[].invoice_id — replace, add, remove.
          purchase_units[].payment_instruction — replace.
          purchase_units[].payment_instruction.disbursement_mode — replace. (By default, disbursement_mode is INSTANT.)
          purchase_units[].payment_instruction.platform_fees — replace, add, remove.
    """

    request_body = {}

    request_body['intent'] = "CAPTURE"
    request_body['purchase_units'] = []

    for order_unit in order_units:
        purchase_unit = {}

        purchase_unit['amount'] = {
            "currency_code": f"{order_unit['currency_code']}",
            "value": f"{order_unit['amount_value']}"
        }

        purchase_unit['payee'] = {
            "email_address": f"{order_unit['payee_email_address']}"
        }

        purchase_unit['description'] = f"{order_unit['description']}"
        purchase_unit['reference_id'] = f"{order_unit['reference_id']}"

        if (order_unit['custom_id'] is not None):
            purchase_unit['custom_id'] = order_unit['custom_id']

        request_body['purchase_units'].append(purchase_unit)

    return request_body


def create_order(order_units):
    """Function to create a Paypal Order.

    Args:
        order_units: object to store order information::
          [
            {
              {
                "currency_code": "EUR",
                "amount_value": 19.90,
                "payee_email_address": "one-single-person@personal.example.com",
                "description": "unit description",
                "custom_id": "unic custom id - not related with paypal",
                "reference_id": "unit reference id - not related with paypal"
              }
            },
            ...
          ]

    Returns:
        Json object: {'orderID': id}
    """

    token = get_token()
    request_body = build_create_order_request_body(order_units)

    d = json.dumps(request_body)
    h = {
        "Content-Type": "application/json",
        "Prefer": "return=representation",
        "Authorization": f"Bearer {token}"}

    r = requests.post(get_paypal_url("ORDERS"),
                      data=d,
                      headers=h)

    if r.status_code == HTTPStatus.CREATED:
        print(f"Order {r.json()['id']} created successfully!")
    else:
        print(r.text)

    return jsonify({'orderID': r.json()['id']})


def capture_order(order_id: str):
    """Function to capture a Paypal Order.

      Args:
          order_id: id of created order

      Returns:
          paypal response

      """
    token = get_token()

    h = {"Content-Type": "application/json",
          "Authorization": f"Bearer {token}"}

     r = requests.post(get_paypal_url("ORDERS", order_id),
                        headers=h)

      response = r.json()

       if r.status_code == HTTPStatus.CREATED:
            print(f"Order {response['id']} captured successfully!")
        else:
            print(r.text)

        return response
