DOCUMENTATION = r'''
module: dd_events
short_description: Event-Driven Ansible source plugin for Datadog events
description:
    - Poll Datadog API for new events
    - Only retrieves events that occurred after the script began executing
    - This script can be tested outside of ansible-rulebook by specifying environment variables for DATADOG_API_KEY, DATADOG_APP_KEY, DATADOG_API_URL, and INTERVAL
author: "Colin McNaughton (@cloin)"
options:
    api_key:
        description:
            - Your Datadog API key
        required: true
    app_key:
        description:
            - Your Datadog Application key
        required: true
    api_url:
        description:
            - The URL for the Datadog API
        required: false
        default: "https://api.datadoghq.com/api/v1/events"
    interval:
        description:
            - The interval, in seconds, at which the script polls the API
        required: false
        default: 10
notes:
    - The script will run indefinitely until manually stopped. To stop the script, use Control-C or any other method of sending an interrupt signal to the process
    - The script uses the aiohttp and asyncio libraries for making HTTP requests and handling asynchronous tasks, respectively. Make sure these libraries are installed in your Python environment before running the script
    - This script is designed for Python 3.7 and above due to the usage of the asyncio library. Please ensure you are using an appropriate version of Python
'''

EXAMPLES = r'''
- name: Respond to Datadog events
  hosts: all
  sources:
    - cloin.datadog.dd_events:
        api_key: asdlkfjh123049857
        app_key: lkjahsdf09827345hasef
        api_url: https://api.us5.datadoghq.com/api/v1/events
        interval: 10

  rules:
    - name: Catch all Datadog events
      condition: event.id is defined
      action:
        debug:
'''


import aiohttp
import asyncio
import json
import os
from datetime import datetime, timedelta

async def fetch_datadog_events(session, api_url, start_time, api_key, app_key):
    # Define end time for events
    end_time = datetime.now()

    # Convert times to Unix timestamps
    start_time = int(start_time.timestamp())
    end_time = int(end_time.timestamp())

    params = {
        "start": start_time,
        "end": end_time,
        "api_key": api_key,
        "application_key": app_key,
    }

    async with session.get(api_url, params=params) as response:
        print(f"HTTP Status Code: {response.status}")
        return await response.json(), end_time

async def main(queue: asyncio.Queue, args: dict):
    interval = int(args.get("interval", 10))
    api_key = args.get("api_key")
    app_key = args.get("app_key")
    api_url = args.get("api_url")

    async with aiohttp.ClientSession() as session:
        # events sometimes take a while to post to the event stream
        # start looking for events from 5 minutes ago
        start_time = datetime.now() - timedelta(minutes=5)
        printed_events = set()  # keep track of printed events

        while True:
            response, _ = await fetch_datadog_events(session, api_url, start_time, api_key, app_key)

            if 'events' in response:
                for event in response['events']:
                    event_id_date = (event['id'], event['date_happened'])
                    if event_id_date not in printed_events:
                        await queue.put(event)  # put the event in the queue
                        printed_events.add(event_id_date)

            await asyncio.sleep(interval)  # wait for interval seconds

            # update start_time to 5 minutes ago for the next iteration
            start_time = datetime.now() - timedelta(minutes=5)

if __name__ == "__main__":
    DATADOG_API_KEY = os.getenv("DATADOG_API_KEY", "default_api_key")
    DATADOG_APP_KEY = os.getenv("DATADOG_APP_KEY", "default_app_key")
    DATADOG_API_URL = os.getenv("DATADOG_API_URL", "https://api.datadoghq.com/api/v1/events")
    INTERVAL = os.getenv("INTERVAL", "10")

    class MockQueue:
        async def put(self, event):
            print(event)

    args = {
        "api_key": DATADOG_API_KEY,
        "app_key": DATADOG_APP_KEY,
        "api_url": DATADOG_API_URL,
        "interval": INTERVAL,
    }
    asyncio.run(main(MockQueue(), args))

