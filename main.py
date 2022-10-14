#!/usr/bin/env python3
from utils.utility import parse_config
from utils.update_data import UpdateData
conf       = parse_config(r"config/conf.yaml")
data = UpdateData(conf)
data.run_update_data()