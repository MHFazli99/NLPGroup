from opsdroid.skill import Skill
from opsdroid.matchers import match_regex

import os
import sys
sys.path.append(os.getcwd())

from regex_classifier import *

class ExtractPattern(Skill):
    @match_regex(r'^extract ')
    async def match(self, message):
        print("---RECEIVED EXTRACT COMMAND---")
        regex_clf = RegexClassifier()
        cmd = message.text.split(' | ')
        pattern = regex_clf.extract_regex_pattern(cmd[1:])
        await message.respond(str(pattern))
