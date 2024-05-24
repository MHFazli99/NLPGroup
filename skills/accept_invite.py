from opsdroid.skill import Skill
from opsdroid.matchers import match_event
from opsdroid.events import UserInvite, JoinRoom, Message


WELCOME_MESSAGE = '''
سلام! این بازوی دسته‌بند رجکس است. شما می‌توانید چندین کار را اینجا انجام دهید:
1. match "text"
با وارد کردن این دستور می‌توانید ایمیل‌ها، شماره‌تلفن‌ها و آدرس‌های موجود در text را استخراج کنید.
'''


class AcceptInvites(Skill):
    @match_event(UserInvite)
    async def user_invite(self, invite):
        print("\n ---USER INVITE---\n")
        if isinstance(invite, UserInvite):
            await invite.respond(JoinRoom())
    @match_event(JoinRoom)
    async def send_welcome_message(self, event):
        print("\n ---JOIN ROOM---\n")
        if isinstance(event, JoinRoom):
            await event.respond(Message(WELCOME_MESSAGE))
