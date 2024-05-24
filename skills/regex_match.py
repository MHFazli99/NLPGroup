from opsdroid.skill import Skill
from opsdroid.matchers import match_regex

import os
import sys
sys.path.append(os.getcwd())

from regex_classifier import *

class RegexMatchSkill(Skill):
    @match_regex(r'^match')
    async def match(self, message):
        print("---RECEIVED MATCH COMMAND---")
        regex_clf = RegexClassifier()
        matches = regex_clf.match_patterns(message.text)
        await message.respond(str(matches))
