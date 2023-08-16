#!/usr/bin/python

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
        response.raise_for_status()
        data = response.json()
        if 'series' in data and data['series']:
            metric_data = data['series'][0]['pointlist']
            return metric_data[-1][1] if metric_data else None
        else:
            return None
    except Exception as e:
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
