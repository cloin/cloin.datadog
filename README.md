# cloin.datadog

# Datadog Event-Driven Ansible Source Plugin

This Python script is an Event-Driven Ansible source plugin for Datadog. It uses the asyncio library to poll the Datadog Events API at a set interval (defaults to 10 seconds) and prints out any new events that have occurred since the last poll. The script tracks events by their ID and timestamp to ensure that each event is printed only once.

## Usage

The script uses environment variables to get necessary parameters:

- `DATADOG_API_KEY`: Your Datadog API key. (required)
- `DATADOG_APP_KEY`: Your Datadog Application key. (required)
  - Requires `events_read` scope
- `DATADOG_API_URL`: The URL for the Datadog API. (default: `https://api.datadoghq.com/api/v1/events`)
- `INTERVAL`: The interval, in seconds, at which the script polls the API. (default: `10`)

To use the script, first set the required environment variables:

```bash
export DATADOG_API_KEY=your_api_key
export DATADOG_APP_KEY=your_app_key
# Optional: Set these if you want to override the default values
export DATADOG_API_URL=your_api_url
export INTERVAL=your_interval
```

Then, simply run the script:

```bash
python3 dd_eda_source.py
```

The script will start polling the Datadog Events API and print out any new events that occur.

## Note

The script will run indefinitely until manually stopped. To stop the script, use Control-C or any other method of sending an interrupt signal to the process.

The script uses the aiohttp and asyncio libraries for making HTTP requests and handling asynchronous tasks, respectively. Make sure these libraries are installed in your Python environment before running the script.

This script is designed for Python 3.7 and above due to the usage of the asyncio library. Please ensure you are using an appropriate version of Python.

## Troubleshooting

- If you encounter a `ModuleNotFoundError` for `aiohttp` or `asyncio`, install the missing module with `pip install aiohttp asyncio`.

- If you get a "Forbidden" error (HTTP status code 403), this means the server understood the request, but it refuses to authorize it. This could mean your API key or Application key is not correct, or it does not have the necessary permissions. Please check these keys in your Datadog dashboard.
