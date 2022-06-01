import re
import time
import aiohttp

class FileModel():
    url: str
    filename: str

class scraper():

    def __init__(self):
        self.headers = {
            'user-agent': 'Mozilla/5.0 (Linux; Android 8.0; Pixel 2 Build/OPD3.170816.012) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Mobile Safari/537.36 Edg/87.0.664.66'
        }
        self.tiktok_headers = {
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
            "authority": "www.tiktok.com",
            "Accept-Encoding": "gzip, deflate",
            "Connection": "keep-alive",
            "Host": "www.tiktok.com",
            "User-Agent": "Mozilla/5.0  (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) coc_coc_browser/86.0.170 Chrome/80.0.3987.170 Safari/537.36",
        }

    async def _GetVideoJSON(self, original_url):
        try:
            video_id: str
            headers = self.headers
            start = time.time()
            if original_url[:12] == "https://www.":
                original_url = original_url
                video_id = re.findall('video/(\d+)?', original_url)[0]
            else:
                async with aiohttp.ClientSession() as session:
                    async with session.get(url=original_url, headers=self.headers, allow_redirects=False) as resp:
                        original_url = str(resp).split("Location': \'")[1].split("\'")[0]
                        if bool(re.findall('video/(\d+)?', original_url)):
                            video_id = re.findall('video/(\d+)?', original_url)[0]
                        else:
                            video_id = re.findall('v/(\d+)?', original_url)[0]
            tiktok_api_link = 'https://api.tiktokv.com/aweme/v1/multi/aweme/detail/?aweme_ids=%5B{}%5D'.format(video_id)
            async with aiohttp.ClientSession() as session:
                async with session.get(url=tiktok_api_link, headers=self.headers) as resp:
                    response = await resp.json()
                    return response
        except Exception as e:
            return "Ошибка при скачивании"

    async def _GetVideoData(self, original_url):
        result = await self._GetVideoJSON(original_url)
        if result == "Ошибка при скачивании":
           return result
        else:
            video_title = result["aweme_details"][0]["desc"]
            video_url = result['aweme_details'][0]['video']['play_addr']['url_list'][0]
            video_author_nickname = result["aweme_details"][0]['author']["nickname"]
            video_author_id = result["aweme_details"][0]['author']["unique_id"]
            video_author_thumb = result["aweme_details"][0]['author']['avatar_larger']['url_list'][1]
            video_create_time = result["aweme_details"][0]['create_time']
            video_aweme_id = result["aweme_details"][0]['statistics']['aweme_id']
            video_music_title = result["aweme_details"][0]['music']['title']
            video_music_author = result["aweme_details"][0]['music']['author']
            video_music_id = result["aweme_details"][0]['music']['id']
            video_music_url = result["aweme_details"][0]['music']['play_url']['url_list'][0]
            video_comment_count = result["aweme_details"][0]['statistics']['comment_count']
            video_digg_count = result["aweme_details"][0]['statistics']['digg_count']
            video_play_count = result["aweme_details"][0]['statistics']['play_count']
            video_download_count = result["aweme_details"][0]['statistics']['download_count']
            video_share_count = result["aweme_details"][0]['statistics']['share_count']
            video_desc = result["aweme_details"][0]['desc']
            video_date = {'status': 'success',
                          'original_url': original_url,
                          'platform': 'tiktok',
                          'video_url': video_url,
                          'video_title': video_title,
                          'video_author_nickname': video_author_nickname,
                          'video_author_id': video_author_id,
                          'video_create_time': video_create_time,
                          'video_aweme_id': video_aweme_id,
                          'video_music_title': video_music_title,
                          'video_music_author': video_music_author,
                          'video_music_id': video_music_id,
                          'video_music_url': video_music_url,
                          'video_comment_count': video_comment_count,
                          'video_digg_count': video_digg_count,
                          'video_play_count': video_play_count,
                          'video_share_count': video_share_count,
                          'video_download_count': video_download_count,
                          'video_desc': video_desc,
                          'video_author_thumb' : video_author_thumb
                          }
            return video_date


    async def GetVideoMusic(self, original_url):
        result = await self._GetVideoData(original_url)
        if result == "Ошибка при скачивании":
           return result
        else:
            file = FileModel()
            file.url = result["video_music_url"]
            file.filename = result["video_music_title"] + ".mp3"
            return file

    async def GetVideoLink(self, original_url):
        return_data = await self._GetVideoData(original_url)
        if return_data == "Ошибка при скачивании":
            return return_data
        else:
            file = FileModel()
            file.url = return_data["video_url"]
            file.filename = return_data["video_title"] + ".mp4"
            return file