.. _dd_events_module:


dd_events -- Event-Driven Ansible source plugin for Datadog events
==================================================================

.. contents::
   :local:
   :depth: 1


Synopsis
--------

Poll Datadog API for new events

Only retrieves events that occurred after the script began executing

This script can be tested outside of ansible-rulebook by specifying environment variables for DATADOG\_API\_KEY, DATADOG\_APP\_KEY, DATADOG\_API\_URL, and INTERVAL






Parameters
----------

  api_key (True, any, None)
    Your Datadog API key


  app_key (True, any, None)
    Your Datadog Application key


  api_url (False, any, https://api.datadoghq.com/api/v1/events)
    The URL for the Datadog API


  interval (False, any, 10)
    The interval, in seconds, at which the script polls the API





Notes
-----

.. note::
   - The script will run indefinitely until manually stopped. To stop the script, use Control-C or any other method of sending an interrupt signal to the process
   - The script uses the aiohttp and asyncio libraries for making HTTP requests and handling asynchronous tasks, respectively. Make sure these libraries are installed in your Python environment before running the script
   - This script is designed for Python 3.7 and above due to the usage of the asyncio library. Please ensure you are using an appropriate version of Python




Examples
--------

.. code-block:: yaml+jinja

    
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





Status
------





Authors
~~~~~~~

- Colin McNaughton (@cloin)

