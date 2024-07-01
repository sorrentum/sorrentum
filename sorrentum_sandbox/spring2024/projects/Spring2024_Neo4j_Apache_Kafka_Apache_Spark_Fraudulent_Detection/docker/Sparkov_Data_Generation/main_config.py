import json


class MainConfig:

    def __init__(self, main):
        self.config = self.all_profiles_dicts(main)

    # convert type to a tuple
    def convert_config_type(self, x):
        if type(x) is dict:
            minval = float(x['min'])
            maxval = float(x['max'])
            if maxval < 0:
                return (minval, float('inf'))
            else:
                return (minval, maxval)
        else:
            return x

    def all_profiles_dicts(self, config):
        with open(config, 'r') as f:
            main_config = json.load(f)
            all_profiles = {}
            for pf in main_config:
                if pf != 'leftovers.json':
                    all_profiles[pf] = {}
                    for qual in main_config[pf]:
                        all_profiles[pf][qual] = \
                        self.convert_config_type(main_config[pf][qual])
            return all_profiles
