# Description
"""
Hive Nuclei connector console client
Author: Vladimir Ivanov
License: MIT
Copyright 2021, Hive Nuclei connector
"""

# Import
from sys import stdin
from hive_nuclei import HiveNuclei
from argparse import ArgumentParser
from uuid import UUID
from typing import List, Union, Optional
from hive_library import HiveLibrary
from ipaddress import IPv4Address
from colorama import Fore, Style

# Authorship information
__author__ = "Vladimir Ivanov"
__copyright__ = "Copyright 2021, Hive Nuclei connector"
__credits__ = [""]
__license__ = "MIT"
__version__ = "0.0.1b1"
__maintainer__ = "Vladimir Ivanov"
__email__ = "ivanov.vladimir.mail@gmail.com"
__status__ = "Development"


# Colored print hive import results in console
def print_hive_hosts(hosts: List[HiveLibrary.Host]) -> None:
    for host in hosts:
        host_address: Union[None, IPv4Address, str] = None
        record_name: Optional[str] = None
        if host.ip is not None:
            host_address = str(host.ip)
        else:
            if len(host.names) == 1:
                host_address = host.names[0].hostname
        if len(host.records) == 1:
            record_name = host.records[0].name
        elif len(host.ports) == 1:
            host_address += f":{host.ports[0].port}"
            if len(host.ports[0].records) == 1:
                record_name = host.ports[0].records[0].name
        if host_address is not None and record_name is not None:
            print(
                f"[{Fore.BLUE}INF{Fore.RESET}] [{Fore.LIGHTBLUE_EX}hive-nuclei{Fore.RESET}] "
                f"{Style.BRIGHT}Making Hive record:{Style.RESET_ALL} {record_name} "
                f"{Style.BRIGHT}for host:{Style.RESET_ALL} {host_address} "
                f"({Fore.LIGHTYELLOW_EX}@_generic_human_{Fore.RESET}) [{Fore.BLUE}info{Fore.RESET}]"
            )
        elif host_address is not None:
            print(
                f"[{Fore.BLUE}INF{Fore.RESET}] [{Fore.LIGHTBLUE_EX}hive-nuclei{Fore.RESET}] "
                f"{Style.BRIGHT}Making Hive host:{Style.RESET_ALL} {host_address} "
                f"({Fore.LIGHTYELLOW_EX}@_generic_human_{Fore.RESET}) [{Fore.BLUE}info{Fore.RESET}]"
            )
        elif record_name is not None:
            print(
                f"[{Fore.BLUE}INF{Fore.RESET}] [{Fore.LIGHTBLUE_EX}hive-nuclei{Fore.RESET}] "
                f"{Style.BRIGHT}Making Hive record:{Style.RESET_ALL} {record_name} "
                f"({Fore.LIGHTYELLOW_EX}@_generic_human_{Fore.RESET}) [{Fore.BLUE}info{Fore.RESET}]"
            )
        else:
            print(
                f"[{Fore.BLUE}INF{Fore.RESET}] [{Fore.LIGHTBLUE_EX}hive-nuclei{Fore.RESET}] "
                f"{Style.BRIGHT}Failed to import nuclei data in Hive{Style.RESET_ALL} "
                f"({Fore.LIGHTYELLOW_EX}@_generic_human_{Fore.RESET}) [{Fore.BLUE}info{Fore.RESET}]"
            )


# Main function
def main() -> None:
    # region Parse script arguments
    parser: ArgumentParser = ArgumentParser(
        description="Connector between Hive and Nuclei"
    )

    # Hive arguments
    parser.add_argument(
        "-S", "--server_url", type=str, help="set Hive server URL", default=None
    )
    parser.add_argument(
        "-U", "--username", type=str, help="set Hive username", default=None
    )
    parser.add_argument(
        "-P", "--password", type=str, help="set Hive password", default=None
    )
    parser.add_argument(
        "-I", "--project_id", type=UUID, help="set project UUID", default=None
    )
    parser.add_argument(
        "-ht", "--host_tag", type=str, help="set Hive tag for host", default=None
    )
    parser.add_argument(
        "-pt", "--port_tag", type=str, help="set Hive tag for port", default=None
    )
    parser.add_argument(
        "-at",
        "--auto_tag",
        action="store_true",
        help="automatically add tag for host and port in Hive",
    )
    parser.add_argument(
        "-n",
        "--not_resolve",
        action="store_true",
        help="Do not resolve hostname",
    )

    # Parsers
    parser.add_argument(
        "-j",
        "--json_output",
        action="store_true",
        help="Parse nuclei json output (by default parse console output)",
    )
    parser.add_argument(
        "-cf",
        "--console_file",
        type=str,
        help="Read and parse nuclei console output file",
        default=None,
    )
    parser.add_argument(
        "-jf",
        "--json_file",
        type=str,
        help="Read and parse nuclei json output file",
        default=None,
    )

    # Verbose
    parser.add_argument(
        "-q", "--quiet", action="store_true", help="Do not print in console"
    )

    # Proxy
    parser.add_argument("-p", "--proxy", type=str, help="Set proxy URL", default=None)
    args = parser.parse_args()
    # endregion

    # Init hive nuclei class
    hive_nuclei: HiveNuclei = HiveNuclei(
        username=args.username,
        password=args.password,
        server=args.server_url,
        proxy=args.proxy,
        project_id=args.project_id,
        host_tag=args.host_tag,
        port_tag=args.port_tag,
        auto_tag=args.auto_tag,
        resolve=not args.not_resolve,
    )

    # Parse nuclei console output file
    if args.console_file is not None:
        try:
            with open(args.console_file, "r") as console_file:
                nuclei_output = console_file.read()
            print(nuclei_output)
            hosts: List[HiveLibrary.Host] = hive_nuclei.parse_nuclei_console_output(
                lines=nuclei_output
            )
            if not args.quiet:
                print_hive_hosts(hosts=hosts)
        except FileNotFoundError:
            print(f"Not found file: {args.console_file} with nuclei console output")

    # Parse nuclei json output file
    elif args.json_file is not None:
        try:
            with open(args.json_file, "r") as json_file:
                nuclei_output = json_file.read()
            print(nuclei_output)
            hosts: List[HiveLibrary.Host] = hive_nuclei.parse_nuclei_json_output(
                lines=nuclei_output
            )
            if not args.quiet:
                print_hive_hosts(hosts=hosts)
        except FileNotFoundError:
            print(f"Not found file: {args.console_file} with nuclei json output")

    # Parse nuclei json output
    elif args.json_output:
        nuclei_output = stdin.read()
        print(nuclei_output)
        hosts: List[HiveLibrary.Host] = hive_nuclei.parse_nuclei_json_output(
            lines=nuclei_output
        )
        if not args.quiet:
            print_hive_hosts(hosts=hosts)

    # By default parse nuclei console output
    else:
        nuclei_output = stdin.read()
        print(nuclei_output)
        hosts: List[HiveLibrary.Host] = hive_nuclei.parse_nuclei_console_output(
            lines=nuclei_output
        )
        if not args.quiet:
            print_hive_hosts(hosts=hosts)


# Run main function
if __name__ == "__main__":
    main()
