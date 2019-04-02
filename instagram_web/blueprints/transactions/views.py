from flask import Blueprint, Flask, redirect, url_for, render_template, request, flash
import os
from os.path import join, dirname
from models.image import Image
from models.transaction import Transaction
from models.user import User
from dotenv import load_dotenv
from flask_login import current_user, login_required
import braintree
from helpers import generate_client_token, transact, find_transaction, send_transaction_email
from app import app

transactions_blueprint = Blueprint('transactions',
                             __name__,
                             template_folder='templates')

TRANSACTION_SUCCESS_STATUSES = [
    braintree.Transaction.Status.Authorized,
    braintree.Transaction.Status.Authorizing,
    braintree.Transaction.Status.Settled,
    braintree.Transaction.Status.SettlementConfirmed,
    braintree.Transaction.Status.SettlementPending,
    braintree.Transaction.Status.Settling,
    braintree.Transaction.Status.SubmittedForSettlement
]


@transactions_blueprint.route('/', methods=['GET'])
def index():
    return redirect(url_for('new_checkout'))



@transactions_blueprint.route('/<image_id>/new', methods=['GET'])
@login_required
def new(image_id):
    image = Image.get_by_id(image_id)
    client_token = generate_client_token()

    return render_template('transactions/new.html', image=image, client_token=client_token)


@transactions_blueprint.route('/<image_id>/<transaction_id>', methods=['GET'])
@login_required
def show_checkout(transaction_id, image_id):
    image = Image.get_by_id(image_id)
    transaction = find_transaction(transaction_id)
    user = User.get_by_id(current_user.id)
    photographer = image.user
    result = {}
    if transaction.status in TRANSACTION_SUCCESS_STATUSES:
        result = {
            'header': 'Sweet Success!',
            'icon': url_for('static', filename="images/ok_icon.png"),
            'message': 'Your test transaction has been successfully processed. You will receive a payment receipt via email shortly.'
        }
        t = Transaction(amount=transaction.amount,
                        braintree_id=transaction.id, user=user, image=image)
        
        if t.save():
            flash(f"Transaction successfully created.")
            send_transaction_email(
                user, transaction.amount, transaction.credit_card_details.card_type, transaction.credit_card_details.last_4, photographer, transaction.id)
        else:
            return render_template('transactions/show.html', transaction=transaction, result=result, errors=t.errors)

    else:
        result = {
            'header': 'Transaction Failed',
            'icon': url_for('static', filename="images/fail_icon.png"),
            'message': 'Your test transaction has a status of ' + transaction.status + '. See the Braintree API response and try again.'
        }

    return render_template('transactions/show.html', transaction=transaction, result=result)


@transactions_blueprint.route('/checkouts/<image_id>', methods=['POST'])
def create_checkout(image_id):
    result = transact({
        'amount': request.form['amount'],
        'payment_method_nonce': request.form['payment_method_nonce'],
        'options': {
            "submit_for_settlement": True
        }
    })

    if result.is_success or result.transaction:
         return redirect(url_for('transactions.show_checkout', transaction_id=result.transaction.id, image_id=image_id))
    else:
        return redirect(url_for('transactions.show_checkout', transaction_id=result.transaction.id, image_id=image_id))
