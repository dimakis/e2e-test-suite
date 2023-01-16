#!/usr/bin/python

import argparse
import json
import os
import rhoas_kafka_instance_sdk
from rhoas_kafka_instance_sdk.api import topics_api
from rhoas_kafka_instance_sdk.model.new_topic_input import NewTopicInput
from pprint import pprint
import dotenv
import auth.rhoas_auth as auth
from rhoas_kafka_instance_sdk.model.topic_settings import TopicSettings

import utils.get_kafka_admin_url

parser = argparse.ArgumentParser()
parser.add_argument('--kafka_id', help='The ID of the Kafka instance', required=True)
parser.add_argument('--topic_name', help='The name of the Kafka topic to be created', required=True)
parser.add_argument('--kafka_admin_url', help='The URL of the Kafka instance', required=False)
parser.add_argument('--partitions', help='The number of partitions for the topic', required=False, default=1)
parser.add_argument('--retention_size_bytes', help='The retention size for the topic', required=False)
parser.add_argument('--retention_period_ms', help='The retention period for the topic', required=False)
parser.add_argument('--cleanup_policy', help='The cleanup policy for the topic', required=False)
parser.add_argument('--openshift_offline_token', help='The offline token for the OpenShift cluster', required=False)
parser.add_argument('--env_file', help='The env file', required=False, default='x.config.env')
args = parser.parse_args()

dotenv.load_dotenv(args.env_file)
offline_token = os.environ.get('OFFLINE_TOKEN')

token = {}
token = auth.get_access_token(offline_token)

kafka_admin_url = utils.get_kafka_admin_url.get_kafka_admin_url(args.kafka_id)
# kafka_admin_url = utils.get_kafka_admin_url.get_kafka_admin_url("cerabvp4ghn16ranm74g")
configuration = rhoas_kafka_instance_sdk.Configuration(
    host = kafka_admin_url,
    access_token = token['access_token']
)

with rhoas_kafka_instance_sdk.ApiClient(configuration) as api_client:
    api_instance = topics_api.TopicsApi(api_client)
    # if flags are set, then set the topic settings
    if args.partitions or args.retention_size_bytes or args.retention_period_ms or args.cleanup_policy:
        topic_settings = TopicSettings(
            partitions = args.partitions,
            retention_size_bytes = args.retention_size_bytes,
            retention_period_ms = args.retention_period_ms,
            cleanup_policy = args.cleanup_policy
        )
        new_topic_input = NewTopicInput(
            name= args.topic_name,
            settings= topic_settings
        )
    else:
        new_topic_input = NewTopicInput(
            name= args.topic_name,
            settings= TopicSettings()
        ) # NewTopicInput | Topic to create.
    try:
        # Creates a new topic
        api_response = api_instance.create_topic(new_topic_input)
        # api_response = json.loads(api_response)
        # convert python object to json string
        api_resp = api_response.to_dict()
        # api_response = json.dumps(api_response)
        for key, value in api_resp.items():
            if value is isinstance(value, bool):
               value = str(value).lower()
            if key == 'is_internal':
                api_resp[key] = str(value).lower()
        # pprint(f'{json.dumps(api_resp)})')
        pprint(api_resp)
    except rhoas_kafka_instance_sdk.ApiException as e:
        print("Exception when calling TopicsApi->create_topic: %s\n" % e)