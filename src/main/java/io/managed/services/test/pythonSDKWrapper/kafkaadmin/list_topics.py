# This is failing because of a bug in the python SDK
#  the error
#  `TypeError: _from_openapi_data() missing 1 required positional argument: 'total'`
#  it appears to be related to the use of `all_of` in the openapi spec

import argparse
import os
import rhoas_kafka_instance_sdk
from rhoas_kafka_instance_sdk.api import topics_api
from rhoas_kafka_instance_sdk.model.sort_direction import SortDirection
from pprint import pprint
import dotenv
import auth.rhoas_auth as auth
import utils.get_kafka_admin_url

parser = argparse.ArgumentParser()
parser.add_argument('--kafka_id', help='ID of the Kafka instance', required=True)
parser.add_argument('--kafka_admin_url', help='URL of the Kafka Admin API', required=False)
parser.add_argument('--offset', help='Offset of the first record to return, zero-based', required=False, default=0)
parser.add_argument('--limit', help='Maximum number of records to return', required=False, default=1)
parser.add_argument('--size', help='Number of records per page', required=False, default=1)
parser.add_argument('--filter', help='Filter to apply when returning the list of topics', required=False)
parser.add_argument('--page', help='Page number', required=False, default=1)
parser.add_argument('--order', help='Order items are sorted', required=False)
parser.add_argument('--order_key', help='Order key to sort the topics by.', required=False)
parser.add_argument('--env_file', help='The env file', required=False, default='x.config.env')
args = parser.parse_args()

dotenv.load_dotenv(args.env_file)
offline_token = os.environ.get('OFFLINE_TOKEN')
openshift_base_uri = os.environ.get('OPENSHIFT_BASE_URI')

token = {}
token = auth.get_access_token(offline_token)

kafka_admin_url = utils.get_kafka_admin_url.get_kafka_admin_url(args.kafka_id)
configuration = rhoas_kafka_instance_sdk.Configuration(
    host = kafka_admin_url,
    access_token = token['access_token']
)

with rhoas_kafka_instance_sdk.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = topics_api.TopicsApi(api_client)
    offset = args.offset # int | Offset of the first record to return, zero-based (optional)
    limit = args.limit # int | Maximum number of records to return (optional)
    size = args.size # int | Number of records per page (optional)
    filter = "filter_example" # str | Filter to apply when returning the list of topics (optional)
    page = args.page # int | Page number (optional)
    order = SortDirection("asc") # SortDirection | Order items are sorted (optional)
    order_key = None # bool, date, datetime, dict, float, int, list, str, none_type | Order key to sort the topics by. (optional)

    try:
        api_response = api_instance.get_topics(offset=offset, limit=limit, size=size, filter=filter, page=page, order=order, order_key=order_key)
        pprint(api_response)
    except rhoas_kafka_instance_sdk.ApiException as e:
        print("Exception when calling TopicsApi->get_topics: %s\n" % e)