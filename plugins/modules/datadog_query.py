#!/usr/bin/python

DOCUMENTATION = r'''
---
module: datadog_query
short_description: Fetches latest metric values from Datadog
description:
    - This module fetches the latest metric values from Datadog for a given query and time range.
options:
    api_key:
        description:
            - The API key for Datadog.
        required: true
        type: str
    app_key:
        description:
            - The application key for Datadog.
        required: true
        type: str
    duration_seconds:
        description:
            - The time duration in seconds for which to fetch metrics.
            - Default is 600 seconds (10 minutes).
        default: 600
        type: int
    endpoint_url:
        description:
            - The Datadog API endpoint URL to fetch metrics.
            - Default is Datadog's v1 query API.
        default: 'https://api.datadoghq.com/api/v1/query'
        type: str
    queries:
        description:
            - List of Datadog metric queries to fetch.
        required: true
        type: list
        elements: str
requirements:
    - python >= 3.x
    - requests
author:
    - Colin McNaughton @cloin
examples:
    - name: Fetch metrics from Datadog
      datadog_metric_fetcher:
        api_key: 'YOUR_DD_API_KEY'
        app_key: 'YOUR_DD_APP_KEY'
        queries:
          - 'avg:system.cpu.idle{*}'
          - 'avg:system.mem.used{*}'
return:
    metrics_data:
        description: A dictionary containing the latest values for the queried metrics.
        returned: always
        type: dict
'''

from ansible.module_utils.basic import AnsibleModule
import time
import requests

def fetch_latest_metric_value(query, duration_seconds, endpoint_url, api_key, app_key):
    """Fetch the latest metric value for a given query."""
    current_time = int(time.time())
    start_time = current_time - duration_seconds
    params = {
        'from': start_time,
        'to': current_time,
        'query': query
    }
    headers = {
        'DD-API-KEY': api_key,
        'DD-APPLICATION-KEY': app_key
    }
    try:
        response = requests.get(endpoint_url, headers=headers, params=params)
        if response.status_code != 200:
            print(f"Received {response.status_code} status code.")
            print(f"Response content: {response.content.decode('utf-8')}")
        response.raise_for_status()
        data = response.json()
        if 'series' in data and data['series']:
            metric_data = data['series'][0]['pointlist']
            return metric_data[-1][1] if metric_data else None
        else:
            return None
    except Exception as e:
        print(f"An error occurred: {e}")
        raise e


def main():
    argument_spec = {
        'api_key': dict(type='str', required=True),
        'app_key': dict(type='str', required=True),
        'duration_seconds': dict(type='int', default=600),
        'endpoint_url': dict(type='str', default='https://api.datadoghq.com/api/v1/query'),
        'queries': dict(type='list', required=True)
    }

    module = AnsibleModule(
        argument_spec=argument_spec,
        supports_check_mode=True
    )

    api_key = module.params['api_key']
    app_key = module.params['app_key']
    duration_seconds = module.params['duration_seconds']
    endpoint_url = module.params['endpoint_url']
    queries = module.params['queries']

    metrics_data = {}

    for query in queries:
        try:
            latest_value = fetch_latest_metric_value(query, duration_seconds, endpoint_url, api_key, app_key)
            if latest_value is not None:
                sanitized_query = query.replace(":", "_").replace(".", "_").replace("{*}", "")
                metrics_data[sanitized_query] = latest_value
            else:
                metrics_data[query] = "No data available for the specified time range."
        except Exception as e:
            module.fail_json(msg=str(e))

    # Using 'metrics_data' for the result
    module.exit_json(changed=False, metrics_data=metrics_data)

if __name__ == '__main__':
    main()
