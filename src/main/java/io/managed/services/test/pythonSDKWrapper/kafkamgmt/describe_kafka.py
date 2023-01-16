import argparse
import datetime
import json
import os
import time
import rhoas_kafka_mgmt_sdk
from rhoas_kafka_mgmt_sdk.api import default_api
from rhoas_kafka_mgmt_sdk.model.kafka_request import KafkaRequest
from rhoas_kafka_mgmt_sdk.model.error import Error
from pprint import pprint
import dotenv
import auth.rhoas_auth as auth

from utils.sanitize_output import clean_datetime_bool

parser = argparse.ArgumentParser()
parser.add_argument('--kafka_id', help='The ID of Kafka to retrieve information about.', required=True)
parser.add_argument('--env_file', help='The env file', required=False, default='x.config.env')
args = parser.parse_args()

dotenv.load_dotenv(args.env_file)
offline_token = os.environ.get('OFFLINE_TOKEN')
openshift_base_uri = os.environ.get('OPENSHIFT_BASE_URI')

token = {}
token = auth.get_access_token(offline_token)

configuration = rhoas_kafka_mgmt_sdk.Configuration(
    host = openshift_base_uri,
    access_token = token['access_token']
)

with rhoas_kafka_mgmt_sdk.ApiClient(configuration) as api_client:
    api_instance = default_api.DefaultApi(api_client)
    id = args.kafka_id # str | The ID of record

    try:
        api_response = api_instance.get_kafka_by_id(id).to_dict()
        api_response = clean_datetime_bool(api_response)
        print(api_response)
    except rhoas_kafka_mgmt_sdk.ApiException as e:
        print("Exception when calling DefaultApi->get_kafka_by_id: %s\n" % e)