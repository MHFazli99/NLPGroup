from opsdroid.skill import Skill
from opsdroid.matchers import match_parse

import os
import sys
sys.path.append(os.getcwd())

from regex_classifier import *

class AddRegex(Skill):
    @match_parse('add_regex {name} {pattern}')
    async def match(self, message):
        print("---RECEIVED ADD-REGEX COMMAND---")
        regex_clf = RegexClassifier()
        regex_clf.add_pattern(message.entities['name']['value'], message.entities['pattern']['value'])
        await message.respond(f"New pattern added! {message.entities['name']['value']}: {message.entities['pattern']['value']}")
