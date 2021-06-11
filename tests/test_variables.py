# Description
"""
test_msf_api.py: Unit tests for MSF REST API
Author: Vladimir Ivanov
License: MIT
Copyright 2021, Hive Nuclei connector
"""

# Import
from hive_library import HiveLibrary
from dataclasses import dataclass
from typing import Optional

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
class HiveVariables:
    server: str = "http://127.0.0.1:8080"
    username: str = "root@ro.ot"
    password: str = "root123"
    cookie: Optional[str] = None
    proxy: Optional[str] = "http://127.0.0.1:8081"

    project: HiveLibrary.Project = HiveLibrary.Project(
        name="test_project",
        description="Unit test project",
    )

    host_tag: HiveLibrary.Tag = HiveLibrary.Tag(name="test_host_tag")
    port_tag: HiveLibrary.Tag = HiveLibrary.Tag(name="test_port_tag")

    console_output_file: str = "nuclei_console_output.txt"
    json_output_file: str = "nuclei_json_output.txt"
