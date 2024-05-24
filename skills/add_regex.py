from opsdroid.skill import Skill
from opsdroid.matchers import match_regex

import os
import sys
sys.path.append(os.getcwd())

from regex_classifier import *

class AddRegex(Skill):
    @match_regex(r'^add_regex ')
    async def match(self, message):
        print("---RECEIVED ADD REGEX COMMAND---")
        regex_clf = RegexClassifier()
        cmd = message.text.split()
        regex_clf.add_pattern(cmd[2], cmd[1])
        await message.respond(f"New pattern added! {cmd[2]}: {cmd[1]}")
