import click

from schema_registry import *

logging.basicConfig(level=logging.INFO)


@click.command()
@click.option('--fail_fast', '--ff', default=True, is_flag=True)
@click.option('--registry_endpoint', '-r', required=True)
@click.option('--files', '-f', required=True)
def check_schemas_compatability(registry_endpoint, files, fail_fast):
    schema_registry = SchemaRegistry(registry_endpoint)

    passed = True
    for proto_path in parse_proto_paths(files):
        proto_schema = ProtoSchema(proto_path)
        if schema_registry.compatible_or_register(proto_schema):
            logging.info(f"Schema {proto_schema.schema_name()} passed compatability check")
        else:
            passed = False
            if fail_fast:
                raise Exception(f"Schema {proto_schema.schema_name()} is not compatible")
            else:
                logging.error(f"Schema {proto_schema.schema_name()} is not compatible")

    if not passed:
        raise Exception("Schema compatability check failed")


def parse_proto_paths(files) -> list:
    files_list = files.split(",")
    files_list = [file for file in files_list if file.endswith('.proto')]

    logging.info(f"Found {len(files_list)} changed protobuf schemas")

    return files_list


if __name__ == '__main__':
    check_schemas_compatability()
