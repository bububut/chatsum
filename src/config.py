import os

config = {
    'clickhouse_port': None,
    'clickhouse_user': None,
    'clickhouse_password': None,
}

def load_config():
    # according to `export` statements in `sample.start.sh`, load config items from environment variables
    config['clickhouse_port'] = 19000
    config['clickhouse_user'] = os.environ['CLICKHOUSE_USER']
    config['clickhouse_password'] = os.environ['CLICKHOUSE_PASSWORD']