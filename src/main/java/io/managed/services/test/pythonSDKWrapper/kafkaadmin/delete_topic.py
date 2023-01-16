import time
import rhoas_kafka_instance_sdk
from rhoas_kafka_instance_sdk.api import topics_api
from rhoas_kafka_instance_sdk.model.error import Error
from pprint import pprint
import utils.get_kafka_admin_url
import auth.rhoas_auth as auth
from pprint import pprint
import os
import argparse
import dotenv
from utils.sanitize_output import clean_datetime_bool

parser = argparse.ArgumentParser()

parser.add_argument('--kafka_id', help='The ID of Kafka to retrieve information about.', required=True)
parser.add_argument('--topic_name', help='The name of the topic to delete', required=True)
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

# Enter a context with an instance of the API client
with rhoas_kafka_instance_sdk.ApiClient(configuration) as api_client:
    api_instance = topics_api.TopicsApi(api_client)
    topic_name = args.topic_name # str | Name of the topic to delete

    try:
        api_instance.delete_topic(topic_name)
    except rhoas_kafka_instance_sdk.ApiException as e:
        print("Exception when calling TopicsApi->delete_topic: %s\n" % e)