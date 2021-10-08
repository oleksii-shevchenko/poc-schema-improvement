import click

from schema_registry import *

logging.basicConfig(level=logging.INFO)


@click.command()
@click.option('--registry_endpoint', '-r', required=True)
@click.option('--files', '-f', required=True)
def register_schemas(registry_endpoint, files):
    schema_registry = SchemaRegistry(registry_endpoint)
    for proto_path in parse_proto_paths(files):
        proto_schema = ProtoSchema(proto_path)
        schema_registry.register(proto_schema)


def parse_proto_paths(files) -> list:
    files_list = files.split(",")
    files_list = [file for file in files_list if file.endswith('.proto')]

    logging.info(f"Found {len(files_list)} changed protobuf schemas")

    return files_list


if __name__ == '__main__':
    register_schemas()
