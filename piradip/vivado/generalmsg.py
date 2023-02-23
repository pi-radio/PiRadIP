from .msghandler import VivadoMessageHandler
from collections import defaultdict, deque
import re


class GeneralMessageHandler(VivadoMessageHandler):
    handlers = {
        ("Common", 17, 14) : msg_overflow,
    }

    def __init__(self, wrapper):
        super().__init__(wrapper, [ "Project", "Common" ])

        # file -> level -> lines -> maj, min -> msgs
        self.file_msgs = defaultdict(
            lambda: defaultdict(
                lambda: defaultdict(
                    lambda: defaultdict(list)
                )
            )
        )

        self.seen = set()
        self.important_msgs = list()
        self.modules = defaultdict(lambda: { 'file': None, 'line': None, 'synthesizing': False, 'messages': list() })
