from opsdroid.skill import Skill
from opsdroid.matchers import match_regex

class HelloSkill(Skill):
    @match_regex(r'hi')
    async def hello(self, message):
        print("---RECEIVED hi---")
        await message.respond('Hey')
