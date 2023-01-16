import argparse
import os
import rhoas_kafka_instance_sdk
from rhoas_kafka_instance_sdk.api import records_api
from rhoas_kafka_instance_sdk.model.record import Record
from pprint import pprint
import dotenv
import auth.rhoas_auth as auth

import utils.get_kafka_admin_url
from utils.sanitize_output import clean_datetime_bool

parser = argparse.ArgumentParser()
parser.add_argument('--kafka_id', help='The ID of Kafka to retrieve information about.', required=True)
parser.add_argument('--topic_name', help='The name of the topic to produce to', required=True)
parser.add_argument('--record_value', help='The record value.', required=True)

parser.add_argument('--env_file', help='The env file', required=False, default='x.config.env')
args = parser.parse_args()

dotenv.load_dotenv(args.env_file)
offline_token = os.environ.get('OFFLINE_TOKEN')

token = {}
token = auth.get_access_token(offline_token)

kafka_admin_url = utils.get_kafka_admin_url.get_kafka_admin_url(args.kafka_id)
configuration = rhoas_kafka_instance_sdk.Configuration(
    host = kafka_admin_url,
    access_token = token['access_token']
)

with rhoas_kafka_instance_sdk.ApiClient(configuration) as api_client:
    api_instance = records_api.RecordsApi(api_client)
    topic_name = args.topic_name # str | Topic name
    record = Record(value=args.record_value) # Record |
    try:
        api_response = api_instance.produce_record(topic_name, record)
        api_response = clean_datetime_bool(api_response.to_dict())
        pprint(api_response)
    except rhoas_kafka_instance_sdk.ApiException as e:
        print("Exception when calling RecordsApi->produce_record: %s\n" % e)