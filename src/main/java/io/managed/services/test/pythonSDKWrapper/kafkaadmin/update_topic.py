import argparse as argparse
import time
import rhoas_kafka_instance_sdk
from rhoas_kafka_instance_sdk.api import topics_api
from rhoas_kafka_instance_sdk.model.topic_settings import TopicSettings
from rhoas_kafka_instance_sdk.model.error import Error
from rhoas_kafka_instance_sdk.model.topic import Topic
from pprint import pprint
import dotenv
import auth.rhoas_auth as auth
from rhoas_kafka_instance_sdk.model.topic_settings import TopicSettings
import os
import utils.get_kafka_admin_url

parser = argparse.ArgumentParser()
parser.add_argument('--kafka_id', help='The ID of the Kafka instance', required=True)
parser.add_argument('--topic_name', help='The name of the Kafka topic to be created', required=True)
parser.add_argument('--partitions', help='The number of partitions for the topic', required=False)
parser.add_argument('--retention_size_bytes', help='The retention size for the topic', required=False)
parser.add_argument('--retention_period_ms', help='The retention period for the topic', required=False)
parser.add_argument('--cleanup_policy', help='The cleanup policy for the topic', required=False)
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
    # Create an instance of the API class
    api_instance = topics_api.TopicsApi(api_client)
    topic_name = "topicName_example" # str | Name of the topic to update
    topic_settings = TopicSettings(
        num_partitions=1,
        config=[
            ConfigEntry(
                key="o",
                value="value_example",
            ),
        ],
    ) # TopicSettings |

    # example passing only required values which don't have defaults set
    try:
        # Updates a single topic
        api_response = api_instance.update_topic(topic_name, topic_settings)
        pprint(api_response)
    except rhoas_kafka_instance_sdk.ApiException as e:
        print("Exception when calling TopicsApi->update_topic: %s\n" % e)