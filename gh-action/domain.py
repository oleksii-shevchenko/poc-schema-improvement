import re

from enum import Enum

option_parser = re.compile(r"@([-_.\w\d]+)=([-_.\w\d]+)")


class Compatability(Enum):
    NONE = 1
    FULL = 2
    FULL_TRANSITIVE = 3
    FORWARD = 4
    FORWARD_TRANSITIVE = 5
    BACKWARD = 6
    BACKWARD_TRANSITIVE = 7


class ProtoSchema:
    def __init__(self, file_path):
        self.__schema = ProtoSchema.__read_schema(file_path)
        self.__schema_options = ProtoSchema.__read_options(self.__schema)
        self.__file_path = file_path

    @staticmethod
    def __read_schema(path: str) -> str:
        schema_file = open(path)
        schema = schema_file.read()
        schema_file.close()
        return schema

    @staticmethod
    def __read_options(schema: str) -> dict:
        options = {}
        for line in schema.split('\n'):
            if line.startswith("//"):
                ProtoSchema.__parse_option(line, options)
            else:
                break
        return options

    @staticmethod
    def __parse_option(line: str, options: dict):
        option = option_parser.search(line)
        if option is not None:
            options[option.group(1)] = option.group(2)

    def compatability(self) -> Compatability:
        if "schema_compatability" in self.__schema_options:
            compatability = self.__schema_options["schema_compatability"].upper()
            return Compatability[compatability]
        else:
            return Compatability.NONE

    def schema_name(self) -> str:
        if "schema_name" in self.__schema_options:
            return self.__schema_options["schema_name"]
        else:
            return self.__file_path.replace("/", ".").replace(".proto", "")

    def schema(self):
        return self.__schema

    def file_name(self):
        return self.__file_path
