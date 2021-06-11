# Description
"""
Hive Nuclei connector class
Author: Vladimir Ivanov
License: MIT
Copyright 2021, Hive Nuclei connector
"""

# Import
from dataclasses import dataclass
from typing import Optional, List, Dict
from datetime import datetime
from re import compile, search, finditer, MULTILINE
from urllib.parse import urlparse, ParseResult
from uuid import UUID
from hive_library import HiveLibrary
from hive_library.enum import RecordTypes
from hive_library.rest import HiveRestApi, AuthenticationError
from socket import gethostbyname, gethostbyaddr, herror
from ipaddress import IPv4Address, ip_address
from marshmallow import fields, pre_load, post_load, EXCLUDE
from marshmallow.exceptions import ValidationError
from marshmallow import Schema as MarshmallowSchema
from json import loads, JSONDecodeError

# Authorship information
__author__ = "Vladimir Ivanov"
__copyright__ = "Copyright 2021, Hive Nuclei connector"
__credits__ = [""]
__license__ = "MIT"
__version__ = "0.0.1b1"
__maintainer__ = "Vladimir Ivanov"
__email__ = "ivanov.vladimir.mail@gmail.com"
__status__ = "Development"


@dataclass
class NucleiData:
    date: Optional[datetime] = None
    template_id: Optional[str] = None
    template_name: Optional[str] = None
    author: Optional[str] = None
    severity: str = "info"
    tags: Optional[str] = None
    reference: Optional[str] = None
    description: Optional[str] = None
    type: Optional[str] = None
    host: Optional[str] = None
    ip: Optional[IPv4Address] = None
    address: Optional[str] = None
    scheme: str = "http"
    port: Optional[int] = None
    matched: Optional[str] = None
    extracted_results: Optional[List[str]] = None

    class Schema(MarshmallowSchema):
        date = fields.DateTime(
            missing=None,
            data_key="timestamp",
        )
        template_id = fields.String(missing=None, data_key="templateID")
        template_name = fields.String(missing=None, data_key="info:name")
        author = fields.String(missing=None, data_key="info:author")
        severity = fields.String(missing="info", data_key="info:severity")
        tags = fields.String(missing=None, data_key="info:tags")
        reference = fields.String(missing=None, data_key="info:reference")
        description = fields.String(missing=None, data_key="info:description")
        type = fields.String(missing=None)
        host = fields.String(missing=None)
        ip = fields.IPv4(missing=None)
        matched = fields.String(missing=None)
        extracted_results = fields.List(fields.String, missing=None)

        @pre_load(pass_many=False)
        def pre_load_data(self, data, many, **kwargs):
            if "info" in data:
                if isinstance(data["info"], Dict):
                    for key in data["info"]:
                        data[f"info:{key}"] = data["info"][key]
                    del data["info"]
            else:
                if "template" in data:
                    data["templateID"] = data["template"]
                    del data["template"]
                if "name" in data:
                    data["info:name"] = data["name"]
                    del data["name"]
                if "author" in data:
                    data["info:author"] = data["author"]
                    del data["author"]
                if "severity" in data:
                    data["info:severity"] = data["severity"]
                    del data["severity"]
                if "tags" in data:
                    data["info:tags"] = data["tags"]
                    del data["tags"]
                if "reference" in data:
                    data["info:reference"] = data["reference"]
                    del data["reference"]
                if "description" in data:
                    data["info:description"] = data["description"]
                    del data["description"]
            return data

        @post_load
        def post_load_data(self, data, **kwargs):
            return NucleiData(**data)


class HiveNuclei:
    def __init__(
        self,
        username: Optional[str] = None,
        password: Optional[str] = None,
        server: Optional[str] = None,
        proxy: Optional[str] = None,
        project_id: Optional[UUID] = None,
        host_tag: Optional[str] = None,
        port_tag: Optional[str] = None,
        auto_tag: bool = False,
        resolve: bool = False,
    ):
        """
        Init HiveNuclei class
        :param username: Hive username, example: 'test@mail.com'
        :param password: Hive password, example: 'strong_password'
        :param server: Hive server url, example: 'https://hive.corp.company.com:443'
        :param proxy: Proxy server url, example: 'http://127.0.0.1:8080'
        :param project_id: Hive project id, example: '2b10f974-3215-4a4e-9fb7-04be8ac5202e'
        :param host_tag: Hive tag for host, example: 'nuclei_host'
        :param port_tag: Hive tag for port, example: 'nuclei_port'
        :param auto_tag: Automatically add tag for host and port, tag example: 'nuclei_<nuclei_severity>'
        :param resolve: Resolve host name and ip address
        """
        self.host_tag = host_tag
        self.port_tag = port_tag
        self.auto_tag = auto_tag
        self.resolve = resolve
        config: HiveLibrary.Config = HiveLibrary.load_config()
        if config.project_id is None and project_id is None:
            print("Hive project id is not set! Please set Hive project id!")
            exit(1)
        else:
            if project_id is not None:
                self.project_id = project_id
            else:
                self.project_id = config.project_id
        if config.server is None and server is None:
            print("Hive server url is not set! Please set Hive server url!")
            exit(2)
        try:
            self.hive_api: HiveRestApi = HiveRestApi(
                username=username,
                password=password,
                server=server,
                proxy=proxy,
                project_id=self.project_id,
            )
        except AuthenticationError as error:
            print(f"Authentication Error: {error}")
            exit(3)

    @staticmethod
    def _parse_nuclei_matched(data_list: List[NucleiData]) -> List[NucleiData]:
        """
        Parse matched field in List of NucleiData objects
        :param data_list: List of NucleiData objects, example:
        [NucleiData(date=datetime.datetime(2021, 6, 7, 12, 54, 47), template_id='apache-version-detect',
                    template_name=None, author=None, severity='info', tags=None, reference=None, description=None,
                    type='http', host=None, ip=None, address=None, scheme='http', port=None,
                    matched='http://server.ispa.cnr.it/ [Apache/2.4.7 (Ubuntu)]', extracted_results=None)]
        :return: List of NucleiData objects, example:
        [NucleiData(date=datetime.datetime(2021, 6, 7, 12, 54, 47), template_id='apache-version-detect',
                    template_name=None, author=None, severity='info', tags=None, reference=None, description=None,
                    type='http', host=None, ip=None, address='server.ispa.cnr.it', scheme='http', port=80,
                    matched='http://server.ispa.cnr.it/', extracted_results=['Apache/2.4.7 (Ubuntu)'])]
        """
        for index in range(len(data_list)):
            matched: str = data_list[index].matched
            extracted_search = search(
                r"^(?P<matched>.*) \[(?P<extracted>.*)\]$", matched
            )
            if extracted_search:
                data_list[index].matched = str(extracted_search.group("matched"))
                data_list[index].extracted_results = [
                    str(extracted_search.group("extracted"))
                ]
                matched: str = data_list[index].matched
            urlparse_result: ParseResult = urlparse(matched)
            if urlparse_result.hostname is not None:
                data_list[index].scheme = urlparse_result.scheme
                data_list[index].address = urlparse_result.hostname
                if urlparse_result.port is None:
                    if urlparse_result.scheme == "http":
                        data_list[index].port = 80
                    elif urlparse_result.scheme == "https":
                        data_list[index].port = 443
                    elif urlparse_result.scheme == "ftp":
                        data_list[index].port = 21
                else:
                    data_list[index].port = urlparse_result.port
            else:
                data_list[index].scheme = data_list[index].type
                matched_regex = (
                    r"^(?P<address>[0-9a-zA-Z.-_:]{3,64}):"
                    r"(?P<port>[0-9]{1,4}|[1-5][0-9]{4}|6[0-4][0-9]{3}|65[0-4][0-9]{2}|655[0-2][0-9]|6553[0-5])$"
                )
                matched_search = search(matched_regex, matched)
                if matched_search:
                    data_list[index].address = str(matched_search.group("address"))
                    data_list[index].port = int(matched_search.group("port"))
            if isinstance(data_list[index].ip, IPv4Address):
                data_list[index].address = str(data_list[index].ip)
        return data_list

    def _parse_nuclei_console_output(self, lines: str) -> List[NucleiData]:
        """
        Parse nuclei console output
        :param lines: Nuclei console output string, example: '[[36m2021-06-07 12:54:47[0m] [[92mapache-version-detect[0m] [[94mhttp[0m] [[34minfo[0m] http://server.ispa.cnr.it/ [[96mApache/2.4.7 (Ubuntu)[0m]'
        :return: List of NucleiData objects, example:
        [NucleiData(date=datetime.datetime(2021, 6, 7, 12, 54, 47), template_id='apache-version-detect',
                    template_name=None, author=None, severity='info', tags=None, reference=None, description=None,
                    type='http', host=None, ip=None, address='server.ispa.cnr.it', scheme='http', port=80,
                    matched='http://server.ispa.cnr.it/', extracted_results=['Apache/2.4.7 (Ubuntu)'])]
        """
        results: List[NucleiData] = list()
        ansi_escape = compile(r"(\x9B|\x1B\[)[0-?]*[ -\/]*[@-~]")
        ansi_escaped_lines = ansi_escape.sub("", lines)
        nuclei_output_regex = (
            r"^\[(?P<date>\d\d\d\d-\d\d-\d\d \d\d:\d\d:\d\d)\] "
            r"\[(?P<template_id>[a-zA-Z0-9-:]{3,32})\] "
            r"\[(?P<type>[a-zA-Z0-9-:]{2,16})\] "
            r"\[(?P<severity>(info|low|medium|high))\] "
            r"(?P<matched>.*)$"
        )
        matches = finditer(nuclei_output_regex, ansi_escaped_lines, MULTILINE)
        for match in matches:
            results.append(
                NucleiData(
                    date=datetime.strptime(match.group("date"), "%Y-%m-%d %H:%M:%S"),
                    template_id=str(match.group("template_id")),
                    type=str(match.group("type")),
                    severity=str(match.group("severity")),
                    matched=str(match.group("matched")),
                )
            )
        return self._parse_nuclei_matched(data_list=results)

    def _parse_nuclei_json_output(self, lines: str) -> List[NucleiData]:
        """
        Parse nuclei json output
        :param lines: Nuclei json output string, example:
        {"templateID":"apache-version-detect",
         "info":{"author":"philippedelteil","reference":"http://reference.com/reference",
                 "description":"Some Apache servers have the version on the response header. The OpenSSL version can be also obtained",
                 "severity":"info","name":"Apache Version"},
         "type":"http","host":"http://server.ispa.cnr.it/","matched":"http://server.ispa.cnr.it/",
         "extracted_results":["Apache/2.4.7 (Ubuntu)"],"ip":"150.145.88.94",
         "timestamp":"2021-06-07T12:57:27.577122+03:00"}
        :return: List of NucleiData objects, example:
        [NucleiData(date=datetime.datetime(2021, 6, 7, 12, 57, 27, 577122, tzinfo=datetime.timezone(datetime.timedelta(seconds=10800), '+0300')),
                    template_id='apache-version-detect', template_name='Apache Version', author='philippedelteil',
                    severity='info', tags=None, reference='http://reference.com/reference',
                    description='Some Apache servers have the version on the response header. The OpenSSL version can be also obtained',
                    type='http', host='http://server.ispa.cnr.it/', ip=IPv4Address('150.145.88.94'),
                    address='150.145.88.94', scheme='http', port=80, matched='http://server.ispa.cnr.it/',
                    extracted_results=['Apache/2.4.7 (Ubuntu)'])]
        """
        results: List[NucleiData] = list()
        for line in lines.split("\n"):
            try:
                nuclei_data_dict: Dict = loads(line)
                nuclei_data: NucleiData = NucleiData.Schema(unknown=EXCLUDE).load(
                    nuclei_data_dict
                )
                results.append(nuclei_data)
            except JSONDecodeError:
                continue
            except ValidationError:
                continue
        return self._parse_nuclei_matched(data_list=results)

    def _upload_nuclei_data(
        self, data_list: List[NucleiData]
    ) -> List[HiveLibrary.Host]:
        """
        Upload nuclei data to Hive
        :param data_list: List of NucleiData objects, example:
        [NucleiData(date=datetime.datetime(2021, 6, 7, 12, 54, 47), template_id='apache-version-detect',
                    template_name=None, author=None, severity='info', tags=None, reference=None, description=None,
                    type='http', host=None, ip=None, address='server.ispa.cnr.it', scheme='http', port=80,
                    matched='http://server.ispa.cnr.it/', extracted_results=['Apache/2.4.7 (Ubuntu)'])]
        :return: List of created Hive hosts, example:
        [HiveLibrary.Host(checkmarks=[], files=[], id=None, uuid=None, notes=[], ip=IPv4Address('150.145.88.94'),
                          records=[], names=[HiveLibrary.Host.Name(checkmarks=[], files=[], id=None, ips=None,
                          uuid=None, notes=[], hostname='server.ispa.cnr.it', records=[], tags=[])],
                          ports=[HiveLibrary.Host.Port(checkmarks=[], files=[], id=None, uuid=None, notes=[], port=80,
                                                       service=HiveLibrary.Host.Port.Service(name='http',
                                                                                             product=None,
                                                                                             version=None,
                                                                                             cpelist=None),
                                                       protocol='tcp', state='open',
                                                       records=[HiveLibrary.Record(children=[], create_time=None,
                                                                                   creator_uuid=None, extra=None,
                                                                                   id=None, uuid=None, import_type=None,
                                                                                   name='[info] apache-version-detect: http://server.ispa.cnr.it/',
                                                                                   tool_name='nuclei',
                                                                                   record_type='nested',
                                                                                   value=[ .... ],
                                                       tags=[HiveLibrary.Tag(id=None, uuid=None, name='test_port_tag',
                                                                             parent_id=None, base_node_id=None,
                                                                             labels=[], parent_labels=[])])],
                          tags=[HiveLibrary.Tag(id=None, uuid=None, name='test_host_tag', parent_id=None,
                                                base_node_id=None, labels=[], parent_labels=[])])]
        """
        hive_hosts: List[HiveLibrary.Host] = list()
        for data in data_list:
            try:
                # Make empty Hive host and port
                host: HiveLibrary.Host = HiveLibrary.Host()
                port: HiveLibrary.Host.Port = HiveLibrary.Host.Port()

                # Set tag for host
                if self.host_tag is not None:
                    host.tags = [HiveLibrary.Tag(name=self.host_tag)]
                # Set tag for port
                if self.port_tag is not None:
                    port.tags = [HiveLibrary.Tag(name=self.port_tag)]
                # Automatically set tag for host and port, example: 'nuclei_high'
                if self.auto_tag:
                    tag_name: str = f"nuclei_{data.severity}"
                    host.tags = [HiveLibrary.Tag(name=tag_name)]
                    port.tags = [HiveLibrary.Tag(name=tag_name)]

                # Get host IP address
                host_address: Optional[IPv4Address] = None
                if isinstance(data.ip, IPv4Address):
                    host_address = data.ip
                else:
                    try:
                        # Convert string IP address to IPv4Address object
                        host_address = ip_address(data.address)
                    except ValueError:
                        # Get host IP address by name
                        if self.resolve:
                            try:
                                host_address = ip_address(gethostbyname(data.address))
                            except herror:
                                pass
                        # Set host name
                        host.names = [HiveLibrary.Host.Name(hostname=data.address)]

                # Set Hive host IP address
                if host_address is not None:
                    host.ip = host_address

                    # Try to resolve host name by address
                    try:
                        if self.resolve:
                            if len(host.names) == 0:
                                host.names = [
                                    HiveLibrary.Host.Name(
                                        hostname=gethostbyaddr(str(host_address))[0]
                                    )
                                ]
                    except herror:
                        pass

                # Set Hive record name
                if data.template_name is not None:
                    record_name: str = f"[{data.severity}] {data.template_name} ({data.template_id}): {data.matched}"
                else:
                    record_name: str = (
                        f"[{data.severity}] {data.template_id}: {data.matched}"
                    )

                # Make Hive record
                records: List[HiveLibrary.Record] = [
                    HiveLibrary.Record(
                        name=record_name,
                        tool_name="nuclei",
                        record_type=RecordTypes.NESTED.value,
                        value=list(),
                    )
                ]
                # Make record value
                for key in [
                    "address",
                    "date",
                    "severity",
                    "type",
                    "tags",
                    "reference",
                    "description",
                    "matched",
                ]:
                    if data.__dict__[key] is not None:
                        records[0].value.append(
                            HiveLibrary.Record(
                                name=f"{key.capitalize()}",
                                tool_name="nuclei",
                                record_type=RecordTypes.STRING.value,
                                value=str(data.__dict__[key]),
                            )
                        )
                if isinstance(data.extracted_results, List):
                    records[0].value.append(
                        HiveLibrary.Record(
                            name="Extracted results",
                            tool_name="nuclei",
                            record_type=RecordTypes.LIST.value,
                            value=data.extracted_results,
                        )
                    )

                # Add port for Hive host
                if data.port is not None:
                    # Add created records to port
                    port.port = data.port
                    port.service = HiveLibrary.Host.Port.Service(name=data.scheme)
                    port.records = records
                    host.ports = [port]
                else:
                    # Add created records to host
                    host.records = records

                # Create Hive host
                task_id: Optional[UUID] = self.hive_api.create_host(
                    project_id=self.project_id, host=host
                )
                if task_id is not None:
                    hive_hosts.append(host)
            except AssertionError as error:
                print(f"Assertion Error: {error}")

        return hive_hosts

    def parse_nuclei_console_output(self, lines: str) -> List[HiveLibrary.Host]:
        """
        Parse nuclei console output and send parsed data to Hive
        :param lines: Nuclei console output string, example: '[[36m2021-06-07 12:54:47[0m] [[92mapache-version-detect[0m] [[94mhttp[0m] [[34minfo[0m] http://server.ispa.cnr.it/ [[96mApache/2.4.7 (Ubuntu)[0m]'
        :return: List of created Hive hosts, example:
        [HiveLibrary.Host(checkmarks=[], files=[], id=None, uuid=None, notes=[], ip=IPv4Address('150.145.88.94'),
                          records=[], names=[HiveLibrary.Host.Name(checkmarks=[], files=[], id=None, ips=None,
                          uuid=None, notes=[], hostname='server.ispa.cnr.it', records=[], tags=[])],
                          ports=[HiveLibrary.Host.Port(checkmarks=[], files=[], id=None, uuid=None, notes=[], port=80,
                                                       service=HiveLibrary.Host.Port.Service(name='http',
                                                                                             product=None,
                                                                                             version=None,
                                                                                             cpelist=None),
                                                       protocol='tcp', state='open',
                                                       records=[HiveLibrary.Record(children=[], create_time=None,
                                                                                   creator_uuid=None, extra=None,
                                                                                   id=None, uuid=None, import_type=None,
                                                                                   name='[info] apache-version-detect: http://server.ispa.cnr.it/',
                                                                                   tool_name='nuclei',
                                                                                   record_type='nested',
                                                                                   value=[ .... ],
                                                       tags=[HiveLibrary.Tag(id=None, uuid=None, name='test_port_tag',
                                                                             parent_id=None, base_node_id=None,
                                                                             labels=[], parent_labels=[])])],
                          tags=[HiveLibrary.Tag(id=None, uuid=None, name='test_host_tag', parent_id=None,
                                                base_node_id=None, labels=[], parent_labels=[])])]
        """
        nuclei_objects = self._parse_nuclei_console_output(lines)
        return self._upload_nuclei_data(nuclei_objects)

    def parse_nuclei_json_output(self, lines: str) -> List[HiveLibrary.Host]:
        """
        Parse nuclei json output and send parsed data to Hive
        :param lines: Nuclei json output string, example:
        {"templateID":"apache-version-detect",
         "info":{"author":"philippedelteil","reference":"http://reference.com/reference",
                 "description":"Some Apache servers have the version on the response header. The OpenSSL version can be also obtained",
                 "severity":"info","name":"Apache Version"},
         "type":"http","host":"http://server.ispa.cnr.it/","matched":"http://server.ispa.cnr.it/",
         "extracted_results":["Apache/2.4.7 (Ubuntu)"],"ip":"150.145.88.94",
         "timestamp":"2021-06-07T12:57:27.577122+03:00"}
        :return: List of created Hive hosts, example:
        [HiveLibrary.Host(checkmarks=[], files=[], id=None, uuid=None, notes=[], ip=IPv4Address('150.145.88.94'),
                          ip_binary=None, records=[], names=[HiveLibrary.Host.Name(checkmarks=[], files=[], id=None,
                                                                                   ips=None, uuid=None, notes=[],
                                                                                   hostname='server.ispa.cnr.it',
                                                                                   records=[], tags=[])],
                          ports=[HiveLibrary.Host.Port(checkmarks=[], files=[], id=None, uuid=None, notes=[], port=80,
                                                       service=HiveLibrary.Host.Port.Service(name='http', product=None,
                                                                                             version=None, cpelist=None),
                                                       protocol='tcp', state='open',
                                                       records=[HiveLibrary.Record(children=[], create_time=None,
                                                                                   creator_uuid=None, extra=None,
                                                                                   id=None, uuid=None, import_type=None,
                                                                                   name='[info] Apache Version (apache-version-detect): http://server.ispa.cnr.it/',
                                                                                   tool_name='nuclei',
                                                                                   record_type='nested',
                                                                                   value=[ .... ])],
                                                       tags=[HiveLibrary.Tag(id=None, uuid=None, name='test_port_tag',
                                                                             parent_id=None, base_node_id=None,
                                                                             labels=[], parent_labels=[])])],
                          tags=[HiveLibrary.Tag(id=None, uuid=None, name='test_host_tag', parent_id=None,
                                                base_node_id=None, labels=[], parent_labels=[])])]
        """
        nuclei_objects = self._parse_nuclei_json_output(lines)
        return self._upload_nuclei_data(nuclei_objects)
