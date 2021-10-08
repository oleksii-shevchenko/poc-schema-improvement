import json

from schema_registry import *

logging.basicConfig(level=logging.INFO)


# @click.command()
# @click.argument('registry_endpoint')
# @click.argument('fail_fast')
# @click.argument('files')
def check_schemas_compatability(registry_endpoint, files, fail_fast):
    schema_registry = SchemaRegistry(registry_endpoint, load_credentials())

    passed = True
    for proto_path in parse_proto_paths(files):
        proto_schema = ProtoSchema(proto_path)
        if schema_registry.compatible_or_register(proto_schema):
            logging.info("Schema %s passed compatability check", proto_schema.schema_name())
        else:
            passed = False
            if fail_fast:
                raise Exception(f"Schema {proto_schema.schema_name()} is not compatible")
            else:
                logging.error(f"Schema {proto_schema.schema_name()} is not compatible")

    if not passed:
        raise Exception("Schema compatability check failed")


def load_credentials():
    with open('credentials.json') as credentials_file:
        data = json.load(credentials_file)
        return data["user"], data["key"]


def parse_proto_paths(files) -> list:
    files_list = json.loads(files)
    files_list = [file for file in files_list if file.endswith('.proto')]

    logging.info(f"Found {len(files_list)} changed protobuf schemas")

    return files_list


if __name__ == '__main__':
    check_schemas_compatability()
