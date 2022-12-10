from flask import Flask, render_template, request
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from flask_sqlalchemy import SQLAlchemy
import os
from form import SubmitForm
from flask_bootstrap import Bootstrap
import boto3


application = Flask(__name__)
Bootstrap(application)
application.config['SECRET_KEY'] = 'jCOo4PAnmU6A0j2lpKeI-A'

# os.environ['AWS_PROFILE'] = "iamadmin-general"
# os.environ['AWS_DEFAULT_REGION'] = "us-east-1"

AWS_region = 'us-east-1'


dynamodb = boto3.resource('dynamodb', region_name=AWS_region)

def create_raffles_table(dynamodb=None):
    dynamodb = boto3.resource('dynamodb', region_name=AWS_region)
    #dynamodb = boto3.resource('dynamodb', endpoint_url="http://localhost:8000")
    # Table defination
    table = dynamodb.create_table(
        TableName='raffle',
        KeySchema=[
            {
                'AttributeName': 'name',
                'KeyType': 'HASH'  # Partition key
            },
            {
                'AttributeName': 'email',
                'KeyType': 'RANGE'  # Sort key
            }
        ],
        AttributeDefinitions=[
            {
                'AttributeName': 'name',
                # AttributeType defines the data type. 'S' is string type and 'N' is number type
                'AttributeType': 'S'
            },
            {
                'AttributeName': 'email',
                'AttributeType': 'S'
            },
        ],
        ProvisionedThroughput={
            # ReadCapacityUnits set to 10 strongly consistent reads per second
            'ReadCapacityUnits': 10,
            'WriteCapacityUnits': 10  # WriteCapacityUnits set to 10 writes per second
        }
    )

try:
    create_raffles_table()
except:
    print("Table already exixts")

# class comments(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     email = db.Column(db.String, unique=True, nullable=False)
#     name = db.Column(db.String, unique=True, nullable=False)

# with app.app_context():
#     db.create_all()

@application.route('/',methods=["GET","POST"])
def home():
    form = SubmitForm()
    flag = True
    raffle_inputs = dynamodb.Table('raffle')
    if form.validate_on_submit():
        response = raffle_inputs.scan()['Items']
        for items in response:   # Check to see if that email is already registered
            if form.email.data==items['email']:
                flag = False
                return render_template('error.html')
                print("User already registered")

        if flag:
           raffle_inputs.put_item(Item={
           'email': form.email.data,
           'name': form.name.data })
    return render_template('index.html',form=form)

@application.route('/error')
def error():
    return render_template('error.html')

if __name__=="__main__":
     application.run(debug=True)


