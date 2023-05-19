import sys
import inspect

#pylint: disable=invalid-name
class node_config_v0_0_0 :
    _config_args = {"wasm-runtime" : "eos-vm",
                    "abi-serializer-max-time-ms" : "15",
                    "contracts-console" : "true",
                    "http-server-address" : "0.0.0.0:8888",
                    "p2p-listen-endpoint" : "0.0.0.0:9876",
                    "state-history-endpoint" : "0.0.0.0:8080",
                    "agent-name" : "DUNE Test Node",
                    "net-threads" : "2",
                    "max-transaction-time" : "100",
                    "producer-name" : "eosio",
                    "enable-stale-production" : "true",
                    "resource-monitor-not-shutdown-on-threshold-exceeded" : "true"}

    _plugins = ["eosio::chain_api_plugin",
                "eosio::http_plugin",
                "eosio::producer_plugin",
                "eosio::producer_api_plugin"]

    def get_config_ini(self):
        config = ""
        for k,v in self._config_args.items() :
            config += k + "=" + v + "\n"
        for plugin in self._plugins :
            config += "plugin=" + plugin + "\n"
        return config


class node_config_v4_0_0(node_config_v0_0_0) :
    _config_add = {"read-only-read-window-time-us" : "120000"}

    def get_config_ini(self) :
        # pylint: disable=too-many-function-args
        config = super().get_config_ini(self)
        for k,v in self._config_add.items() :
            config += k + "=" + v + "\n"
        return config

def get_config_ini(major, minor=0, patch=0) :
    cls_name = "node_config_v"+ str(major) + "_" + str(minor) + "_" + str(patch)
    current_mod = sys.modules[__name__]
    config_cls_name = ""
    for name, obj in inspect.getmembers(current_mod):
        if inspect.isclass(obj):
            if (obj.__name__ == cls_name or obj.__name__ < cls_name) :
                if config_cls_name < obj.__name__ :
                    config_cls_name = obj.__name__

    config_cls = getattr(current_mod, config_cls_name)
    print(config_cls)
    return config_cls.get_config_ini(config_cls)

#pylint: enable=invalid-name
