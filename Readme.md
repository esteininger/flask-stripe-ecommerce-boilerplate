# Flask Stripe AJAX eEcommerce Example

![gif](https://i.imgur.com/jvwrlKd.gif)

[![Build Status](http://img.shields.io/travis/shama/gaze.svg)](https://travis-ci.org/shama/gaze) [![Build status](https://ci.appveyor.com/api/projects/status/vtx65w9eg511tgo4)](https://ci.appveyor.com/project/shama/gaze)

A simple, Flask & AJAX-powered eCommerce web app starter kit that uses Stripe to charge products based on what's added to a user's LocalStorage cart.

This example was built during Stripe's [Solutions Architect](https://stripe.com/jobs/listing/solutions-architect/1156461) interview process, and is freely available to anyone exploring Stripe checkout integration with Flask and JQuery/AJAX.

### Installation

This app requires Python 3+.

1. Install the dependencies:

```shell
pip install -r requirements.txt
```

2. Add your [Stripe keys](https://stripe.com/docs/testing) in config.py:

``` json
stripe_keys = {
    "secret_key": "",
    "publishable_key": ""
}
```

3. Run:

```python
python manage.py
```

## Overview

### How does it work?

1. When the page is loaded, the `publishable_key` you configured above is sent to the client via `render_template`:
``` python
@app.route('/')
def home_page():
    return render_template('index.html', key=stripe_keys['publishable_key'])
```
The LocalStorage key `cart` and cart HTML DOM is also cleared.

2. Clicking `Add to Cart` below each product will both append an object like `{amount: 74999, product: "iPhone 6"}` to the `cart` LocalStorage array, and push the product to the DOM `<ul class="dropdown-cart"/>` cart dropdown.

3. Clicking Checkout in the cart dropdown loops through the `cart` LocalStorage array and calculates the amount total, while concatenating the product strings:

``` javascript
var cart = JSON.parse(localStorage.getItem('cart'));
// build amount and product for stripe handler
cart.forEach(function(item, index) {
    totalAmount += item.amount;
    productStr += item.product;
    // only append and if not last one
    if (index !== cart.length - 1) {
        productStr += " and ";
    }
});
```
4. The total amount `int`, product `str`, and key (`data-key`) are sent to the client and passed to the stripeHandler function, which calls the `StripeCheckout.configure` method. This returns a `token` variable, which is then passed into an object, `data`.

``` javascript
function stripeHandlder(totalAmount, productStr) {
    var handler = StripeCheckout.configure({
        key: $('#stripeKey').attr("data-key"),
        locale: "auto",
        token: function(token) {
            var data = {
                "email": token.email,
                "stripe_token": token.id,
                "description": productStr,
                "amount": totalAmount
            }
        })
}
```

5. This object `data` is then sent to the Flask backend api: `/api/charge` where it first [creates a customer](https://stripe.com/docs/api/customers/create):

``` python
customer = stripe.Customer.create(
    email=json['email'],
    source=json['stripe_token']
)
```
Then passes the customer response to the [create charge method](https://stripe.com/docs/api/charges/create):

``` python
charge = stripe.Charge.create(
    customer=customer.id,
    amount=json['amount'],
    currency='usd',
    description=json['description']
)
```

6. This charge variable is then sent back to the frontend as a 200 json response where the AJAX `done` callback redirects the page to `/confirmation` with url arguments: `id`, `amount`, `email` and `product`.

7. Flask then pulls the arguments from that redirect URL and sends them directly to the client via `render_template`:

``` python
@app.route('/confirmation')
def confirmation_page():
    id = request.args.get('id', default="", type=str)
    amount = request.args.get('amount', default="", type=str)
    email = request.args.get('email', default="", type=str)
    product = request.args.get('product', default="", type=str)

    return render_template('confirmation.html', id=id, email=email, product=product, amount=amount)
```

Where the Success confirmation screen is finally displayed.

8. Double check that the charge was stored accurately in your [Stripe Dashboard](https://dashboard.stripe.com/test/payments)


## Technology Justification

The intent of this activity was to demonstrate the ability to consume technical documentation ([Stripe SDK](https://stripe.com/docs/libraries)) and produce a fully-functional POC (proof of concept) that can be handed off with minimal instruction.

These front end and backend selections were made due to both of their eases of use and simplicity. Both technology choices have the capability to scale assuming some code refactoring.

## What's next?

* Email confirmation with a link to the charge ID for review
* Storing email address with charge ID in a SQL database
* Request and store shipping information /w auto calculation of shipping cost
* Organize the code base into a Model View Controller structure
* Sentry error logging and email alerting
* Order purchase notifications emailed


## License
Copyright (c) 2019 Ethan Steininger  
Licensed under the MIT license.
