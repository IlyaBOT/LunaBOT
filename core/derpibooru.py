import aiohttp
import logging
import random
from core.settings_bot import config


class DerpibooruConnect:
    def __init__(self):
        self.config = config()
        self.token = self.config['API_TOKEN_DERPIBOORU']
        self.log = logging.getLogger(f'LunaBOT.{__name__}')

    async def get_safe_post(self, tag):
        URL = f"https://derpibooru.org/api/v1/json/search/images?key={self.token}&q={tag}%2C+safe&per_page=50"
        try:
            data = await self.__get_request(url=URL)
            if data.get('images'):
                get_post = random.choice(data.get('images'))
                self.log.info(f"{get_post.get('view_url')}")
                return get_post
            else:
                return None
        except TypeError as e:
            self.log.critical(f"Failed to get post", exc_info=e)
            return None

    async def get_explicit_post(self, tag):
        URL = f"https://derpibooru.org/api/v1/json/search/images?key={self.token}&q={tag}%2C+explicit&per_page=50"
        try:
            data = await self.__get_request(url=URL)
            if not data['images']:
                return None
            else:
                get_post = random.choice(data['images'])
                self.log.info(f"{get_post['view_url']}")
                return get_post
        except TypeError as e:
            self.log.critical(f"Failed to get post", exc_info=e)
            return None

    async def __get_request(self, url):
        head = {"User-Agent": "LunaBot/2.0.5 (SylvesterNotCute)"}
        if not self.token:
            self.log.info("Auth is None!")
            return None

        async with aiohttp.ClientSession(headers=head) as session:
            try:
                async with session.get(url=url) as response:
                    if response.status == 200:
                        return await response.json()
                    else:
                        self.log.debug(f"Response status: {response.status}")
            except Exception as e:
                self.log.warning(f"Unable to connect.. {e}")
                return None
