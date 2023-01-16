import argparse
import os
from pprint import pprint
import rhoas_kafka_mgmt_sdk
from rhoas_kafka_mgmt_sdk.api import default_api
import dotenv
import auth.rhoas_auth as auth

dotenv.load_dotenv('x.config.env')
openshift_base_uri = os.environ.get('OPENSHIFT_BASE_URI')
offline_token = os.environ.get('OFFLINE_TOKEN')

def get_kafka_admin_url(kafka_id):
    token = {}
    token = auth.get_access_token(offline_token)
    configuration = rhoas_kafka_mgmt_sdk.Configuration(
        host = openshift_base_uri,
        access_token = token['access_token']
    )

    with rhoas_kafka_mgmt_sdk.ApiClient(configuration) as api_client:
        api_instance = default_api.DefaultApi(api_client)
        id = kafka_id  # str | The ID of record

        try:
            api_response = api_instance.get_kafka_by_id(id)
            # pprint(api_response['admin_api_server_url'])
            return api_response['admin_api_server_url']
        except rhoas_kafka_mgmt_sdk.ApiException as e:
            print("Exception when calling DefaultApi->get_kafka_by_id: %s\n" % e)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--kafka_id', help='The ID of Kafka to retrieve information about.', required=True)
    args = parser.parse_args()
    kafka_id = args.kafka_id
    get_kafka_admin_url(kafka_id)