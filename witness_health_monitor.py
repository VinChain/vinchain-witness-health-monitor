#!/usr/bin/env python3

import time
import sys
from signal import signal, SIGINT, SIGTERM
import logging
import logstash
import argparse

from settings import WITNESS_HEALTH_MONITOR_SETTINGS
from vinchainio.witness import Witness
from vinchainio.blockchain import Blockchain
from vinchainio import VinChain


_app_name = WITNESS_HEALTH_MONITOR_SETTINGS['app_name']

_logger = logging.getLogger(_app_name)
_logger.setLevel(logging.INFO)
_logger.addHandler(logstash.TCPLogstashHandler(WITNESS_HEALTH_MONITOR_SETTINGS['logstash_host'],
                                               WITNESS_HEALTH_MONITOR_SETTINGS['logstash_port'],
                                               message_type=WITNESS_HEALTH_MONITOR_SETTINGS['app_name'],
                                               version=WITNESS_HEALTH_MONITOR_SETTINGS['logging_version']))
_logger.addHandler(logging.StreamHandler(sys.stdout))


class WitnessHealthMonitor(object):
    def __init__(self, node=None, account=None, checking_timeout=None):
        self._node = node or WITNESS_HEALTH_MONITOR_SETTINGS['node']
        self._account = account or WITNESS_HEALTH_MONITOR_SETTINGS['account']
        self._checking_timeout = checking_timeout or WITNESS_HEALTH_MONITOR_SETTINGS['checking_witness_timeout']

        self._stop = False
        signal(SIGINT, self.stop_gracefully)
        signal(SIGTERM, self.stop_gracefully)

    def stop_gracefully(self, signum, frame):
        _logger.warning(
            '%s: Trying to stop... ({} - {})'.format(self._node, self._account),
            _app_name,
            extra={'node': self._node, 'account': self._account,}
        )
        self._stop = True


    def monitor(self):
        _logger.warning(
            '%s: Starting...  ({} - {})'.format(self._node, self._account),
            _app_name,
            extra={'node': self._node, 'account': self._account,}
        )

        try:
            vinchain = VinChain(node=self._node, known_chains=WITNESS_HEALTH_MONITOR_SETTINGS['known_chains'], debug=False)
            blockchain = Blockchain(vinchain_instance=vinchain, mode='head')

            _logger.warning(
                '%s: Started...  ({} - {})'.format(self._node, self._account),
                _app_name,
                extra={'node': self._node, 'account': self._account,}
            )

            while not self._stop:
                status = Witness(self._account, bitshares_instance=vinchain)
                missed = status['total_missed']
                last_node_block = status['last_confirmed_block_num']
                last_blockchain_block = blockchain.get_current_block_num()
                _logger.info(
                    '%s: Node\'s response. Current block-{}, missed blocks-{} ({} - {})'.format(last_node_block,
                                                                                              missed, self._node,
                                                                                              self._account),
                    _app_name,
                    extra={'node': self._node, 'account': self._account, 'total_missed': missed,
                           'last_node_block': last_node_block, 'last_blockchain_block': last_blockchain_block}
                )
                time.sleep(self._checking_timeout)
        except Exception as e:
            _logger.exception('%s: Exception. Application has stopped!!! ({} - {})'.format(self._node, self._account),
                              _app_name,
                              extra={'node': self._node, 'account': self._account,}
                              )
            raise e

        _logger.warning(
            '%s: Stopped...  ({} - {})'.format(self._node, self._account),
            _app_name,
            extra={'node': self._node, 'account': self._account,}
        )


# Main Loop
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Vinchain witness healh monitor.')
    parser.add_argument('--node', dest='node', type=str, nargs='?', help='Witness node\'s websocket address')
    parser.add_argument('--account', dest='account', type=str, nargs='?', help='Witness node\'s account name')
    parser.add_argument('--checking_timeout', dest='checking_timeout', type=int, nargs='?',
                        help='Timeout of witness node checking (sec)')
    args = parser.parse_args()

    witness_health_monitor = WitnessHealthMonitor(args.node, args.account, args.checking_timeout)
    witness_health_monitor.monitor()
