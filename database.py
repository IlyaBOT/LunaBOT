import sqlite3


def db_connect(func):
    def inner(*args, **kwargs):
        with sqlite3.connect("bot.db") as conn:
            res = func(*args, conn=conn, **kwargs)
            return res
    return inner


@db_connect
def init_bot_db(conn):
    c = conn.cursor()
    c.execute("""CREATE TABLE IF NOT EXISTS role_reaction (
        guild_id INTEGER NOT NULL,
        channel_id INTEGER NOT NULL,
        message_id INTEGER NOT NULL,
        emoji TEXT NOT NULL,
        role_id INTEGER NOT NULL)""")
    c.execute("""CREATE TABLE IF NOT EXISTS vc_lobbys (
                guild_id INTEGER NOT NULL,
                vc_channel_id INTEGER NOT NULL)""")
    c.execute("""CREATE TABLE IF NOT EXISTS custom_voice (
                vc_id INTEGER NOT NULL,
                name_channel TEXT NOT NULL,
                created_at TEXT NOT NULL,
                created_member_id INTEGER NOT NULL,
                guild_id INTEGER NOT NULL)""")
    conn.commit()


class RolesDatabase:
    def __int__(self):
        pass

    @db_connect
    def role_insert(self, conn, guild_id: int, channel_id: int, message_id: int, emoji: str, role_id: int):
        c = conn.cursor()
        c.execute('INSERT INTO role_reaction (guild_id, channel_id, message_id, emoji, role_id) VALUES (?, ?, ?, ?, ?)', (guild_id, channel_id, message_id, emoji, role_id))
        conn.commit()

    @db_connect
    def db_channel_id(self, conn):
        c = conn.cursor()
        c.execute('SELECT channel_id, message_id, emoji FROM role_reaction')
        res = c.fetchall()
        return res

    @db_connect
    def db_role_delete(self, conn, role_id: int):
        c = conn.cursor()
        c.execute('SELECT message_id, channel_id, emoji FROM role_reaction WHERE role_id = ?', (role_id, ))
        res = c.fetchone()
        c.execute('DELETE FROM role_reaction WHERE role_id = ?', (role_id, ))
        return res

    @db_connect
    def db_role_get(self, conn, guild_id: int, emoji: str):
        c = conn.cursor()
        c.execute('SELECT role_id, channel_id, message_id FROM role_reaction WHERE guild_id = ? AND emoji = ?', (guild_id, emoji))
        res = c.fetchone()
        return res


class VcDB:
    def __init__(self):
        pass

    @db_connect
    def vc_setup_insert(self, conn, guild_id: int, voice_channel_id: int):
        c = conn.cursor()
        c.execute('INSERT INTO vc_lobbys (guild_id, vc_channel_id) VALUES (?, ?)', (guild_id, voice_channel_id))
        conn.commit()

    @db_connect
    def get_lobby_from_guild(self, conn, guild_id: int):
        c = conn.cursor()
        c.execute("SELECT vc_channel_id FROM vc_lobbys WHERE guild_id = ?", (guild_id, ))
        try:
            (res, ) = c.fetchone()
            return res
        except TypeError:
            return None

    @db_connect
    def create_vc(self, conn, vc_id: int, name: str, created_at: str, created_member_id: int, guild_id: int):
        c = conn.cursor()
        c.execute("INSERT INTO custom_voice (vc_id, name_channel, created_at, created_member_id, guild_id) "
                  "VALUES (?, ?, ?, ?, ?)", (vc_id, name, created_at, created_member_id, guild_id))
        conn.commit()

    @db_connect
    def get_vcdb_name(self, conn, channel_id: int, guild_id: int):
        c = conn.cursor()
        c.execute("SELECT name_channel FROM custom_voice WHERE guild_id = ? AND vc_id = ?", (guild_id, channel_id))
        try:
            (res, ) = c.fetchone()
            return res
        except TypeError:
            return None

    @db_connect
    def delete_vc(self, conn, channel_id: int, guild_id: int):
        c = conn.cursor()
        c.execute("DELETE FROM custom_voice WHERE guild_id = ? AND vc_id = ?", (guild_id, channel_id))
        conn.commit()
