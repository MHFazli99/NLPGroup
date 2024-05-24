from opsdroid.skill import Skill
from opsdroid.matchers import match_parse

import os
import sys
sys.path.append(os.getcwd())

from regex_classifier import *
from utils import prettify_matches

class MatchAll(Skill):
    @match_parse('match {text}')
    async def match(self, message):
        print("---RECEIVED MATCH-ALL COMMAND---")
        regex_clf = RegexClassifier()
        matches = regex_clf.match_patterns(message.entities['text']['value'])
        await message.respond(prettify_matches(matches))

class MatchRegex(Skill):
    @match_parse('match_regex {text} {pattern}')
    async def match(self, message):
        print("---RECEIVED MATCH-REGEX COMMAND---")
        regex_clf = RegexClassifier()
        matches = regex_clf.match_input_pattern(message.entities['text']['value'], message.entities['pattern']['value'])
        if matches:
            await message.respond("Regex matches the input")
        else:
            await message.respond("Regex doesn't match input")
