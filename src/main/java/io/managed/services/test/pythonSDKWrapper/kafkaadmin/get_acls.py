# not working because of a deserialization issue with the SDK
import os
import argparse
import dotenv
import rhoas_kafka_instance_sdk
from rhoas_kafka_instance_sdk.api import acls_api
from rhoas_kafka_instance_sdk.model.sort_direction import SortDirection
from rhoas_kafka_instance_sdk.model.acl_operation import AclOperation
from rhoas_kafka_instance_sdk.model.acl_pattern_type import AclPatternType
from rhoas_kafka_instance_sdk.model.acl_permission_type import AclPermissionType
from rhoas_kafka_instance_sdk.model.acl_resource_type import AclResourceType
from pprint import pprint
import auth.rhoas_auth as auth

import utils.get_kafka_admin_url

parser = argparse.ArgumentParser()
parser.add_argument('--kafka_id', help='The ID of Kafka to retrieve information about.', required=True)
parser.add_argument('--env_file', help='The env file', required=False, default='x.config.env')
parser.add_argument('--resource_type', help='The resource type.', required=False, default='TOPIC')
parser.add_argument('--resource_name', help='The resource name.', required=False)
parser.add_argument('--principal', help='The ID of the principal. Use a "*" to return information about all principals', required=False)
parser.add_argument('--operation', help='The operation.', required=False, default=None)
parser.add_argument('--permission', help='The permission.', required=False, default=None)
parser.add_argument('--page', help='The page number.', required=False, default=1)
parser.add_argument('--size', help='The page size.', required=False, default=100)
parser.add_argument('--order', help='The order.', required=False, default='asc')
parser.add_argument('--order_key', help='The order key.', required=False, default=None)
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
    resource_type =args.resource_type
    resource_name = args.resource_name  # str | ACL Resource Name Filter (optional)
    # pattern_type = AclPatternType(args.pattern_type),
    principal = f'User:{args.principal}'  # str | ACL Principal Filter. Either a specific user or the wildcard user `User:*` may be provided. - When fetching by a specific user, the results will also include ACL bindings that apply to all users. - When deleting, ACL bindings to be delete must match the provided `principal` exactly. (optional) if omitted the server will use the default value of ""
    # operation = AclOperation(args.operation_type),
    # permission = AclPermissionType(args.permission_type)
    page = 1 # int | Page number (optional)
    size = 1 # int | Number of records per page (optional)
    order = SortDirection("asc") # SortDirection | Order items are sorted (optional)
    order_key = args.order_key # bool, date, datetime, dict, float, int, list, str, none_type |  (optional)
    try:
        # api_response = api_instance.get_acls(resource_type=resource_type, resource_name=resource_name, pattern_type=pattern_type, principal=principal, operation=operation, permission=permission, page=page, size=size, order=order, order_key=order_key)
        api_response = api_instance.get_acls(resource_type=resource_type, principal=principal, page=page, size=size, order=order, order_key=order_key)
        pprint(api_response)
    except rhoas_kafka_instance_sdk.ApiException as e:
        print("Exception when calling AclsApi->get_acls: %s\n" % e)
