import argparse
import os
import rhoas_kafka_instance_sdk
from rhoas_kafka_instance_sdk.api import acls_api
from rhoas_kafka_instance_sdk.model.acl_binding import AclBinding
from rhoas_kafka_instance_sdk.model.acl_operation import AclOperation
from rhoas_kafka_instance_sdk.model.acl_pattern_type import AclPatternType
from rhoas_kafka_instance_sdk.model.acl_permission_type import AclPermissionType
from rhoas_kafka_instance_sdk.model.acl_resource_type import AclResourceType
import dotenv
import auth.rhoas_auth as auth

import utils.get_kafka_admin_url

parser = argparse.ArgumentParser()
parser.add_argument('--kafka_id', help='The ID of Kafka to retrieve information about.', required=True)
parser.add_argument('--principal', help='ID for the Principal to create ACL for', required=True)
parser.add_argument('--kafka_admin_url', help='Kafka Admin URL', required=False)
parser.add_argument('--resource_type', help='Resource type', required=True)
parser.add_argument('--resource_name', help='Resource name', required=True)
parser.add_argument('--pattern_type', help='Pattern type', required=True)
parser.add_argument('--operation_type', help='Operation type', required=True)
parser.add_argument('--permission_type', help='Permission type', required=True)
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
    api_instance = acls_api.AclsApi(api_client)
    acl_binding = AclBinding(
        resource_type = AclResourceType(args.resource_type),
        resource_name = args.resource_name,
        pattern_type = AclPatternType(args.pattern_type),
        principal = f'User:{args.principal}',
        operation = AclOperation(args.operation_type),
        permission = AclPermissionType(args.permission_type)
        ) # AclBinding | ACL to create.
    try:
        api_instance.create_acl(acl_binding)
    except rhoas_kafka_instance_sdk.ApiException as e:
        print("Exception when calling AclsApi->create_acl: %s\n" % e)