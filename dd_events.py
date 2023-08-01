import aiohttp
import asyncio
import json
import os
from datetime import datetime, timedelta

DATADOG_API_URL = "https://api.us5.datadoghq.com/api/v1/events"

async def fetch_datadog_events(session, start_time, api_key, app_key):
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

    async with session.get(DATADOG_API_URL, params=params) as response:
        print(f"HTTP Status Code: {response.status}")
        return await response.json(), end_time

async def main(queue: asyncio.Queue, args: dict):
    interval = int(args.get("interval", 10))
    api_key = args.get("api_key")
    app_key = args.get("app_key")

    async with aiohttp.ClientSession() as session:
        # start from 5 minutes ago
        start_time = datetime.now() - timedelta(minutes=5)
        printed_events = set()  # keep track of printed events

        while True:
            response, _ = await fetch_datadog_events(session, start_time, api_key, app_key)

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
    INTERVAL = os.getenv("INTERVAL", "10")

    class MockQueue:
        async def put(self, event):
            print(event)

    args = {"api_key": DATADOG_API_KEY, "app_key": DATADOG_APP_KEY, "interval": INTERVAL}
    asyncio.run(main(MockQueue(), args))

