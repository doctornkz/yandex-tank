# coding=utf-8
# TODO: make the next two lines unnecessary
# pylint: disable=line-too-long
# pylint: disable=missing-docstring
import datetime
import logging
import sys
import json
import requests
from uuid import uuid4

from builtins import str

from .decoder import Decoder
from ...common.interfaces import AbstractPlugin, \
    AggregateResultListener

logger = logging.getLogger(__name__)  # pylint: disable=C0103

class Plugin(AbstractPlugin, AggregateResultListener):
    SECTION = 'signalfx'

    def __init__(self, core, cfg, name):
        AbstractPlugin.__init__(self, core, cfg, name)
        self.tank_tag = self.get_option("tank_tag")
        self.dashboard_url = self.get_option("dashboard_url")
        self.api_url = self.get_option("api_url")
        self.project = self.get_option("project")
        self.token = self.read_token(self.get_option("token_file"))
        self.start_time = None
        self.project = self.get_option("project")
        self.end_time = None
        self.headers = {'Content-Type': 'application/json', 'X-SF-TOKEN': self.token}
        # Generates uuid without "-" to avoid conflict in dimensions.
        # Read details here: 
        # https://community.signalfx.com/s/article/Timestamp-and-UUID-data-not-allowable-in-Dimension-values
        self.uuid = str(uuid4()).replace("-", "") 
        self.decoder = Decoder(
            self.tank_tag,
            self.uuid,
            self.get_option("custom_tags"),
         )
         

    def read_token(self, filename):
        if filename:
            logger.debug("Trying to read token from %s", filename)
            try:
                with open(filename, 'r') as handle:
                    data = handle.read().strip()
                    logger.info(
                        "Read authentication token from %s, "
                        "token length is %d bytes", filename, len(str(data)))
            except IOError:
                logger.error(
                    "Failed to read SignalFX API token from %s", filename)
                logger.info(
                    "Get your SignalFX API token from your profile"
                )
                raise RuntimeError("API token error")
            return data
        else:
            logger.error("SignalFX API token filename is not defined")
            logger.info(
                "Get your SignalFX API token from your profile and provide it via 'overload.token_file' parameter"
            )
            raise RuntimeError("API token error")


    def prepare_test(self):
        self.core.job.subscribe_plugin(self)

    def start_test(self):
        logger.info("SignalFX dashboard: %s", self.render_sfx_dashboard())
        self.start_time = datetime.datetime.now()

    def render_sfx_dashboard(self):
        return self.dashboard_url + \
            '?startTime=-15m&endTime=Now' + \
            '&sources%5B%5D=' + \
            'project:' + \
            self.project + \
            '&sources%5B%5D=uuid:' + \
            self.uuid + \
            '&density=4'

    def end_test(self, retcode):
        self.end_time = datetime.datetime.now() + datetime.timedelta(minutes=1)
        logger.info("SignalFX dashboard: %s", self.render_sfx_dashboard())
        return retcode

    def on_aggregated_data(self, data, stats):
        decoded_data = self.decoder.decode_sfx_aggregates(data, stats, self.project)
        payload = {'gauge': decoded_data}
        try:
            r = requests.post(self.api_url, data=json.dumps(payload),headers=self.headers)
            if r.status_code != 200:
                logger.error('Error in sending metrics, check data or authorization')

        except:
            logger.error('Critical protocol error in sending metrics to SignalFX, check network connection')

    def set_uuid(self, id_):
        self.decoder.tags['uuid'] = id_
