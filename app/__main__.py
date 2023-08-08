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
from zoneinfo import ZoneInfo

from time import sleep

import schedule
from aussiebb import AussieBB  # type: ignore
from aussiebb.types import AussieBBConfigFile, AussieBBOutage  # type: ignore

from .test_utils import configloader


def test_login_cycle() -> None:
    """do the needful"""

    config: AussieBBConfigFile = configloader()
    users = [
        AussieBB(username=user.username, password=user.password)
        for user in config.users
    ][:1]

    for user in users:
        try:
            services = user.get_services()
        except Exception as error_message:
            print(f"Failed to run get_services: {error_message}")
            return

        for service in services:
            try:
                outages = user.service_outages(service["service_id"])
            except Exception as error_message:
                print(
                    f"Failed to run get_services({service['service_id']}): {error_message}"
                )
                continue

            data = {
                "_time": datetime.now(ZoneInfo("UTC")).isoformat(),
            }
            try:
                parsed_obj = AussieBBOutage.model_validate(outages).model_dump()
            except Exception as error_message:
                print(f"Failed to parse into AussieBBOutage object: {error_message}")
                print(json.dumps(outages, default=str))
                continue
            data.update(parsed_obj)
            print(json.dumps(data, default=str))


if __name__ == "__main__":
    test_login_cycle()

    try:
        schedule.every(10).minutes.do(test_login_cycle)
        while True:
            schedule.run_pending()
            sleep(5)
    except KeyboardInterrupt:
        pass
    except Exception:
        print("well, that failed.")
        sleep(30)
