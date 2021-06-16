# Description
"""
Unit tests for Hive Nuclei connector
Author: Vladimir Ivanov
License: MIT
Copyright 2021, Hive Nuclei connector
"""

# Import
from unittest import TestCase
from test_variables import HiveVariables
from hive_library import HiveLibrary
from hive_library.rest import HiveRestApi
from hive_nuclei import HiveNuclei
from typing import Optional, List
from time import sleep

# Authorship information
__author__ = "Vladimir Ivanov"
__copyright__ = "Copyright 2021, Hive Nuclei connector"
__credits__ = [""]
__license__ = "MIT"
__version__ = "0.0.1"
__maintainer__ = "Vladimir Ivanov"
__email__ = "ivanov.vladimir.mail@gmail.com"
__status__ = "Development"

# Global variables
variables: HiveVariables = HiveVariables()
hive_api: HiveRestApi = HiveRestApi(
    username=variables.username,
    password=variables.password,
    cookie=variables.cookie,
    server=variables.server,
    proxy=variables.proxy,
    debug=True,
)


# Class MsfNucleiTest
class HiveNucleiTest(TestCase):

    # Parse console output
    def test01_parse_console_output(self):
        hive_api.delete_project_by_name(variables.project.name)
        variables.project = hive_api.create_project(project=variables.project)
        self.assertIsNotNone(variables.project)
        project_id = hive_api.get_project_id_by_name(
            project_name=variables.project.name
        )
        self.assertIsNotNone(project_id)
        self.assertEqual(variables.project.id, project_id)
        hive_nuclei: HiveNuclei = HiveNuclei(
            username=variables.username,
            password=variables.password,
            server=variables.server,
            proxy=variables.proxy,
            project_id=variables.project.id,
            host_tag=variables.host_tag.name,
            port_tag=variables.port_tag.name,
            resolve=True,
        )
        with open(variables.console_output_file, "r") as console_output_file:
            nuclei_lines: str = console_output_file.read()
        created_hosts: Optional[
            List[HiveLibrary.Host]
        ] = hive_nuclei.parse_nuclei_console_output(lines=nuclei_lines)
        self.assertIsInstance(created_hosts, List)
        self.assertGreater(len(created_hosts), 0)
        self.assertIsInstance(created_hosts[0], HiveLibrary.Host)
        created_host: HiveLibrary.Host = created_hosts[0]
        sleep(10)
        existing_hosts: Optional[List[HiveLibrary.Host]] = hive_api.get_hosts(
            project_id=variables.project.id
        )
        self.assertIsInstance(existing_hosts, List)
        self.assertGreater(len(existing_hosts), 0)
        self.assertIsInstance(existing_hosts[0], HiveLibrary.Host)
        existing_host: HiveLibrary.Host = existing_hosts[0]
        self.assertEqual(created_host.ip, existing_host.ip)
        self.assertEqual(
            created_host.names[0].hostname, existing_host.names[0].hostname
        )
        self.assertEqual(created_host.tags[0].name, existing_host.tags[0].name)
        self.assertEqual(created_host.ports[0].port, existing_host.ports[0].port)
        self.assertEqual(
            created_host.ports[0].tags[0].name, existing_host.ports[0].tags[0].name
        )
        hive_api.delete_project_by_name(variables.project.name)

    # Parse json output
    def test02_parse_json_output(self):
        hive_api.delete_project_by_name(variables.project.name)
        variables.project = hive_api.create_project(project=variables.project)
        self.assertIsNotNone(variables.project)
        project_id = hive_api.get_project_id_by_name(
            project_name=variables.project.name
        )
        self.assertIsNotNone(project_id)
        self.assertEqual(variables.project.id, project_id)
        hive_nuclei: HiveNuclei = HiveNuclei(
            username=variables.username,
            password=variables.password,
            server=variables.server,
            proxy=variables.proxy,
            project_id=variables.project.id,
            host_tag=variables.host_tag.name,
            port_tag=variables.port_tag.name,
            resolve=True,
        )
        with open(variables.json_output_file, "r") as json_output_file:
            nuclei_lines: str = json_output_file.read()
        created_hosts: Optional[
            List[HiveLibrary.Host]
        ] = hive_nuclei.parse_nuclei_json_output(lines=nuclei_lines)
        self.assertIsInstance(created_hosts, List)
        self.assertGreater(len(created_hosts), 0)
        self.assertIsInstance(created_hosts[0], HiveLibrary.Host)
        created_host: HiveLibrary.Host = created_hosts[0]
        sleep(10)
        existing_hosts: Optional[List[HiveLibrary.Host]] = hive_api.get_hosts(
            project_id=variables.project.id
        )
        self.assertIsInstance(existing_hosts, List)
        self.assertGreater(len(existing_hosts), 0)
        self.assertIsInstance(existing_hosts[0], HiveLibrary.Host)
        existing_host: HiveLibrary.Host = existing_hosts[0]
        self.assertEqual(created_host.ip, existing_host.ip)
        self.assertEqual(
            created_host.names[0].hostname, existing_host.names[0].hostname
        )
        self.assertEqual(created_host.tags[0].name, existing_host.tags[0].name)
        self.assertEqual(created_host.ports[0].port, existing_host.ports[0].port)
        self.assertEqual(
            created_host.ports[0].tags[0].name, existing_host.ports[0].tags[0].name
        )
        hive_api.delete_project_by_name(variables.project.name)

    # Parse console output auto_tag
    def test03_parse_console_output_auto_tag(self):
        hive_api.delete_project_by_name(variables.project.name)
        variables.project = hive_api.create_project(project=variables.project)
        self.assertIsNotNone(variables.project)
        project_id = hive_api.get_project_id_by_name(
            project_name=variables.project.name
        )
        self.assertIsNotNone(project_id)
        self.assertEqual(variables.project.id, project_id)
        hive_nuclei: HiveNuclei = HiveNuclei(
            username=variables.username,
            password=variables.password,
            server=variables.server,
            proxy=variables.proxy,
            project_id=variables.project.id,
            auto_tag=True,
            resolve=True,
        )
        with open(variables.console_output_file, "r") as console_output_file:
            nuclei_lines: str = console_output_file.read()
        created_hosts: Optional[
            List[HiveLibrary.Host]
        ] = hive_nuclei.parse_nuclei_console_output(lines=nuclei_lines)
        self.assertIsInstance(created_hosts, List)
        self.assertGreater(len(created_hosts), 0)
        self.assertIsInstance(created_hosts[0], HiveLibrary.Host)
        created_host: HiveLibrary.Host = created_hosts[0]
        sleep(10)
        existing_hosts: Optional[List[HiveLibrary.Host]] = hive_api.get_hosts(
            project_id=variables.project.id
        )
        self.assertIsInstance(existing_hosts, List)
        self.assertGreater(len(existing_hosts), 0)
        self.assertIsInstance(existing_hosts[0], HiveLibrary.Host)
        existing_host: HiveLibrary.Host = existing_hosts[0]
        self.assertEqual(created_host.ip, existing_host.ip)
        self.assertEqual(
            created_host.names[0].hostname, existing_host.names[0].hostname
        )
        self.assertEqual(created_host.tags[0].name, "nuclei_info")
        self.assertEqual(created_host.tags[0].name, existing_host.tags[0].name)
        self.assertEqual(created_host.ports[0].port, existing_host.ports[0].port)
        self.assertEqual(created_host.ports[0].tags[0].name, "nuclei_info")
        self.assertEqual(
            created_host.ports[0].tags[0].name, existing_host.ports[0].tags[0].name
        )
        hive_api.delete_project_by_name(variables.project.name)
