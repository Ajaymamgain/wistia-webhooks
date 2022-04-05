import os
import uuid
from flask import Flask, request, abort, jsonify
from flask_restx import Resource, Api
import re
from functools import wraps
import json
import boto3
import shortuuid
from datetime import datetime

app = Flask(__name__)

authorizations = {
    'apikey': {
        'type': 'apiKey',
        'in': 'header',
        'name': 'X-API-KEY'
    }
}

api = Api(app, authorizations=authorizations)


def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):

        token = None

        if 'X-API-KEY' in request.headers:
            token = request.headers['X-API-KEY']

        if not token:
            return {'message': 'Token is missing.'}, 401

        if token != os.environ["TOKEN"]:
            return {'message': 'Your Token is wrong please contact amamgain@egencia.com'}, 401

        print('TOKEN: {}'.format(token))
        return f(*args, **kwargs)

    return decorated


@api.route('/wistia-events')
class events(Resource):
    @api.doc(security='apikey') ##//    @token_required
    def post(self):
        if request.method == 'POST':
            data = request.get_json()
            uuid = data['hook']['uuid']
            jsondump = data['events']
     
            try:
                s3 = boto3.client('s3')
                bucket_name = os.environ["BUCKET"]

                date = datetime.now()
                filename = str(uuid) + ".json"
                print(filename)
                data = {
                    'jsondump': jsondump, 'datetime': str(date), 'uuid':uuid
                }

                body = json.dumps(data, sort_keys=True, indent=5)

                s3.put_object(Bucket=bucket_name, Key="wistia-mkto/"+filename,
                              Body=body, ACL="private")

            except Exception as e:
                print(str(e))

            return {'data': data}

        else:
            abort(400)


if __name__ == '__main__':
    app.run()
