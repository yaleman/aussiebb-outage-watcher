# pylint: disable=broad-except

"""
Using this

You really need a file called "aussiebb.json" in either the local dir or ~/.config/.

It needs at least one user in the "users" field. eg:

{
    "users" : [
        { "username" : "mickeymouse.123", "password" : "hunter2" }
    ]
}
"""

import json
from datetime import datetime
import sys
from typing import List
from zoneinfo import ZoneInfo

from time import sleep

import schedule
from aussiebb import AussieBB
from aussiebb.types import AussieBBConfigFile, AussieBBOutage

from aussiebb_outage_watcher import configloader


def do_the_thing(users: List[AussieBB]) -> None:
    """do the needful"""

    for user in users:
        try:
            services = user.get_services(use_cached=True)
        except Exception as error_message:
            print(f"Failed to run get_services: {error_message}")
            return
        if services is None:
            print("No services found, exiting.")
            return
        for service in services:
            try:
                outages = user.service_outages(service["service_id"])
            except Exception as error_message:
                print(f"Failed to run get_services({service['service_id']}): {error_message}")
                continue

            data = {
                "_time": datetime.now(ZoneInfo("UTC")).isoformat(),
                "account_username": user.username,
            }
            try:
                parsed_obj = AussieBBOutage.model_validate(outages).model_dump()
            except Exception as error_message:
                print(f"Failed to parse into AussieBBOutage object: {error_message}")
                print(json.dumps(outages, default=str))
                continue
            data.update(parsed_obj)
            print(json.dumps(data, default=str))


def main() -> None:
    config: AussieBBConfigFile = configloader()
    users = [AussieBB(username=user.username, password=user.password) for user in config.users][:1]

    if not users:
        print("No users found in config, exiting.")
        sys.exit(1)
    do_the_thing(users)

    try:
        schedule.every(10).minutes.do(do_the_thing)
        while True:
            schedule.run_pending()
            sleep(5)
    except KeyboardInterrupt:
        pass
    except Exception:
        print("well, that failed.")
        sleep(30)


if __name__ == "__main__":
    main()
