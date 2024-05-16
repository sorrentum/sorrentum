from kazoo.client import KazooClient
import json

ZK_SERVER = 'zookeeper:2181'

class ConfigManager:
    def __init__(self):
        self.zk = KazooClient(hosts=ZK_SERVER)
        self.zk.start()

    def create_node(self, path, value):
        if not self.zk.exists(path):
            self.zk.create(path, json.dumps(value).encode('utf-8'))
        else:
            self.update_node(path, value)

    def read_node(self, path):
        if self.zk.exists(path):
            data, _ = self.zk.get(path)
            return json.loads(data.decode('utf-8'))
        else:
            return None

    def update_node(self, path, value):
        if self.zk.exists(path):
            self.zk.set(path, json.dumps(value).encode('utf-8'))
        else:
            self.create_node(path, value)

    def delete_node(self, path):
        if self.zk.exists(path):
            self.zk.delete(path)

    def close(self):
        self.zk.stop()

if __name__ == "__main__":
    cm = ConfigManager()
    config_path = "/app/config"
    initial_config = {"database": {"host": "localhost", "port": 5432}}

    cm.create_node(config_path, initial_config)

    config = cm.read_node(config_path)
    print("Current Configuration:", config)

    updated_config = {"database": {"host": "localhost", "port": 3306}}
    cm.update_node(config_path, updated_config)

    config = cm.read_node(config_path)
    print("Updated Configuration:", config)

    cm.delete_node(config_path)
    cm.close()
