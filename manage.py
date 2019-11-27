from flask import Flask, render_template, request
import stripe
# local files
from config import stripe_keys
from helpers import success_response, error_response, check_json


app = Flask(__name__)


@app.route('/')
def home_page():
    return render_template('index.html', key=stripe_keys['publishable_key'])


@app.route('/confirmation')
def confirmation_page():
    id = request.args.get('id', default="", type=str)
    amount = request.args.get('amount', default="", type=str)
    email = request.args.get('email', default="", type=str)
    product = request.args.get('product', default="", type=str)

    return render_template('confirmation.html', id=id, email=email, product=product, amount=amount)


@app.route('/api/charge', methods=['POST'])
def charge_api():
    if request.method == 'POST':
        # grab json from request body
        json = request.json
        # check if all keys present, return error if any missing
        result = check_json(
            json, ['email', 'stripe_token', 'description', 'amount'])
        if result:
            return error_response("missing {}".format(result))
        # add stripe api key
        stripe.api_key = stripe_keys['secret_key']
        try:
            # create customer ID
            customer = stripe.Customer.create(
                email=json['email'],
                source=json['stripe_token']
            )
            # create charge
            charge = stripe.Charge.create(
                customer=customer.id,
                amount=json['amount'],
                currency='usd',
                description=json['description']
            )
            # jsonify'd 200 success
            return success_response(charge)

        except stripe.error.StripeError as e:
            # jsonify'd 500 error
            return error_response(e)


if __name__ == '__main__':
    app.run(host="localhost", port=5008, debug=True)
