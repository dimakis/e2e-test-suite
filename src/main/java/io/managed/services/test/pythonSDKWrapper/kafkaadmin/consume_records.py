# This isn't operational on account of a bug in the python SDK.
# This bug involves the partition number being returned as a float instead of an int.

import argparse
import os

import dotenv
import rhoas_kafka_instance_sdk
from rhoas_kafka_instance_sdk.api import records_api
from rhoas_kafka_instance_sdk.model.record_included_property import RecordIncludedProperty
import auth.rhoas_auth as auth
from pprint import pprint

import utils.get_kafka_admin_url
from utils.sanitize_output import clean_datetime_bool

parser = argparse.ArgumentParser()
parser.add_argument('--kafka_id', help='The ID of the Kafka instance', required=True)
parser.add_argument('--topic_name', help='The name of the topic', required=True)
parser.add_argument('--partition', help='The partition number', required=False, default=1)
parser.add_argument('--offset', help='The offset number', required=False, default=0)
parser.add_argument('--limit', help='The limit number', required=False, default=1)
parser.add_argument('--max_value_length', help='The max value length', required=False, default=1)
parser.add_argument('--timestamp', help='The timestamp', required=False, default=None)
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
    topic_name = args.topic_name  # str | Topic name
    include = [
        RecordIncludedProperty("partition"),
    ] # [RecordIncludedProperty] | List of properties to include for each record in the response (optional)
    limit = args.limit # int | Limit the number of records fetched and returned (optional)
    max_value_length = args.max_value_length # int | Maximum length of string values returned in the response. Values with a length that exceeds this parameter will be truncated. When this parameter is not included in the request, the full string values will be returned. (optional)
    offset = int(args.offset) # int | Retrieve messages with an offset equal to or greater than this offset. If both `timestamp` and `offset` are requested, `timestamp` is given preference. (optional)
    partition = int(args.partition) # int | Retrieve messages only from this partition (optional)
    timestamp = args.timestamp # bool, date, datetime, dict, float, int, list, str, none_type | Retrieve messages with a timestamp equal to or later than this timestamp. If both `timestamp` and `offset` are requested, `timestamp` is given preference. (optional)
    passed_args = False
    print(f'args: {vars(args)}')
    args_vars = vars(args)
    for k, v in args_vars.items():
        print(f'k: {k}, v: {v}')
        # check if args are passed i.e. not the default values
        if v != parser.get_default(k):
            passed_args = True
            print(f'passed_args: {passed_args}')
        # passed_args = True
    if passed_args:
        try:
            print(f'partition: {partition}')
            pprint(f'args passed')
            api_response = api_instance.consume_records(topic_name, include=include, limit=limit, max_value_length=max_value_length, offset=offset, partition=partition)
            api_response = clean_datetime_bool(api_response.to_dict())
            pprint(api_response)
        except rhoas_kafka_instance_sdk.ApiException as e:
            print("Exception when calling RecordsApi->consume_records with arguments: %s\n" % e)
    else:
        try:
            print(f'partition: {partition}')
            pprint(f'no args')
            api_response = api_instance.consume_records(topic_name)
            api_response = clean_datetime_bool(api_response.to_dict())
            pprint(api_response)
        except rhoas_kafka_instance_sdk.ApiException as e:
            print("Exception when calling RecordsApi->consume_records: %s\n" % e)
