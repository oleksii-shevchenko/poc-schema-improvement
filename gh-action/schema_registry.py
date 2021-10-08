import requests
import logging
from domain import *

logging.basicConfig(level=logging.INFO)

TRANSITIVE_COMPATABILITY = {Compatability.FULL_TRANSITIVE,
                            Compatability.FORWARD_TRANSITIVE,
                            Compatability.BACKWARD_TRANSITIVE}


class SchemaRegistry:
    def __init__(self, endpoint, credentials):
        self.endpoint = endpoint
        self.credentials = credentials

    def __get_compatability_versions(self, proto_schema: ProtoSchema) -> list:
        if proto_schema.compatability() in TRANSITIVE_COMPATABILITY:
            return self.__get_versions(proto_schema.schema_name())
        else:
            return ["latest"]

    def __is_compatible_version(self, proto_schema: ProtoSchema, version) -> bool:
        endpoint = self.endpoint + f"/compatibility/subjects/{proto_schema.schema_name()}/versions/{version}"
        request_body = {"schema": proto_schema.schema(), "schemaType": "PROTOBUF"}

        response = requests.post(endpoint, json=request_body, auth=self.credentials)

        match response.status_code:
            case 200:
                return response.json()["is_compatible"]
            case 404:
                raise Exception("Schema Not Found")
            case 422:
                raise Exception("Invalid Protobuf Schema")
            case 500:
                raise Exception("Schema Registry Internal Error")
            case _:
                raise Exception("Unexpected Error")

    def __get_versions(self, subject) -> list:
        assert self.is_registered(subject)

        endpoint = self.endpoint + f"/subjects/{subject}/versions"
        return requests.get(endpoint, auth=self.credentials).json()

    def is_registered(self, subject) -> bool:
        endpoint = self.endpoint + f"/subjects/{subject}/versions/latest"
        return requests.get(endpoint, auth=self.credentials).status_code == 200

    def is_compatible(self, proto_schema: ProtoSchema) -> bool:
        assert self.is_registered(proto_schema.schema_name())

        for version in self.__get_compatability_versions(proto_schema):
            if not self.__is_compatible_version(proto_schema, version):
                logging.error(f"Schema {proto_schema.schema_name()} is not compatible with version {version}")
                return False
        return True

    def register(self, proto_schema: ProtoSchema, override_config=False):
        assert proto_schema.schema_name()

        if override_config or not self.is_registered(proto_schema.schema_name()):
            config_endpoint = self.endpoint + f"/config/{proto_schema.schema_name()}"
            config_request = {"compatibility": proto_schema.compatability().name}
            config_response = requests.put(config_endpoint, json=config_request, auth=self.credentials)

            assert config_response.status_code == 200

            logging.info(f"Set {proto_schema.compatability()} level for {proto_schema.schema_name()}")

        subject_endpoint = self.endpoint + f"/subjects/{proto_schema.schema_name()}/versions"
        subject_request = {"schema": proto_schema.schema(), "schemaType": "PROTOBUF"}
        response = requests.post(subject_endpoint, json=subject_request, auth=self.credentials)

        match response.status_code:
            case 200:
                logging.info(f"Registered schema with name {proto_schema.schema_name()}")
                return
            case 404:
                raise Exception("Not Found")
            case 409:
                raise Exception("Incompatible Schema")
            case 500:
                raise Exception("Schema Registry Internal Error")
            case _:
                raise Exception("Unknown Error")

    def compatible_or_register(self, proto_schema: ProtoSchema) -> bool:
        if self.is_registered(proto_schema.schema_name()):
            return self.is_compatible(proto_schema)
        else:
            self.register(proto_schema)
            return True
