from flask import Flask, jsonify, render_template, request
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

boto3.setup_default_session(profile_name='iamadmin-general')
dynamodb = boto3.resource(service_name='dynamodb')

tablename="newraffletable"


def create_raffles_table(dynamodb):

    table_names = [table.name for table in dynamodb.tables.all()]

    if tablename in table_names:
        print('table', tablename, 'exists')

    #print(response)

    else:

        #dynamodb = boto3.resource('dynamodb', endpoint_url="http://localhost:8000")
        # Table defination
        table = dynamodb.create_table(
            TableName=tablename,

            AttributeDefinitions=[
                {
                    'AttributeName': 'id',
                    # AttributeType defines the data type. 'S' is string type and 'N' is number type
                    'AttributeType': 'N'
                },
                {
                    'AttributeName': 'name',
                    # AttributeType defines the data type. 'S' is string type and 'N' is number type
                    'AttributeType': 'S'
                },

            ],

            KeySchema=[
                {
                    'AttributeName': 'id',
                    'KeyType': 'HASH'  # Partition key
                },
                {
                    'AttributeName': 'name',
                    'KeyType': 'RANGE'  # Sort key
                }

            ],
            ProvisionedThroughput={
                # ReadCapacityUnits set to 10 strongly consistent reads per second
                'ReadCapacityUnits': 10,
                'WriteCapacityUnits': 10  # WriteCapacityUnits set to 10 writes per second
            }
        )



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
    raffle_inputs = dynamodb.Table(tablename)
    if form.validate_on_submit():
        try:
            response = raffle_inputs.scan()(Item={'id':1, 'name':form.name.data})
            flag = False
            return render_template('error.html')
            print("User already registered")
        except:
           raffle_inputs.put_item(Item={'id':1,
           'email': form.email.data,
           'name': form.name.data })
    return render_template('index.html',form=form)

@application.route('/scan',methods=["GET","POST"])
def scan():
    flag = True
    raffle_outputs = dynamodb.Table(tablename)
    raffle_outputs.get_item(Item={'id':1})
    return (jsonify(raffle_outputs))

@application.route('/query',methods=["GET","POST"])
def query():
    recname = request.args.get('name')
    flag = True
    raffle_outputs = dynamodb.Table(tablename)
    raffle_outputs.query(Item={'id':1, 'name':recname})
    return (jsonify(raffle_outputs))

@application.route('/error')
def error():
    return render_template('error.html')

if __name__=="__main__":
    create_raffles_table(dynamodb)
    application.run()





