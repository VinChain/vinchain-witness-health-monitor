
WITNESS_HEALTH_MONITOR_SETTINGS = {
    'app_name': 'witness_health_monitor',
    'checking_witness_timeout': 30,  # sec
    'node': 'wss://127.0.0.1:11011/',
    'account': 'abetterbid',
    'known_chains': {
        'VIN': {
            'chain_id': 'b025b3dacd447ae0f9baa148ad5e69e2ec8ca93c0cc6c341b60da8a4b2a29871',
            'core_symbol': 'VIN',
            'prefix': 'VIN'
        },
    },
    'logstash_host': '127.0.0.1',
    'logstash_port': 5200,
    'logging_version': 1,
}
