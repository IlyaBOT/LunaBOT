import aiohttp
import logging
import random
from core.settings_bot import config


class E621connect:
    def __init__(self):
        self.config = config()
        self.token = self.config['API_TOKEN_E621']
        self.authUser = self.config['USER_E621']
        self.log = logging.getLogger(f'LunaBOT.{__name__}')

    async def get_random_post_by_tag(self, tags: str):
        limit = 320
        URL = f"https://e621.net/posts.json?tags={tags}&limit={limit}"
        try:
            data = await self.__get_request(url=URL)
            if not data['posts']:
                return None
            else:
                get_post = random.choice(data['posts'])
                self.log.debug(f"Getting this post: {get_post['file']['url']}")
                return get_post
        except TypeError as e:
            self.log.critical(f"Failed to get post")
            return None

    async def get_random_post(self, type: str = None):
        limit = 320
        if type is not None:
            URL = f"https://e621.net/posts.json?tags=order%3Arandom{type}&limit={limit}"
        else:
            URL = f"https://e621.net/posts.json?tags=order%3Arandom&limit={limit}"
        try:
            data = await self.__get_request(url=URL)
            if not data['posts']:
                return None
            else:
                get_post = random.choice(data['posts'])
                self.log.debug(f"Getting this post: {get_post['file']['url']}")
                return get_post
        except TypeError as e:
            self.log.critical(f"Failed to get post")
            return None

    async def __get_request(self, url):
        head = {"User-Agent": "LunaBot/2.0.5 (SylvesterNotCute)"}
        if not self.token and self.authUser:
            self.log.warning("Auth is None!")
            return None

        auth = aiohttp.BasicAuth(login=self.authUser, password=self.token)
        async with aiohttp.ClientSession(auth=auth, headers=head) as session:
            try:
                async with session.get(url=url) as response:
                    if response.status == 200:
                        return await response.json()
                    else:
                        self.log.debug(f"Response status: {response.status}")
            except Exception as e:
                self.log.warning(f"Unable to connect.. {e}")
                return None


