import sys
from os.path import dirname, abspath

from adapt.intent import IntentBuilder
from mycroft.skills.core import MycroftSkill
from mycroft.util.log import getLogger
from mycroft.util.log import LOG
import time
import re
import subprocess
from mycroft import intent_file_handler, intent_handler
from mycroft.util.log import getLogger
from fuzzywuzzy import fuzz
from fuzzywuzzy import process

sys.path.append(abspath(dirname(__file__)))
dr = __import__('dr')

logger = getLogger(__name__)

__author__ = 'tjoen'


class DutchRadio(MycroftSkill):
    def __init__(self):
        super(DutchRadio, self).__init__('Dutch Radio')
        self.dr = dr.DutchRadio()
        self.process = None

    def initialize(self):
        logger.info('initializing DutchRadio')
        self.load_data_files(dirname(__file__))
        super(DutchRadio, self).initialize()

        

    def before_play(self):
        """
           Stop currently playing media before starting the new. This method
           should always be called before the skill starts playback.
        """
        logger.info('Stopping currently playing media if any')
        #if self.process:
        #    self.stop()

    def play(self):
        self.before_play()
        
        self.speak_dialog('listening_to', {'channel': self.channel})
        time.sleep(2)
        stream_url = self.dr.channels[self.channel].stream_url
        self.process = subprocess.Popen(['mpg123', stream_url])

    def match_channel(self, channel_name):
        query = channel_name
        choices = []
        for x in self.dr.channels:
           LOG.info(x)
           choices.append(x)
        LOG.info(choices)
        # If we want only the top one
        result=process.extractOne(query, choices)
        self.channel=result[0]
        LOG.info('channel after Wuzzy: '+self.channel)

    def get_available(self, channel_name):
        logger.info(channel_name)
        if channel_name in self.dr:
            logger.info('Registring play intention...')
            return channel_name
        else:
            return None

    def prepare(self, channel_name):
        if self.process:
            self.stop()
        self.channel = channel_name
    
    @intent_handler(IntentBuilder("").require("Dutchradio").require("Words"))
    def handle_play_channel(self, message):
        logger.debug( message.data )
        cc = message.data.get('utterance')
        LOG.info("NOT Adjusted:"+cc)
        c = re.sub('^.*?' + message.data['Dutchradio'], '', cc)
        c = c[1:]
        LOG.info("Adjusted:"+c)
        self.prepare(c)
        self.match_channel(c)
        self.play()

    def stop(self, message=None):
        logger.info('Handling stop request')
        if self.process:
            self.process.terminate()
            self.process.wait()
            self.process = None
            self.channel = None

    def handle_currently_playing(self, message):
        if self.channel is not None:
            self.speak_dialog('currently_playing', {'channel': self.channel})


def create_skill():
    return DutchRadio()
