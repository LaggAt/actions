# Copyright (c) 2021 Florian Lagg
# 
# This software is released under the MIT License.
# https://opensource.org/licenses/MIT


import asyncio
from datetime import datetime
import jsonl
import time
import os
from govee_api_laggat import Govee, GoveeNoLearningStorage

async def run():
    result = await check_connection(os.environ['GOVEE_API_KEY'], GoveeNoLearningStorage())
    persist(result)

async def check_connection(api_key, learning_storage):
    async with Govee(api_key, learning_storage=learning_storage) as govee:
        result = {
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'get_devices': {
                'success': False,
                'ping': None,
                'error': 'no result',
            },
            'get_states': {
                'success': False,
                'ping': None,
                'error': 'no result',
            },
        }

        start = time.time()
        try:
            devices, err = await govee.get_devices()
            result['get_devices']['ping'] = int((time.time() - start) * 1000)

            result['get_devices']['success'] = err is None and len(devices) > 0
            result['get_devices']['error'] = err
        except Exception as ex:
            result['get_devices']['ping'] = int((time.time() - start) * 1000)
            result['get_devices']['success'] = False
            result['get_devices']['error'] = ex

        start = time.time()
        try:
            states = await govee.get_states()
            result['get_states']['ping'] = int((time.time() - start) * 1000)

            get_states_success = True
            get_states_error = None
            if len(states) < 1:
                get_states_success = False
                get_states_error = 'no device returned' 
            elif states[0].error:
                get_states_success = False
                get_states_error = states[0].error       
            result['get_states']['success'] = get_states_success
            result['get_states']['error'] = get_states_error
        except Exception as ex:
            result['get_states']['ping'] = int((time.time() - start) * 1000)
            result['get_states']['success'] = False
            result['get_states']['error'] = ex

        return result

def persist(result):
    result_list = [result,]
    jsonl.dump_jsonl(result_list, 'output/govee-api-up.jsonl', append=True)

if __name__ == "__main__":

    loop = asyncio.get_event_loop()
    try:
        loop.run_until_complete(
            run()
        )
    finally:
        loop.close()
