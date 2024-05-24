from opsdroid.skill import Skill
from opsdroid.matchers import match_regex

import os
import sys
sys.path.append(os.getcwd())

from regex_classifier import *

class MatchAll(Skill):
    @match_regex(r'^match ')
    async def match(self, message):
        print("---RECEIVED MATCH-ALL COMMAND---")
        regex_clf = RegexClassifier()
        matches = regex_clf.match_patterns(message.text.split()[1])
        await message.respond(str(matches))

class MatchRegex(Skill):
    @match_regex(r'^match_regex ')
    async def match(self, message):
        print("---RECEIVED MATCH-REGEX COMMAND---")
        regex_clf = RegexClassifier()
        cmd = message.text.split()
        matches = regex_clf.match_input_pattern(cmd[1], cmd[2])
        await message.respond(str(matches))
