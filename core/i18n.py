import gettext
from .database import GuildSettings

class I18n:
    def __init__(self, language='en_US') -> None:
        self.language = language
        self.trans = gettext.translation('messages', localedir='locate', languages=[language])
        self.trans.install()
        self.settings = GuildSettings()

    def set_language(self, language):
        self.language = language
        self.trans = gettext.translation('messages', localedir='locate', languages=[language])
        self.trans.install()
    
    def gettext(self, message):
        return self.trans.gettext(message)
    
    def get_gulid_locale(self, guild_id):
        return self.settings.get_lang(guild_id=guild_id)


i18n = I18n()

def __get_locate(guild):
    guild_id = guild
    locate = i18n.get_gulid_locale(guild_id=guild_id)
    return locate

def translate(guild):
    locale = __get_locate(guild=guild)
    i18n.set_language(locale)
    return i18n.gettext
