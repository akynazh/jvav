# -*- coding: UTF-8 -*-
import concurrent.futures
import logging
import random
import re
from typing import Tuple, Union, List, Any, Dict

import os
import requests
import requests_cache
import unicodedata
import wikipediaapi
from anti_useragent import UserAgent
from bs4 import BeautifulSoup
from deep_translator import GoogleTranslator

PATH_ROOT = os.path.expanduser("~") + "/.jvav"
PATH_CACHE_JVAV = f"{PATH_ROOT}/.jvav_cache"
if not os.path.exists(PATH_ROOT):
    os.makedirs(PATH_ROOT)


class BaseUtil:
    def __init__(self, proxy_addr="", use_cache=True, expire_after=3600):
        self.log = logging.getLogger(__name__)
        self.proxy_addr = proxy_addr
        self.use_cache = use_cache
        self.proxy_json = None
        self.expire_after = expire_after
        if self.proxy_addr != "":
            self.proxy_json = {"http": proxy_addr, "https": proxy_addr}

    @staticmethod
    def ua_mobile() -> str:
        return UserAgent().android

    @staticmethod
    def ua_desktop() -> str:
        return UserAgent(platform="windows").random

    @staticmethod
    def ua() -> str:
        return UserAgent().random

    def _inner_send_req(
        self, url: str, session, headers=None, m=0, **args
    ) -> Union[Tuple[int, None], Tuple[int, Any]]:
        if not headers:
            headers = {"user-agent": self.ua()}
        try:
            methods = {
                0: session.get,
                1: session.post,
                2: session.delete,
                3: session.put,
            }
            if m in methods:
                if self.proxy_json:
                    resp = methods[m](
                        url, proxies=self.proxy_json, headers=headers, **args
                    )
                else:
                    resp = methods[m](url, headers=headers, **args)
                if resp.status_code != 200:
                    return 404, None
                return 200, resp
            else:
                return 502, None
        except Exception as e:
            self.log.error(f"BaseUtil: failed to access {url}: {e}")
            return 502, None

    def send_req(
        self, url: str, headers=None, m=0, **args
    ) -> Tuple[int, requests.Response]:
        """send request

        :param str url: url
        :param dict headers: headers, random headers by default
        :param int m: request method, default: get(0), others: post(1), delete(2), put(3)
        :param dict args: othre request parameters
        :return tuple[int, requests.Response] status code and response
        About status code:
        200: success
        404: not found
        502: bad gateway
        """
        if self.use_cache:
            with requests_cache.CachedSession(
                cache_name=PATH_CACHE_JVAV, expire_after=self.expire_after
            ) as session:
                return self._inner_send_req(url, session, headers, m, **args)
        else:
            with requests.Session() as session:
                return self._inner_send_req(url, session, headers, m, **args)

    @staticmethod
    def get_soup(resp: requests.Response) -> BeautifulSoup:
        return BeautifulSoup(resp.text, "lxml")

    @staticmethod
    def write_html(resp: requests.Response):
        with open(f"./tmp.html", "w") as f:
            f.write(resp.text)


class RankUtil(BaseUtil):
    BASE_URL_AV_RANK = "https://gist.githubusercontent.com/jinjier/7a405fad753f996d85ed43073e3bf009/raw/29bf7a4635c1283a1415aad9fb335f92ece2972b/250.csv"
    BASE_URL_STAR_RANK = ""  # DmmUtil supports

    def random_get_av_from_rank(self) -> Tuple[int, str]:
        code, resp = self.send_req(self.BASE_URL_AV_RANK)
        if code != 200:
            return code, None
        lines = str(resp.text).splitlines()
        id = lines[random.randint(0, len(lines) - 1)].split(",")[1]
        return 200, id

    def get_av_250_rank(self) -> Tuple[int, list]:
        code, resp = self.send_req(self.BASE_URL_AV_RANK)
        if code != 200:
            return code, None
        lines = str(resp.text).splitlines()
        return 200, [line.split(",")[1] for line in lines]


class JavDbUtil(BaseUtil):
    BASE_URL = "https://javdb.com"
    BASE_PARAM_NICE_AVS_OF_STAR = "?sort_type=1"
    PAT_SCORE = re.compile(r"(\d+\.?\d+)分")

    def __init__(
        self,
        proxy_addr="",
        use_cache=True,
        max_home_page_count=100,
        max_new_avs_count=8,
        base_url=BASE_URL,
    ):
        """Initialize

        :param str proxy_addr: proxy address, defaults to ''
        :param bool use_cache: whether to use cache, defaults to True
        :param int max_home_page_count: maximum home page pages to crawl, defaults to 100
        :param int max_new_avs_count: number of newest AVs to fetch, defaults to 8
        :param str base_url: base url, defaults to BASE_URL
        """
        super().__init__(proxy_addr, use_cache)
        self.base_url = base_url
        self.base_url_new_av = self.base_url + "/?vft=1&vst=1"
        self.base_url_search = self.base_url + "/search?q="
        self.base_url_video = self.base_url + "/v/"
        self.base_url_actor = self.base_url + "/actors/"
        self.base_url_search_star = self.base_url + "/search?f=actor&q="
        self.max_home_page_count = max_home_page_count
        self.max_new_avs_count = max_new_avs_count

    def get_max_page(self, url: str) -> Union[Tuple[int, None], Tuple[int, int]]:
        """Get the maximum page number for a paginated resource

        :param str url: page url
        :return tuple[int, int]: status code and max page number
        """
        code, resp = self.send_req(url)
        if code != 200:
            return code, None
        try:
            soup = self.get_soup(resp)
            last_page = int(
                soup.find(class_="pagination-list").find_all("li")[-1].a.text
            )
            if not last_page:
                return 404, None
            return 200, last_page
        except Exception as e:
            self.log.error(f"JavDbUtil: failed to get max page from {url}: {e}")
            return 404, None

    def get_new_ids(self) -> Tuple[int, any]:
        """Get the list of newest IDs

        :return Tuple[int, list]: status code and list of IDs
        """
        return self.get_ids_from_page(self.base_url_new_av)

    def get_ids_from_page(
        self, url: str
    ) -> Union[Tuple[int, None], Tuple[int, List[Any]]]:
        """Get ID list from a page URL

        :param str url: home/search page url
        :return Tuple[int, list]: status code and id list
        """
        code, resp = self.send_req(url=url)
        if code != 200:
            return code, None
        try:
            soup = self.get_soup(resp)
            items = soup.find_all(class_="item")
            ids = [
                item.find(class_="video-title").strong.text.strip() for item in items
            ]
            if not ids:
                return 404, None
            return 200, ids
        except Exception as e:
            self.log.error(f"JavDbUtil: failed to get id list from page: {e}")
            return 404, None

    def get_star_page_by_star_name(
        self, star_name
    ) -> Union[Tuple[int, None], Tuple[int, str]]:
        code, resp = self.send_req(url=self.base_url_search_star + star_name)
        if code != 200:
            return code, None
        try:
            soup = self.get_soup(resp)
            url = soup.find(class_="actor-box").find("a").attrs["href"]
            if not url:
                return 404, None
            return 200, f"{self.base_url}{url}"
        except Exception as e:
            self.log.error(f"JavDbUtil: failed to get star page: {e}")
            return 404, None

    def fuzzy_search_stars(
        self, text
    ) -> Union[Tuple[int, None], Tuple[int, List[Any]]]:
        """Fuzzy search actors by name

        :param str text: actor name
        :return Tuple[int, list]: status code and list of actor names
        """
        code, resp = self.send_req(url=self.base_url_search_star + text)
        if code != 200:
            return code, None
        try:
            soup = self.get_soup(resp)
            actor_boxs = soup.find_all(class_="actor-box")
            names = [box.find("a")["title"] for box in actor_boxs]
            if not names:
                return 404, None
            names = [name.split(",")[0] for name in names]
            names = list(set(names))
            return 200, names
        except Exception as e:
            self.log.error(f"JavDbUtil: fuzzy searching actors failed: {e}")
            return 404, None

    def get_id_by_star_name(
        self, star_name: str, page=-1
    ) -> Union[Tuple[int, None], Tuple[int, Any]]:
        """Get a single ID by actor name

        :param str star_name: actor name
        :param int page: which page to fetch; -1 means random
        :return tuple[int, str]: status code and ID
        """
        code, ids = self.get_ids_by_star_name(star_name, page)
        if code != 200:
            return code, None
        return 200, random.choice(ids)

    def get_ids_by_star_name(
        self, star_name: str, page=-1
    ) -> Union[Tuple[Any, None], Tuple[int, Any], Tuple[int, None]]:
        """Get a list of IDs by actor name

        :param str star_name: actor name
        :param int page: which page to fetch; -1 means random
        :return tuple[int, list]: status code and list of IDs
        """
        code, base_page_url = self.get_star_page_by_star_name(star_name)
        if code != 200:
            return code, None
        try:
            if page != -1:
                url = f"{base_page_url}?page={page}"
            else:
                code, max_page = self.get_max_page(base_page_url)
                if code != 200:
                    return code, None
                url = f"{base_page_url}?page={random.randint(1, max_page)}"
            code, ids = self.get_ids_from_page(url)
            if code != 200:
                return code, None
            return 200, ids
        except Exception as e:
            self.log.error(f"JavDbUtil: failed to get ids by actor name: {e}")
            return 404, None

    def get_new_ids_by_star_name(
        self, star_name: str
    ) -> Union[Tuple[Any, None], Tuple[int, Any], Tuple[int, None]]:
        """Get newest IDs for an actor

        :param str star_name: actor name
        :return Tuple[int, list]: status code and list of new IDs
        """
        code, url = self.get_star_page_by_star_name(star_name)
        if code != 200:
            return code, None
        try:
            code, ids = self.get_ids_from_page(url)
            if code != 200:
                return code, None
            return 200, ids[: self.max_new_avs_count]
        except Exception as e:
            self.log.error(f"JavDbUtil: failed to get newest ids by actor name: {e}")
            return 404, None

    def get_nice_avs_by_star_name(
        self, star_name: str, cookie: str
    ) -> Union[
        Tuple[Any, None], Tuple[int, None], Tuple[int, List[Dict[str, Union[str, Any]]]]
    ]:
        """Get high-rated AVs by actor name (login required)

        :param str star_name: actor name
        :param str cookie: requires login; `_jdb_session` in cookie is required
        :return Tuple[int, list]: status code and list of rated AVs
        Single item structure:
        {
            'rate': rate, # rating
            'id': id # AV id
        }
        """
        code, base_page_url = self.get_star_page_by_star_name(star_name)
        if code != 200:
            return code, None
        url = f"{base_page_url}{self.BASE_PARAM_NICE_AVS_OF_STAR}"
        code, resp = self.send_req(
            url=url, headers={"cookie": cookie, "user-agent": self.ua_desktop()}
        )
        if code != 200:
            return code, None
        try:
            soup = self.get_soup(resp)
            items = soup.find_all(class_="item")
            res = []
            for item in items:
                try:
                    res.append(
                        {
                            "rate": self.PAT_SCORE.findall(
                                item.find(class_="score").text
                            )[0],
                            "id": item.find(class_="video-title").strong.text.strip(),
                        }
                    )
                except Exception:
                    pass
            if not res:
                return 404, None
            return 200, res
        except Exception as e:
            self.log.error(f"JavDbUtil: failed to parse rated av list: {e}")
            return 404, None

    def get_javdb_id_by_id(self, id: str) -> Union[Tuple[int, None], Tuple[int, Any]]:
        """Get JavDB internal ID from public ID

        :param id: public id
        :return: tuple[int, str] status code and JavDB internal ID
        """
        code, resp = self.send_req(url=self.base_url_search + id)
        if code != 200:
            return code, None
        try:
            soup = self.get_soup(resp)
            items = soup.find_all(class_="item")
            for item in items:
                if item.find(class_="video-title").strong.text.strip() == id.upper():
                    return 200, item.find("a")["href"].split("/")[-1]
            return 404, None  # if there is no correct result, return 404
        except Exception as e:
            self.log.error(f"JavDbUtil: failed to get JavDB internal id by id: {e}")
            return 404, None

    def get_javdb_ids_from_page(
        self, url: str
    ) -> Union[Tuple[int, None], Tuple[int, List[Any]]]:
        """Get JavDB internal IDs from a page URL

        :param url: home/search page url
        :return: Tuple[int, list]: status code and list of JavDB internal IDs
        """
        code, resp = self.send_req(url=url)
        if code != 200:
            return code, None
        try:
            soup = self.get_soup(resp)
            items = soup.find_all(class_="item")
            ids = [item.find("a")["href"].split("/")[-1] for item in items]
            if not ids:
                return 404, None
            return 200, ids
        except Exception as e:
            self.log.error(f"JavDbUtil: failed to get JavDB ids from page: {e}")
            return 404, None

    def get_id_from_home(self) -> Union[Tuple[Any, None], Tuple[int, Any]]:
        """Get a random ID from the homepage

        :return Tuple[int, str]: status code and ID
        """
        code, resp = self.get_ids_from_page(url=self.base_url)
        if code != 200:
            return code, None
        else:
            return 200, random.choice(resp)

    def get_javdb_id_from_home(self) -> Union[Tuple[Any, None], Tuple[int, Any]]:
        """Get a random JavDB internal ID from the homepage

        :return Tuple[int, str]: status code and JavDB internal ID
        """
        code, resp = self.get_javdb_ids_from_page(url=self.base_url)
        if code != 200:
            return code, None
        else:
            return 200, random.choice(resp)

    def get_ids_from_home(self) -> Union[Tuple[Any, None], Tuple[int, Any]]:
        """Get all IDs from the homepage

        :return Tuple[int, list]: status code and list of IDs
        """
        code, resp = self.get_ids_from_page(url=self.base_url)
        if code != 200:
            return code, None
        else:
            return 200, resp

    def get_javdb_ids_from_home(self) -> Union[Tuple[Any, None], Tuple[int, Any]]:
        """Get all JavDB internal IDs from the homepage

        :return Tuple[int, list]: status code and list of JavDB internal IDs
        """
        code, resp = self.get_javdb_ids_from_page(url=self.base_url)
        if code != 200:
            return code, None
        else:
            return 200, resp

    def get_ids_by_tag(self, tag: str) -> Tuple[int, list]:
        """Get IDs by tag

        :param str tag: tag
        :return Tuple[int, list]: status code and list of IDs
        """
        url = f"{self.base_url_search}{tag}"
        return self.get_ids_from_page(url)

    def get_javdb_ids_by_tag(self, tag: str) -> Tuple[int, list]:
        """Get JavDB IDs by tag

        :param str tag: tag
        :return Tuple[int, list]: status code and list of JavDB IDs
        """
        url = f"{self.base_url_search}{tag}"
        return self.get_javdb_ids_from_page(url)

    def get_cover_by_id(self, id: str) -> Union[Tuple[int, None], Tuple[int, Any]]:
        """Get cover image by public ID

        :param str id: public id
        :return Tuple[int, str]: status code and cover url
        """
        code, resp = self.send_req(url=self.base_url_search + id)
        if code != 200:
            return code, None
        try:
            soup = self.get_soup(resp)
            items = soup.find_all(class_="item")
            for item in items:
                if item.find(class_="video-title").strong.text.strip() == id.upper():
                    return 200, item.find("img")["src"]
            else:
                return 404, None
        except Exception as e:
            self.log.error(f"JavDbUtil: failed to get cover by id: {e}")
            return 404, None

    def get_cover_by_javdb_id(
        self, javdb_id: str
    ) -> Union[Tuple[int, None], Tuple[int, Union[str, Any]]]:
        """Get cover image by JavDB internal ID

        :param str javdb_id: JavDB internal ID
        :return Tuple[int, str]: status code and cover url
        """
        code, resp = self.send_req(url=self.base_url_video + javdb_id)
        if code != 200:
            return code, None
        try:
            soup = self.get_soup(resp)
            cover = soup.find(class_="column column-video-cover")
            if not cover:
                return 404, None
            return 200, cover.find("img")["src"]
        except Exception as e:
            self.log.error(f"JavDbUtil: failed to get cover by JavDB id: {e}")
            return 404, None

    def get_pv_by_id(
        self, id: str
    ) -> Union[Tuple[Any, None], Tuple[int, None], Tuple[int, Union[str, Any]]]:
        code, j_id = self.get_javdb_id_by_id(id)
        if code != 200:
            return code, None
        code, resp = self.send_req(url=self.base_url_video + j_id)
        if code != 200:
            return code, None
        try:
            soup = self.get_soup(resp)
            url = soup.find(id="preview-video").find("source").attrs["src"]
            if not url:
                return 404, None
            if "http" not in url:
                url = f"https:{url}"
            return 200, url
        except Exception as e:
            self.log.error(f"JavDbUtil: failed to get preview video: {e}")
            return 404, None

    def get_samples_by_id(
        self, id: str
    ) -> Union[Tuple[Any, None], Tuple[int, None], Tuple[int, List[Any]]]:
        code, j_id = self.get_javdb_id_by_id(id)
        if code != 200:
            return code, None
        code, resp = self.send_req(url=self.base_url_video + j_id)
        if code != 200:
            return code, None
        try:
            soup = self.get_soup(resp)
            img_tags = soup.find_all(class_="tile-item")
            if not img_tags:
                return 404, None
            return 200, [t.attrs["href"] for t in img_tags]
        except Exception as e:
            self.log.error(f"JavDbUtil: failed to get preview images: {e}")
            return 404, None

    def get_av_by_javdb_id(
        self,
        javdb_id: str,
        is_nice: bool,
        is_uncensored: bool,
        sex_limit: bool = False,
        magnet_max_count=10,
    ) -> Tuple[int, any]:
        """Get AV information by JavDB internal ID

        :param javdb_id: JavDB internal ID
        :param bool is_nice: whether to filter for HD and subtitled magnets
        :param bool is_uncensored: whether to filter for uncensored magnets
        :param bool sex_limit: whether to include only female actors
        :param int magnet_max_count: max number of magnets after filtering (default 10)
        :return Tuple[int, any]: status code and av dict

        AV format:
        {
            'id': '',       # public id
            'date': '',     # release date
            'title': '',    # title
            'title_cn': '', # Chinese title
            'img': '',      # cover url
            'duration': '', # duration (minutes)
            'producer': '', # producer
            'publisher': '',# publisher
            'series': '',   # series
            'score': '',    # score
            'tags': [],     # tags
            'stars': [],    # actors
            'magnets': [],  # magnets
            'url': '',      # url
        }

        Magnet format:
        {
            'link': '', # link
            'size': '', # size
            'hd': '0',  # is HD 0 no | 1 yes
            'zm': '0',  # has subtitles 0 no | 1 yes
            'uc': '0',  # uncensored 0 no | 1 yes
            'size_no_unit': float # size normalized (no unit) for sorting; present when filtering
        }

        Actor format:
        {
            'name': '', # actor name
            'id': '',   # actor id
            'sex': ''   # actor sex
        }
        """
        code, resp = self.send_req(url=self.base_url_video + javdb_id)
        if code != 200:
            return code, None
        try:
            av = {
                "id": "",
                "date": "",
                "img": "",
                "title": "",
                "title_cn": "",
                "duration": "",
                "producer": "",
                "publisher": "",
                "series": "",
                "score": "",
                "tags": [],
                "stars": [],
                "magnets": [],
                "url": self.base_url_video + javdb_id,
            }
            soup = self.get_soup(resp)
            # get meta information
            title_cn = soup.find("strong", {"class": "current-title"})
            title = soup.find("span", {"class": "origin-title"})
            if not title:
                title, title_cn = title_cn, ""
            av["title_cn"] = title_cn.text.strip() if title_cn else ""
            av["title"] = title.text.strip() if title else ""
            av["img"] = soup.find("div", {"class": "column column-video-cover"}).find(
                "img"
            )["src"]
            # Because the nav bar structure varies depending on available info,
            # iterate over the blocks to extract metadata
            metainfos = soup.find("nav", {"class": "panel movie-panel-info"}).find_all(
                "div", {"class": "panel-block"}
            )
            for info in metainfos:  # iterate over nav bar info
                text = unicodedata.normalize("NFKD", re.sub("[\n ]", "", info.text))
                if re.search("番號:.+", text):
                    av["id"] = re.search("(番號: )(.+)", text).group(2).strip()
                elif re.search("日期:.+", text):
                    av["date"] = re.search("(日期: )(.+)", text).group(2).strip()
                elif re.search("\d+(分鍾)", text):
                    av["duration"] = int(re.search("(\d+)(分鍾)", text).group(1))
                elif re.search("片商:.+", text):
                    av["producer"] = re.search("(片商: )(.+)", text).group(2).strip()
                elif re.search("發行:.+", text):
                    av["publisher"] = re.search("(發行: )(.+)", text).group(2).strip()
                elif re.search("系列:.+", text):
                    av["series"] = re.search("(系列: )(.+)", text).group(2).strip()
                elif re.search("類別:.+", text):
                    av["tags"] = re.search("(類別: )(.+)", text).group(2).split(", ")
                elif re.search("評分:.+", text):
                    av["score"] = (
                        re.search("(評分: +)(\d+\.*\d*)(分.+)", text).group(2).strip()
                    )
                elif re.search("演員:.+", text):
                    actor_info = info.find_all(("a", "strong"))[1:]
                    for a in range(len(actor_info) // 2):
                        actor = {
                            "name": actor_info[a * 2].text.strip(),
                            "id": actor_info[a * 2]["href"].split("/")[-1],
                            "sex": (
                                "女"
                                if actor_info[a * 2 + 1].text.endswith("♀")
                                else "男"
                            ),
                        }
                        if not (sex_limit and actor["sex"] == "男"):
                            av["stars"].append(actor)
            # get magnet links
            magnet_list = soup.find_all(
                "div", {"class": "item columns is-desktop"}
            ) + soup.find_all("div", {"class": "item columns is-desktop odd"})
            for link in magnet_list:
                magnet = {
                    "link": link.find("a")["href"],
                    "hd": "0",
                    "zm": "0",
                    "uc": "0",
                    "size": "0",
                }
                # get size
                size = link.find("span", {"class": "meta"})
                if size:
                    magnet["size"] = size.text.strip().split(",")[0]
                # check if uncensored
                title = link.find("span", {"class": "name"}).text
                if any(
                    k in title
                    for k in [
                        "-U",
                        "无码",
                        "無碼",
                        "无码流出",
                        "無碼流出",
                        "无码破解",
                        "無碼破解",
                        "uncensored",
                        "Uncensored",
                    ]
                ):
                    magnet["uc"] = "1"
                # check tags
                tags_elements = link.find("div", {"class": "tags"})
                if tags_elements:
                    tags_contents = tags_elements.findAll("span")
                    for i in tags_contents:
                        if i.text.strip() == "高清":
                            magnet["hd"] = "1"
                        elif i.text.strip() == "字幕":
                            magnet["zm"] = "1"
                av["magnets"].append(magnet)
            if is_uncensored:
                av["magnets"] = MagnetUtil.get_nice_magnets(
                    av["magnets"], "uc", expect_val="1"
                )
            if is_nice:
                magnets = av["magnets"]
                magnets = MagnetUtil.get_nice_magnets(
                    magnets, "hd", expect_val="1"
                )  # filter HD
                magnets = MagnetUtil.get_nice_magnets(
                    magnets, "zm", expect_val="1"
                )  # filter subtitles
                magnets = MagnetUtil.sort_magnets(magnets)  # sort by size descending
                magnets = magnets[0:magnet_max_count]
                av["magnets"] = magnets
            return 200, av
        except Exception as e:
            self.log.error(f"JavDbUtil: failed to get av info: {e}")
            return 404, None

    def get_av_by_id(
        self,
        id: str,
        is_nice: bool,
        is_uncensored: bool,
        sex_limit: bool = False,
        magnet_max_count=10,
    ) -> Tuple[int, any]:
        """Get AV info for a public ID via JavDB

        :param str id: public id
        :param bool is_nice: filter for HD and subtitled magnets
        :param bool is_uncensored: filter for uncensored magnets
        :param int magnet_max_count: max magnets after filtering (default 10)
        :return Tuple[int, dict]: status code and AV dict

        AV format:
        {
            'id': '',       # public id
            'date': '',     # release date
            'title': '',    # title
            'title_cn': '', # Chinese title
            'img': '',      # cover url
            'duration': '', # duration (minutes)
            'producer': '', # producer
            'publisher': '',# publisher
            'series': '',   # series
            'score': '',    # score
            'tags': [],     # tags
            'stars': [],    # actors
            'magnets': [],  # magnets
            'url': '',      # url
        }

        Magnet format:
        {
            'link': '', # link
            'size': '', # size
            'hd': '0',  # is HD 0 no | 1 yes
            'zm': '0',  # has subtitles 0 no | 1 yes
            'uc': '0',  # uncensored 0 no | 1 yes
            'size_no_unit': float # size normalized (no unit) for sorting
        }

        Actor format:
        {
            'name': '', # actor name
            'id': '',   # actor id
            'sex': ''   # actor sex
        }
        """
        code, j_id = self.get_javdb_id_by_id(id)
        return (
            self.get_av_by_javdb_id(
                j_id, is_nice, is_uncensored, sex_limit, magnet_max_count
            )
            if code == 200
            else (code, None)
        )


class JavLibUtil(BaseUtil):
    BASE_URL = "https://www.javlibrary.com"
    # max number of ranking pages
    MAX_RANK_PAGE = 25

    def __init__(
        self,
        proxy_addr="",
        use_cache=True,
        base_url=BASE_URL,
    ):
        """Initialize JavLibUtil

        :param str proxy_addr: proxy address, defaults to ''
        :param bool use_cache: whether to use cache, defaults to True
        :param str base_url: base url, defaults to BASE_URL
        """
        super().__init__(proxy_addr, use_cache)
        self.base_url = base_url
        # nice
        self.base_url_best_rated_last_month = (
            self.base_url + "/cn/vl_bestrated.php?mode=1&page="
        )
        self.base_url_best_rated_all = (
            self.base_url + "/cn/vl_bestrated.php?mode=2&page="
        )
        self.base_url_most_wanted_last_month = (
            self.base_url + "/cn/vl_mostwanted.php?&mode=1&page="
        )
        self.base_url_most_wanted_all = (
            self.base_url + "/cn/vl_mostwanted.php?&mode=2&page="
        )
        # new
        self.base_url_new_release_have_comment = (
            self.base_url + "/cn/vl_newrelease.php?&mode=1&page="
        )
        self.base_url_new_release_all = (
            self.base_url + "/cn/vl_newrelease.php?&mode=2&page="
        )
        self.base_url_new_entries = self.base_url + "/cn/vl_newentries.php?page="
        self.urls_nice = [
            self.base_url_best_rated_last_month,
            self.base_url_best_rated_all,
            self.base_url_most_wanted_last_month,
            self.base_url_most_wanted_all,
        ]
        self.urls_new = [
            self.base_url_new_release_have_comment,
            self.base_url_new_release_all,
            self.base_url_new_entries,
        ]
        # search
        self.base_url_search_av = self.base_url + "/cn/vl_searchbyid.php?keyword="
        # comment
        self.base_url_comment = self.base_url + "/cn/videocomments.php?v="
        # review (top reviews)
        self.base_url_review = self.base_url + "/cn/videoreviews.php?v="

    def get_headers(self):
        return {
            "cookie": "over18=18;",
            "user-agent": self.ua_desktop(),
        }

    def get_random_ids_from_rank_by_page(
        self, page: int, list_type: int
    ) -> Union[Tuple[int, None], Tuple[int, List[Any]]]:
        """Get IDs from a ranking page

        :param int page: page number
        :param int list_type: ranking type 0 nice | 1 new
        :return Tuple[int, list]: status code and list of IDs
        """
        url = None
        if list_type == 0:
            url = random.choice(self.urls_nice)
        elif list_type == 1:
            url = random.choice(self.urls_new)
        code, resp = self.send_req(url=url + str(page), headers=self.get_headers())
        if code != 200:
            return code, None
        try:
            soup = self.get_soup(resp)
            tag_ids = soup.find_all(class_="id")
            ids = [tag.text for tag in tag_ids]
            if len(ids) > 0:
                return 200, ids
            else:
                return 404, None
        except Exception as e:
            self.log.error(f"JavLibUtil: failed to get ids from rank page: {e}")
            return 404, None

    def get_random_id_from_rank(
        self, list_type: int
    ) -> Union[Tuple[Any, None], Tuple[int, Any]]:
        """Get a random ID from ranking lists

        :param int list_type: ranking type 0 nice | 1 new
        :return Tuple[int, str]: status code and ID
        """
        page = random.randint(1, self.MAX_RANK_PAGE)
        code, ids = self.get_random_ids_from_rank_by_page(
            page=page, list_type=list_type
        )
        if code != 200:
            return code, None
        else:
            return 200, random.choice(ids)

    def get_comments_by_id(
        self, id: str
    ) -> Union[Tuple[int, None], Tuple[int, List[Any]]]:
        """Get top comments for a given ID (up to 5)

        :param str id: public id
        :return Tuple[int, list]: status code and list of comments
        """
        url = self.base_url_search_av + id
        code, resp = self.send_req(url=url, headers=self.get_headers())
        if code != 200:
            return code, None
        if resp.url == url:
            try:
                soup = self.get_soup(resp)
                videos = soup.find_all(class_="video")
                video_href = videos[0].a["href"]
                javlib_av_id = video_href[video_href.find("v=") + 2 :]
            except Exception as e:
                self.log.error(f"JavLibUtil: failed to get comments for {id}: {e}")
                return 404, None
        else:
            r_url = resp.url
            javlib_av_id = r_url[r_url.find("v=") + 2 :]
        comment_url = self.base_url_review + javlib_av_id
        code, resp = self.send_req(url=comment_url, headers=self.get_headers())
        if code != 200:
            return code, None
        try:
            soup = self.get_soup(resp)
            comment_tags = soup.find_all(class_="t")
            comments = []
            for c in comment_tags:
                comments.append(c.text)
            if comments == []:
                return 404, None
            return 200, comments[:5]
        except Exception as e:
            self.log.error(f"JavLibUtil: failed to get comments by {id}: {e}")
            return 404, None


class DmmUtil(BaseUtil):
    BASE_URL = "https://www.dmm.co.jp"
    PAT_CID = re.compile(r"/cid=.+/")
    PAT_CID_REAL = re.compile(r"[A-Za-z]+0+[0-9]+")
    PAT_AV = re.compile(r"[a-z]+\d+")

    def __init__(
        self,
        proxy_addr="",
        use_cache=True,
        base_url=BASE_URL,
    ):
        """Initialize DMM utility

        :param str proxy_addr: proxy server address, defaults to ''
        :param bool use_cache: whether to use cache, defaults to True
        :param str base_url: base URL, defaults to BASE_URL
        """
        super().__init__(proxy_addr, use_cache)
        self.base_url = base_url
        self.base_url_search_av = self.base_url + "/mono/-/search/=/searchstr="
        self.base_url_search_av_monthly = (
            self.base_url + "/monthly/dream/-/list/search/=/sort=ranking/?searchstr="
        )
        self.base_url_search_star = (
            "https://www.dmm.co.jp/search/=/limit=30/sort=ranking/searchstr="
        )
        self.base_url_top_stars = (
            self.base_url + "/digital/videoa/-/ranking/=/type=actress"
        )

    def get_id_by_cid(self, cid: str) -> str:
        id_0 = self.PAT_AV.findall(cid)[0]
        id_num = re.search(r"[1-9]\d*", id_0).group()
        id_pre = re.sub(r"\d*$", "", id_0)
        return f"{id_pre}-{id_num}"

    def get_pv_by_id(self, id: str) -> Union[Tuple[int, None], Tuple[int, Any]]:
        """Get preview video URL from DMM by public ID

        :param str id: public id
        :return tuple[int, str]: status code and preview video URL
        """
        # search for id
        url = self.base_url_search_av + id
        code, resp = self.send_req(
            url=url,
            headers={
                "user-agent": self.ua_mobile(),
            },
            cookies={
                "age_check_done": "1",
            },
        )
        if code != 200:
            return code, None
        try:
            soup = self.get_soup(resp)
            res = soup.find(class_="box-sampleplay")
            return 200, res.a["href"]
        except Exception as e:
            self.log.error(
                f"DmmUtil: failed to get preview video from DMM for {id}: {e}"
            )
            return 404, None

    def get_cid_from_link(self, lk: str) -> Union[None, str]:
        try:
            match = self.PAT_CID.findall(lk)
            cid = match[0].replace("/cid=", "").replace("/", "")
            # cid = self.CID_PAT_REAL.findall(cid)[0]
            return cid
        except Exception:
            return None

    def get_cids(self, url: str) -> Union[Tuple[int, None], Tuple[int, List[str]]]:
        code, resp = self.send_req(
            url=url,
            headers={
                "user-agent": self.ua_desktop(),  # desktop pages are easier to scrape
            },
            cookies={
                "age_check_done": "1",
            },
        )
        if code != 200:
            return code, None
        try:
            soup = self.get_soup(resp)
            tmb_tags = soup.find_all(class_="tmb")
            cids = []
            for tmb in tmb_tags:
                try:
                    lk = tmb.a["href"]
                    cid = self.get_cid_from_link(lk)
                    if cid:
                        cids.append(cid)
                except Exception:
                    pass
            return 200, cids
        except Exception as e:
            self.log.error(f"DmmUtil: failed to get cid list from {url}: {e}")
            return 404, None

    def get_cids_monthly(
        self, url: str
    ) -> Union[Tuple[int, None], Tuple[int, List[str]]]:
        code, resp = self.send_req(
            url=url,
            headers={
                "user-agent": self.ua_desktop(),  # desktop pages are easier to scrape
            },
            cookies={
                "age_check_done": "1",
            },
        )
        if code != 200:
            return code, None
        try:
            soup = self.get_soup(resp)
            li_tags = soup.find(id="list").find_all("li")
            cids = []
            for li in li_tags:
                try:
                    lk = li.div.a["href"]
                    cid = self.get_cid_from_link(lk)
                    if cid:
                        cids.append(cid)
                except Exception:
                    pass
            return 200, cids
        except Exception as e:
            self.log.error(f"DmmUtil: failed to get cid list from {url}: {e}")
            return 404, None

    def get_cids_by_tag(self, tag: str) -> Tuple[int, list]:
        return self.get_cids(self.base_url_search_av + tag)

    def get_cids_by_tag_monthly(self, tag: str) -> Tuple[int, list]:
        return self.get_cids_monthly(self.base_url_search_av_monthly + tag)

    def get_cids_by_link(self, lk: str) -> Tuple[int, list]:
        return self.get_cids(lk)

    def get_cids_by_link_monthly(self, lk: str) -> Tuple[int, list]:
        return self.get_cids_monthly(lk)

    def get_nice_avs_by_star_name(self, star_name: str) -> Tuple[int, any]:
        """Get high-rated AVs by actor name

        :param str star_name: actor name
        :return Tuple[int, list]: status code and list of AVs
        Single item structure:
        {
            'rate': rate, # rating
            'id': id # AV id
        }
        """
        # search actor
        url = self.base_url_search_star + star_name + "%20単体"
        code, resp = self.send_req(
            url=url,
            headers={
                "user-agent": self.ua_desktop(),  # desktop pages are easier to scrape
            },
            cookies={
                "age_check_done": "1",
            },
        )
        if code != 200:
            return code, resp
        try:
            soup = self.get_soup(resp)
            av_list = soup.find_all(class_="grid")[2]
            av_tags = av_list.find_all("div", recursive=False)
            avs = []
            for av in av_tags:
                try:
                    a_tag = av.find("a", href=True)
                    link = a_tag["href"] if a_tag else None
                    match = re.search(r"content=([^&]+)", link)
                    cid = match.group(1)
                    id = self.get_id_by_cid(cid)
                    score_span = av.find("span", class_="text-gray-500")
                    if score_span:
                        score_text = score_span.get_text(strip=True)
                        match = re.match(r"([\d.]+)", score_text)
                        score = float(match.group(1)) if match else None
                    else:
                        score = None
                    avs.append({"rate": score, "id": id})
                except Exception:
                    pass
            if avs == []:
                return 404, None
            avs = list(filter(lambda av: av["rate"] >= 4.0, avs))
            if len(avs) == 0:
                return 404, None
            return 200, avs
        except Exception as e:
            self.log.error(
                f"DmmUtil: failed to get nice avs by star name: {star_name}: {e}"
            )
            return 404, None

    def get_score_by_id(self, id: str) -> Tuple[int, any]:
        """Get score by public ID

        :param str id: public id
        :return tuple[int, str]: status code and score
        """
        # search id
        url = self.base_url_search_av + id
        code, resp = self.send_req(
            url=url,
            headers={
                "user-agent": self.ua_desktop(),  # desktop pages are easier to scrape
            },
            cookies={
                "age_check_done": "1",
            },
        )
        if code != 200:
            return code, resp
        try:
            soup = self.get_soup(resp)
            res = soup.find(class_="rate")
            return 200, res.span.span.text
        except Exception as e:
            self.log.error(f"DmmUtil: failed to get scroe by {id}: {e}")
            return 404, None

    def get_nice_pv_by_src(self, src: str) -> str:
        """Convert a regular src to a higher-quality src

        :param str src: original src
        :return str: nicer src
        """
        return src.replace("_sm_", "_dmb_")

    def get_top_stars(self, page=1) -> Union[Tuple[int, None], Tuple[int, List[Any]]]:
        """Get the list of stars from a ranking page by page

        :param int page: page number (1-5). There are 5 pages, 20 per page, 100 total. defaults to 1
        :return tuple[int, list]: status code and list of star names
        """
        url = self.base_url_top_stars + f"/page={page}/"
        code, resp = self.send_req(
            url=url,
            headers={
                "user-agent": self.ua_desktop(),  # desktop pages are easier to scrape
            },
            cookies={
                "age_check_done": "1",
            },
        )
        if code != 200:
            return code, None
        try:
            soup = self.get_soup(resp)
            res = soup.find_all(class_="data")
            if not res or len(res) == 0:
                return 404, None
            return 200, [obj.p.a.text for obj in res]
        except Exception as e:
            self.log.error(f"DmmUtil: fail to get top stars at page:{page}: {e}")
            return 404, None

    def get_all_top_stars(self) -> Union[Tuple[int, None], Tuple[int, List[Any]]]:
        """Get top 100 actresses from DMM ranking

        :return tuple[int, list]: status code and list of actress names
        """
        with concurrent.futures.ThreadPoolExecutor(max_workers=6) as executor:
            # crawl pages 1 to 5
            futures = {
                executor.submit(self.get_top_stars, page): page for page in range(1, 6)
            }
            results = {}
            # wait and collect results
            for future in concurrent.futures.as_completed(futures):
                code, res = future.result()
                if code != 200:
                    return 502, None
                results[futures[future]] = res
            stars = []
            for i in range(1, 6):
                if results[i] != None:
                    stars += results[i]
            if stars == []:
                return 404, None
            return 200, stars


class JavBusUtil(BaseUtil):
    BASE_URL = "https://www.javbus.com"

    def get_headers(self):
        # return {
        #     "authority": "www.javbus.com",
        #     "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
        #     "accept-language": "zh-CN,zh;q=0.9,en;q=0.8,en-US;q=0.7,fr-FR;q=0.6,fr;q=0.5",
        #     "cookie": f"bus_auth={self.bus_auth};",
        #     "dnt": "1",
        #     "sec-ch-ua-platform": '"Windows"',
        #     "user-agent": self.ua_desktop(),
        # }
        return {
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Sec-Fetch-Site": "none",
            "Accept-Encoding": "gzip, deflate, br",
            "Sec-Fetch-Mode": "navigate",
            "Host": "www.javbus.com",
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.5 Safari/605.1.15",
            "Accept-Language": "zh-CN,zh-Hans;q=0.9",
            "Sec-Fetch-Dest": "document",
            "Connection": "keep-alive",
        }

    def __init__(
        self,
        bus_auth="",
        proxy_addr="",
        use_cache=True,
        max_home_page_count=100,
        max_new_avs_count=8,
        base_url=BASE_URL,
    ):
        """Initialize JavBus utility

        :param str proxy_addr: proxy server address, defaults to ''
        :param bool use_cache: whether to use cache
        :param int max_home_page_count: maximum pages to crawl on homepage, defaults to 100
        :param int max_new_avs_count: number of newest AVs to fetch, defaults to 8
        :param str bus_auth: cookie value required for requests, defaults to empty string
        :param str base_url: base URL, defaults to BASE_URL
        """
        super().__init__(proxy_addr, use_cache)
        self.max_home_page_count = max_home_page_count
        self.max_new_avs_count = max_new_avs_count
        self.bus_auth = bus_auth
        self.base_url = base_url
        self.base_url_search_by_star_name = f"{self.base_url}/search"
        self.base_url_search_by_star_id = f"{self.base_url}/star"
        self.base_url_search_star = f"{self.base_url}/searchstar"
        self.base_url_magnet = f"{self.base_url}/ajax/uncledatoolsbyajax.php?lang=zh"
        self.base_url_genre = f"{self.base_url}/genre"

    def get_all_genres(
        self,
    ) -> Union[Tuple[int, None], Tuple[int, List[Dict[Any, Any]]]]:
        """Get all genres

        :return Tuple[int, list]: status code and list of genres
        """
        code, resp = self.send_req(url=self.base_url_genre, headers=self.get_headers())
        if code != 200:
            return code, None
        try:
            soup = self.get_soup(resp)
            boxes = soup.find_all(class_="row genre-box")
            genres = []
            for box in boxes:
                tags = box.find_all("a")
                for tag in tags:
                    genres.append({tag.text: tag["href"][tag["href"].rfind("/") + 1 :]})
            if genres == []:
                return 404, None
            return 200, genres
        except Exception as e:
            self.log.error(f"JavBusUtil: failed to get all genres: {e}")
            return 404, None

    def get_id_by_genre_id(self, genre: str) -> Tuple[int, str]:
        """Get an ID by genre id

        :param str genre: genre id
        :return Tuple[int, str]: status code and id
        """
        return self.get_id_from_page(base_page_url=f"{self.base_url_genre}/{genre}")

    def get_id_by_genre_name(self, genre: str) -> Tuple[int, str]:
        """Get an ID by genre name

        :param str genre: genre name
        :return Tuple[int, str]: status code and id
        """
        return self.get_id_from_page(base_page_url=f"{self.base_url_genre}/{genre}")

    def get_max_page(self, url: str) -> Union[Tuple[int, None], Tuple[int, int]]:
        """Get the maximum page number (only for pages <= 10)

        :param str url: page url
        :return tuple[int, int]: status code and max page number
        """
        code, resp = self.send_req(url, headers=self.get_headers())
        if code != 200:
            return code, None
        try:
            soup = self.get_soup(resp)
            tag_pagination = soup.find(class_="pagination pagination-lg")
            # if no pagination block, there is only the first page
            if not tag_pagination:
                return 200, 1
            tags_li = tag_pagination.find_all("li")
            return 200, int(tags_li[len(tags_li) - 2].a.text)
        except Exception as e:
            self.log.error(f"JavBusUtil: failed to get max page from {url}: {e}")
            return 404, None

    def get_ids_from_page(
        self, base_page_url: str, page=1
    ) -> Union[Tuple[int, None], Tuple[int, List[Any]]]:
        """Get all IDs from an AV list page

        :param str base_page: base page url (first page)
        :param int page: which page to fetch; defaults to 1
        :return tuple[int, list]: status code and list of IDs
        """
        if page != -1:
            url = f"{base_page_url}/{page}"
        else:
            code, max_page = self.get_max_page(base_page_url)
            if code != 200:
                return code, None
            url = f"{base_page_url}/{random.randint(1, max_page)}"
        code, resp = self.send_req(url=url, headers=self.get_headers())
        if code != 200:
            return code, None
        try:
            ids = []
            soup = self.get_soup(resp)
            tags = soup.find_all(class_="movie-box")
            for tag in tags:
                id_link = tag["href"]
                id = id_link[id_link.rfind("/") + 1 :]
                ids.append(id)
            if ids == []:
                return 404, None
            return 200, ids
        except Exception as e:
            self.log.error(
                f"JavBusUtil: failed to get ids from av list page {base_page_url}: {e}"
            )
            return 404, None

    def get_id_from_page(
        self, base_page_url: str, page=-1
    ) -> Union[Tuple[int, None], Tuple[int, Any]]:
        """Get a single ID from an AV list page

        :param str base_page: base page url (first page)
        :param int page: which page to fetch; -1 means random
        :return tuple[int, str]: status code and ID
        """
        code, ids = self.get_ids_from_page(base_page_url, page)
        if code != 200:
            return code, None
        return 200, random.choice(ids)

    def get_id_from_home(self, page=-1) -> Tuple[int, str]:
        """Get an ID from the javbus homepage

        :param int page: which page to fetch; -1 means random
        :return tuple[int, str]: status code and ID
        """
        if page == -1:
            page = random.randint(1, self.max_home_page_count)
        return self.get_id_from_page(base_page_url=self.base_url + "/page", page=page)

    def get_id_by_star_name(self, star_name: str, page=-1) -> Tuple[int, str]:
        """Get an ID by actor name

        :param str star_name: actor name
        :param int page: which page to fetch; -1 means random
        :return tuple[int, str]: status code and ID
        """
        return self.get_id_from_page(
            base_page_url=f"{self.base_url_search_by_star_name}/{star_name}",
            page=page,
        )

    def get_ids_by_star_name(self, star_name: str, page=-1) -> Tuple[int, list]:
        """Get a list of IDs by actor name

        :param str star_name: actor name
        :param int page: which page to fetch; -1 means random
        :return tuple[int, list]: status code and list of IDs
        """
        return self.get_ids_from_page(
            base_page_url=f"{self.base_url_search_by_star_name}/{star_name}",
            page=page,
        )

    def get_new_ids_by_star_name(
        self, star_name: str
    ) -> Union[Tuple[int, None], Tuple[int, Any]]:
        """Get newest IDs for an actor by name

        :param str star_name: actor name
        :return Tuple[int, list]: status code and list of latest IDs
        """
        code, ids = self.get_ids_from_page(
            base_page_url=f"{self.base_url_search_by_star_name}/{star_name}",
            page=1,
        )
        if code != 200:
            return code, None
        return 200, ids[: self.max_new_avs_count]

    def get_id_by_star_id(self, star_id: str, page=-1) -> Tuple[int, str]:
        """Get an ID by actor id

        :param str star_id: actor id
        :param int page: which page to fetch; -1 means random
        :return tuple[int, str]: status code and ID
        """
        return self.get_id_from_page(
            base_page_url=f"{self.base_url_search_by_star_id}/{star_id}",
            page=page,
        )

    def get_new_ids_by_star_id(
        self, star_id: str
    ) -> Union[Tuple[int, None], Tuple[int, list]]:
        """Get newest IDs by actor id

        :param str star_id: actor id
        :return tuple[int, list]: status code and list of latest IDs
        """
        code, ids = self.get_ids_from_page(
            base_page_url=f"{self.base_url_search_by_star_id}/{star_id}", page=1
        )
        if code != 200:
            return code, None
        return 200, ids[: self.max_new_avs_count]

    def get_samples_by_id(
        self, id: str
    ) -> Union[Tuple[int, None], Tuple[int, List[Union[str, Any]]]]:
        """Get sample images by public ID

        :param str id: public id
        :return tuple[int, list]: status code and list of sample image URLs
        """
        samples = []
        url = f"{self.base_url}/{id}"
        code, resp = self.send_req(url=url, headers=self.get_headers())
        if code != 200:
            return code, None
        try:
            soup = self.get_soup(resp)
            sample_tags = soup.find_all(class_="sample-box")
            for tag in sample_tags:
                sample_link = tag["href"]
                if sample_link.find("https") == -1:
                    sample_link = self.base_url + sample_link
                samples.append(sample_link)
            if samples == []:
                return 404, None
            return 200, samples
        except Exception as e:
            self.log.error(f"JavBusUtil: failed to get samples for {id}: {e}")
            return 404, None

    def check_star_exists(
        self, star_name: str
    ) -> Union[Tuple[int, None], Tuple[int, Dict[str, Union[str, Any]]]]:
        """Check whether an actor exists on javbus; return id and name if exists

        :param str star_name: actor name
        :return tuple[int, dict]: status code and dict with actor id and name
        dict format:
        {
            "star_id": star_id,
            "star_name": star_name
        }
        """
        code, resp = self.send_req(
            url=f"{self.base_url_search_star}/{star_name}",
            headers=self.get_headers(),
        )
        if code != 200:
            return code, None
        try:
            soup = self.get_soup(resp)
            star = soup.find(class_="avatar-box text-center")
            star_id = star["href"].split("star/")[1]
            res_star_name = star.find("img")["title"]
            return 200, {"star_id": star_id, "star_name": res_star_name}
        except Exception as e:
            self.log.error(
                f"JavBusUtil: failed to confirm actor {star_name} existence on javbus: {e}"
            )
            return 404, None

    def fuzzy_search_stars(
        self, text
    ) -> Union[Tuple[int, None], Tuple[int, List[Any]]]:
        """Fuzzy search actors by name

        :param str text: actor name
        :return Tuple[int, list]: status code and list of actor names
        """
        code, resp = self.send_req(
            url=f"{self.base_url_search_star}/{text}", headers=self.get_headers()
        )
        if code != 200:
            return code, None
        try:
            soup = self.get_soup(resp)
            actor_boxs = soup.find_all(class_="avatar-box text-center")
            names = [box.find("img")["title"] for box in actor_boxs]
            if not names:
                return 404, None
            names = list(set(names))
            return 200, names
        except Exception as e:
            self.log.error(f"JavDbUtil: fuzzy search for actors failed: {e}")
            return 404, None

    def get_av_by_id(
        self,
        id: str,
        is_nice: bool,
        is_uncensored: bool,
        magnet_max_count=10,
    ) -> Tuple[int, any]:
        """Get AV info from javbus by public ID

        :param str id: public id
        :param bool is_nice: filter for HD and subtitled magnets
        :param bool is_uncensored: filter for uncensored magnets
        :param int magnet_max_count: max magnets after filtering (default 10)
        :return tuple[int, dict]: status code and AV dict

        AV format:
        {
            'id': '',      # public id
            'title': '',   # title
            'img': '',     # cover url
            'date': '',    # release date
            'tags': [],    # tags
            'stars': [],   # actors
            'magnets': [], # magnets
            'url': '',     # url
        }

        Magnet format:
        {
            'link': '', # link
            'size': '', # size
            'hd': '0',  # is HD 0 no | 1 yes
            'zm': '0',  # has subtitles 0 no | 1 yes
            'uc': '0',  # uncensored 0 no | 1 yes
            'size_no_unit': float # normalized size for sorting
        }

        Actor format:
        {
            'name': '', # actor name
            'id': ''    # actor id
        }
        """
        id = id.lower()  # some IDs must be lowercase to be found on javbus
        av = {
            "id": id,
            "title": "",
            "img": "",
            "date": "",
            "tags": "",
            "stars": [],
            "magnets": [],
            "url": "",
        }
        url = f"{self.base_url}/{id}"
        av["url"] = url
        code, resp = self.send_req(url=url, headers=self.get_headers())
        if code != 200:
            return code, None
        soup = self.get_soup(resp)
        html = soup.prettify()
        try:
            # get cover and title
            big_image = soup.find(class_="bigImage")
            img = None
            if big_image:
                img = big_image["href"]
                if img.find("http") == -1:
                    av["img"] = self.base_url + img
                    av["title"] = big_image.img["title"]
            paras = soup.find(class_="col-md-3 info").find_all("p")
            for i, p in enumerate(paras):
                # get identifier
                if p.text.find("識別碼:") != -1:
                    av["id"] = "".join(
                        p.text.replace("識別碼:", "").replace('"', "").split()
                    )
                # get release date
                elif p.text.find("發行日期:") != -1:
                    av["date"] = "".join(
                        p.text.replace("發行日期:", "").replace('"', "").split()
                    )
                # get tags
                elif p.text.find("類別:") != -1:
                    tags = paras[i + 1].find_all("a")
                    av["tags"] = ["".join(tag.text.split()) for tag in tags]
                # get actors
                elif i == len(paras) - 1:
                    tags = p.find_all("a")
                    for tag in tags:
                        star = {"name": "", "id": ""}
                        star["name"] = "".join(tag.text.split())
                        star["id"] = tag["href"].split("star/")[1]
                        av["stars"].append(star)
        except Exception as e:
            self.log.error(f"JavBusUtil: failed to get av {id}: {e}")
        # get uc
        uc_pattern = re.compile(r"var uc = .+;")
        match = uc_pattern.findall(html)
        uc = None
        if match:
            uc = match[0].replace("var uc = ", "").replace(";", "")
        # get gid
        gid_pattern = re.compile(r"var gid = .+;")
        match = gid_pattern.findall(html)
        gid = None
        if match:
            gid = match[0].replace("var gid = ", "").replace(";", "")
        # if there are no magnets, return immediately
        if not uc and not gid:
            return 200, av
        # construct ajax URL to retrieve magnets
        url = f"{self.base_url_magnet}&gid={gid}&uc={uc}"
        headers = {
            "user-agent": self.ua(),
            "referer": f"{self.base_url}/{id}",
        }
        # send request to obtain page that contains magnets
        code, resp = self.send_req(url=url, headers=headers)
        # if no magnets or request failed, return
        if code != 200:
            return 200, av
        # parse page to extract magnets
        try:
            soup = self.get_soup(resp)
            trs = soup.find_all("tr")
            for tr in trs:
                magnet = {"link": "", "hd": "0", "zm": "0", "uc": "0"}
                tds = tr.find_all("td")
                for i, td in enumerate(tds):
                    if i == 0:
                        magnet["link"] = td.a["href"]
                        magnet_title = td.a.text.strip().lower()
                        if (
                            "uncensor" in magnet_title
                            or "無修正" in magnet_title
                            or "无修正" in magnet_title
                            or "无码" in magnet_title
                        ):
                            magnet["uc"] = "1"
                        links = td.find_all("a")
                        for link in links:
                            text = link.text.strip()
                            if text == "高清":
                                magnet["hd"] = "1"
                            elif text == "字幕":
                                magnet["zm"] = "1"
                    if i == 1:
                        magnet["size"] = td.a.text.strip()
                if magnet["link"] != "":
                    av["magnets"].append(magnet)
            if is_uncensored:
                av["magnets"] = MagnetUtil.get_nice_magnets(
                    av["magnets"], "uc", expect_val="1"
                )
            if is_nice:
                magnets = av["magnets"]
                magnets = MagnetUtil.get_nice_magnets(
                    magnets, "hd", expect_val="1"
                )  # filter HD
                magnets = MagnetUtil.get_nice_magnets(
                    magnets, "zm", expect_val="1"
                )  # filter subtitles
                magnets = MagnetUtil.sort_magnets(magnets)  # sort by size descending
                magnets = magnets[0:magnet_max_count]
                av["magnets"] = magnets
        except Exception as e:
            self.log.error(f"JavBusUtil: failed to get av {id}: {e}")
        return 200, av


class AvgleUtil(BaseUtil):
    BASE_URL = "https://api.avgle.com"

    def __init__(
        self,
        proxy_addr="",
        use_cache=True,
        base_url=BASE_URL,
    ):
        """Initialize Avgle utility

        :param str proxy_addr: proxy server address, defaults to ''
        :param bool use_cache: whether to use cache, defaults to True
        :param str base_url: base URL, defaults to BASE_URL
        """
        super().__init__(proxy_addr, use_cache)
        self.base_url = base_url

    def get_video_by_id(self, id: str) -> Tuple[int, any]:
        """Get video links from Avgle by public ID

        :param str id: public id
        :return tuple[int, dict]: status code and video links
        Video links format:
        {
            'fv': '', # full video link
            'pv': ''  # preview video link
        }
        """
        page = 0
        limit = 3
        url = f"{self.base_url}/v1/jav/{id}/{page}?limit={limit}"
        res = {"fv": "", "pv": ""}
        code, resp = self.send_req(url=url)
        if code != 200:
            return code, None
        if resp.json()["success"]:
            videos = resp.json()["response"]["videos"]
            if videos != []:
                for video in videos:
                    fv_url = video["video_url"].strip()
                    pv_url = video["preview_video_url"].strip()
                    if res["fv"] == "" and fv_url != "":
                        res["fv"] = fv_url
                    if res["pv"] == "" and pv_url != "":
                        res["pv"] = pv_url
            return code, res
        else:
            return 404, None

    def get_pv_by_id(self, id: str) -> Union[Tuple[int, None], Tuple[int, str]]:
        """Get preview video from Avgle by public ID

        :param str id: public id
        :return tuple[int, str]: status code and preview video link
        """
        code, res = self.get_video_by_id(id)
        if code != 200:
            return code, None
        if res["pv"] != "":
            return 200, res["pv"]
        else:
            return 404, None

    def get_fv_by_id(self, id: str) -> Union[Tuple[int, None], Tuple[int, str]]:
        """Get full video from Avgle by public ID

        :param str id: public id
        :return tuple[int, str]: status code and full video link
        """
        code, res = self.get_video_by_id(id)
        if code != 200:
            return code, None
        if res["pv"] != "":
            return 200, res["fv"]
        else:
            return 404, None


class MagnetUtil:
    @staticmethod
    def get_nice_magnets(magnets: list, prop: str, expect_val: any) -> list:
        """Filter magnet list by property

        :param list magnets: list of magnets to filter
        :param str prop: property to filter on
        :param any expect_val: expected value of the property
        :return list: filtered list of magnets
        """
        # cannot filter further
        if len(magnets) == 0:
            return []
        if len(magnets) == 1:
            return magnets
        magnets_nice = []
        for magnet in magnets:
            if magnet[prop] == expect_val:
                magnets_nice.append(magnet)
        # if filtering removed all, return the original list
        if len(magnets_nice) == 0:
            return magnets
        return magnets_nice

    @staticmethod
    def sort_magnets(magnets: list) -> list:
        """Sort magnet list by size

        :param list magnets: list of magnets
        :return list: sorted list of magnets
        """
        # normalize units to MB
        for magnet in magnets:
            magnet["size_no_unit"] = -1
            size = magnet["size"].lower().replace("gib", "gb").replace("mib", "mb")
            gb_idx = size.find("gb")
            mb_idx = size.find("mb")
            if gb_idx != -1:  # unit is GB
                magnet["size_no_unit"] = float(size[:gb_idx]) * 1024
            elif mb_idx != -1:  # unit is MB
                magnet["size_no_unit"] = float(size[:mb_idx])
        # sort by size_no_unit descending
        magnets = sorted(magnets, key=lambda m: m["size_no_unit"], reverse=True)
        return magnets


class SukebeiUtil(BaseUtil):
    BASE_URL = "https://sukebei.nyaa.si"

    def __init__(
        self,
        proxy_addr="",
        use_cache=True,
        base_url=BASE_URL,
    ):
        """Initialize Sukebei utility

        :param str proxy_addr: proxy server address, defaults to ''
        :param bool use_cache: whether to use cache, defaults to True
        :param str base_url: base URL, defaults to BASE_URL
        """
        super().__init__(proxy_addr, use_cache)
        self.base_url = base_url

    def get_av_by_id(
        self,
        id: str,
        is_nice: bool,
        is_uncensored: bool,
        magnet_max_count=10,
    ) -> Tuple[int, any]:
        """Fetch AV information from Sukebei by public ID

        :param str id: public id
        :param bool is_nice: whether to filter for HD and subtitled magnets
        :param bool is_uncensored: whether to filter for uncensored magnets
        :param int magnet_max_count: max number of magnets after filtering, defaults to 10
        :return tuple[int, dict]: status code and AV dict

        AV format:
        {
            'id': '',      # public id
            'title': '',   # title
            'img': '',     # cover URL | sukebei does not support
            'date': '',    # release date | sukebei does not support
            'tags': [],    # tags | sukebei does not support
            'stars': [],   # actors | sukebei does not support
            'magnets': [], # magnets
            'url': '',     # url
        }

        Magnet format:
        {
            'link': '', # link
            'size': '', # size
            'hd': '0',  # is HD 0 no | 1 yes | sukebei does not support
            'zm': '0',  # has subtitles 0 no | 1 yes | sukebei does not support
            'uc': '0',  # uncensored 0 no | 1 yes
            'size_no_unit': float # normalized size without unit, used for sorting; present when filtering
        }

        Actor format: | sukebei does not support
        {
            'name': '', # actor name
            'id': ''    # actor id
        }
        """
        av = {
            "id": id,
            "title": "",
            "img": "",
            "date": "",
            "tags": [],
            "stars": [],
            "magnets": [],
            "url": "",
        }
        qid = id.lower()
        if qid.find("fc2") != -1:
            qid = qid.replace("-", " ")
        # search for av
        url = f"{self.base_url}?q={qid}"
        code, resp = self.send_req(url=url)
        if code != 200:
            return code, None
        try:
            av["url"] = url
            soup = self.get_soup(resp)
            torrent_list = soup.find(class_="torrent-list")
            trs = torrent_list.tbody.find_all("tr")
            for i, tr in enumerate(trs):
                tds = tr.find_all("td")
                magnet = {
                    "link": "",  # link
                    "size": "",  # size
                    "hd": "0",  # is HD 0 no | 1 yes
                    "zm": "0",  # has subtitles 0 no | 1 yes
                    "uc": "0",  # uncensored 0 no | 1 yes
                }
                for j, td in enumerate(tds):
                    if j == 1:  # get title
                        title = td.a.text
                        if (
                            "uncensor" in title
                            or "無修正" in title
                            or "无修正" in title
                            or "无码" in title
                        ):
                            magnet["uc"] = "1"
                        if i == 0:
                            av["title"] = title
                    if j == 2:  # get magnet link
                        magnet["link"] = td.find_all("a")[-1]["href"]
                    if j == 3:  # get size
                        magnet["size"] = td.text
                av["magnets"].append(magnet)
            # filter magnets
            if is_uncensored:
                av["magnets"] = MagnetUtil.get_nice_magnets(
                    av["magnets"], "uc", expect_val="1"
                )
            if is_nice:
                magnets = av["magnets"]
                magnets = magnets[0:magnet_max_count]
                magnets = MagnetUtil.sort_magnets(magnets)
                av["magnets"] = magnets

        except Exception as e:
            self.log.error(f"SukebeiUtil: failed to get av {id}: {e}")
            return 404, None
        return 200, av

    def search_av_by_tag(self, tag: str) -> Tuple[int, any]:
        """Search videos by keyword

        :param str tag: keyword
        :return Tuple[int, list]: status code and list of videos
        Video item format:
        {
            "title": "",
            "loc": "", # /view/{num}
        }
        """
        url = f"{self.base_url}?q={tag}"
        code, resp = self.send_req(url=url)
        if code != 200:
            return code, None
        try:
            soup = self.get_soup(resp)
            torrent_list = soup.find(class_="torrent-list")
            trs = torrent_list.tbody.find_all("tr")
            avs = []
            for tr in trs:
                av = {
                    "title": "",
                    "loc": "",
                }
                tds = tr.find_all("td")
                av["title"] = tds[1].a["title"]
                av["loc"] = tds[1].a["href"]
                avs.append(av)
            if avs == []:
                return 404, None
            return 200, avs
        except Exception as e:
            self.log.error(f"SukebeiUtil: search av by {tag}: {e}")
            return 404, None

    def get_av_by_url(self, url: str) -> Tuple[int, any]:
        """Get AV by URL

        :param str url: URL
        :return Tuple[int, dict]: status code and resource
        Resource format:
        {
            "url": "",
            "title": "",
            "img": [],
            "magnet": "",
        }
        """
        code, resp = self.send_req(url=url)
        if code != 200:
            return code, None
        try:
            soup = self.get_soup(resp)
            av = {
                "url": url,
                "title": "",
                "img": [],
                "magnet": "",
            }
            av["title"] = soup.find(class_="panel-title").text
            av["magnet"] = soup.find(class_="card-footer-item")["href"]
            tag_desc = soup.find(id="torrent-description").text
            imgs = re.compile(r"\((.*?)\)").findall(tag_desc)
            av["img"] = [img for img in imgs]
            return 200, av
        except Exception as e:
            self.log.error(f"SukebeiUtil: get av by {url}: {e}")
            return 404, None


class WikiUtil(BaseUtil):
    logging.getLogger("wikipediaapi").setLevel(logging.ERROR)
    BASE_URL_JAPAN_WIKI = "https://ja.wikipedia.org/wiki"
    BASE_URL_CHINA_WIKI = "https://zh.wikipedia.org/wiki"

    def get_wiki_page_by_lang(
        self, topic: str, from_lang: str, to_lang: str
    ) -> Union[dict, None]:
        """Return a Wikipedia page in the requested language given a topic and source language.

        If no page is found, return None. If a page is found but the requested language is not available,
        return the original page info.

        :param str topic: search topic
        :param str from_lang: source language code
        :param str to_lang: target language code
        :return dict: result with keys:
        {
            'title': '', # title
            'url': '',   # URL
            'lang': ''   # language code
        }
        """
        try:
            wiki = wikipediaapi.Wikipedia(language=from_lang, proxies=self.proxy_json)
            page = wiki.page(title=topic)
            # links = page.links
            # for k in links.keys():
            #     if links[k].title.find(topic) != -1:
            #         print(links[k].fullurl)
            if page.text:
                langlinks = page.langlinks
                for k in langlinks.keys():
                    if k == to_lang:
                        return {
                            "title": langlinks[k].title,
                            "url": langlinks[k].fullurl,
                            "lang": langlinks[k].language,
                        }
                return {"title": page.title, "url": page.fullurl, "lang": from_lang}
        except Exception as e:
            self.log.error(
                f"WikiUtil: get wiki page by {topic} - {from_lang} - {to_lang}: {e}"
            )
            return None


class TransUtil(BaseUtil):
    def trans(self, text: str, from_lang="auto", to_lang="zh-CN") -> str:
        """Translate text using GoogleTranslator

        :param str text: text to translate
        :param str from_lang: source language code, defaults to 'auto'
        :param str to_lang: target language code, defaults to 'zh-CN'
        :return str: translated text; returns None on failure
        """
        try:
            return GoogleTranslator(
                source=from_lang, target=to_lang, proxies=self.proxy_json
            ).translate(text)
        except Exception as e:
            self.log.error(f"TransUtil: {e}")
