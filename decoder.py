import traceback
from web3.auto import w3
from eth_utils import event_abi_to_log_topic, to_hex
from web3._utils.events import get_event_data
from hexbytes import HexBytes
import json
import re

class Decoder():

    def decode_tuple(self, t, target_field):
        output = dict()
        for i in range(len(t)):
            if isinstance(t[i], (bytes, bytearray)):
                output[target_field[i]['name']] = to_hex(t[i])
            elif isinstance(t[i], (tuple)):
                output[target_field[i]['name']] = self.decode_tuple(t[i], target_field[i]['components'])
            else:
                output[target_field[i]['name']] = t[i]
        return output

    def decode_list_tuple(self, l, target_field):
        output = l
        for i in range(len(l)):
            output[i] = self.decode_tuple(l[i], target_field)
        return output

    def decode_list(self, l):
        output = l
        for i in range(len(l)):
            if isinstance(l[i], (bytes, bytearray)):
                output[i] = to_hex(l[i])
            else:
                output[i] = l[i]
        return output

    def convert_to_hex(self, arg, target_schema):
        output = dict()
        for k in arg:
            if isinstance(arg[k], (bytes, bytearray)):
                output[k] = to_hex(arg[k])
            elif isinstance(arg[k], (list)) and len(arg[k]) > 0:
                target = [a for a in target_schema if 'name' in a and a['name'] == k][0]
                if target['type'] == 'tuple[]':
                    target_field = target['components']
                    output[k] = self.decode_tuple(arg[k], target_field)
                else:
                    output[k] = self.decode_tuple(arg[k])
            elif isinstance(arg[k], (tuple)):
                target_field = [a['components'] for a in target_schema if 'name' in a and a['name'] == k][0]
                output[k] = self.decode_tuple(arg[k], target_field)
            else:
                output[k] = arg[k]
        return output

    def _get_topic2abi(self, abi):
        if isinstance(abi, (str)):
            abi = json.loads(abi)

        event_abi = [a for a in abi if a['type'] == 'event']
        topic2abi = {event_abi_to_log_topic(_): _ for _ in event_abi}
        return topic2abi

    def _get_hex_topic(self, t):
        hex_t = HexBytes(t)
        return hex_t

    def decode_log(self, data, topics, abi):
        if abi is not None:
            try:
                topic2abi = self._get_topic2abi(abi)

                log = {
                    'address': None,
                    'blockHash': None,
                    'blockNumber': None,
                    'data': data,
                    'logIndex': None,
                    'topics': [self._get_hex_topic(_) for _ in topics],
                    'transactionHash': None,
                    'transactionIndex': None
                }
                try:
                    event_abi = topic2abi[log['topics'][0]]
                    evt_name = event_abi['name']

                    data = get_event_data(w3.codec, event_abi, log)['args']
                    target_schema = event_abi['inputs']
                    decoded_data = self.convert_to_hex(data, target_schema)

                    output = evt_name, json.dumps(decoded_data), json.dumps(target_schema)

                    return output

                except KeyError:
                    return 'no matching abi', None, None
            except Exception:
                return 'decode error', traceback.format_exc(), None
        else:
            return 'no matching abi', None, None

    def clean_input (self, input):
        if isinstance(input, str):
            element = re.sub(r'[\W_]+', '', input)
        elif isinstance(input,list):
            element = []
            for ele in input:
                each_lement = re.sub(r'[\W_]+', '', ele)
                element.append(each_lement)
        return element
