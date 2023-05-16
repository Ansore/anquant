# -*— coding:utf-8 -*-
import json

from anquant.utils import logger, tools


class Config:

    class Platform:
        pass

    def __init__(self, config_file=None):
        self.server_id = None
        self.run_time_update = False
        self.log = {}
        self.rabbitmq = {}
        self.mongodb = {}
        self.redis = {}
        self.platforms = {}
        self.heartbeat = {}
        self.service = {}
        self.proxy = {}
        if config_file is not None:
            self.loads(config_file)

    def loads(self, config_file=None):
        configures = {}
        if config_file:
            try:
                with open(config_file) as f:
                    data = f.read()
                    configures = json.loads(data)
            except Exception as e:
                print(e)
                exit(0)
            if not configures:
                print("config file error!")
                exit(0)
        self.update(configures)

    def update(self, update_fields):
        self.server_id = update_fields.get("SERVER_ID", tools.get_uuid1())
        self.run_time_update = update_fields.get("RUN_TIME_UPDATE", False)
        self.log = update_fields.get("LOG", {})
        self.rabbitmq = update_fields.get("RABBITMQ", None)
        self.mongodb = update_fields.get("MONGODB", None)
        self.redis = update_fields.get("REDIS", None)
        self.platforms = update_fields.get("PLATFORMS", {})
        self.heartbeat = update_fields.get("HEARTBEAT", {})
        self.service = update_fields.get("SERVICE", {})
        self.proxy = update_fields.get("PROXY", None)
        for k, v in update_fields.items():
            setattr(self, k, v)

    def initialize(self):
        if self.run_time_update:
            from anquant.event import EventConfig
            EventConfig(self.server_id).subscribe(self.on_event_config, False)

    async def on_event_config(self, event):
        if event.server_id != self.server_id:
            return
        if not isinstance(event.params, dict):
            logger.error("params format error! params:", event.params, caller=self)
            return

        self.update(event.params)
        logger.info("config update success!", caller=self)


