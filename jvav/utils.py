# -*- coding: UTF-8 -*-
import re
import lxml
import random
import typing
import logging
import requests
import wikipediaapi
import concurrent.futures
from bs4 import BeautifulSoup
from anti_useragent import UserAgent
from deep_translator import GoogleTranslator


class BaseUtil:
    def __init__(self, proxy_addr=""):
        """初始化

        :param str proxy_addr: 代理服务器地址, 默认为 ''
        """

        self.log = logging.getLogger(__name__)
        self.proxy_addr = ""
        if proxy_addr != "":
            self.proxy_addr = proxy_addr
        if self.proxy_addr != "":
            self.proxy_json = {"http": proxy_addr, "https": proxy_addr}
        else:
            self.proxy_json = {"http": "", "https": ""}

    @staticmethod
    def ua_mobile() -> str:
        """返回手机端 UserAgent

        :return str: 手机端 UserAgent
        """
        return UserAgent().android

    @staticmethod
    def ua_desktop() -> str:
        """返回桌面端 UserAgent

        :return str: 桌面端 UserAgent
        """
        return UserAgent(platform="windows").random

    @staticmethod
    def ua() -> str:
        """随机返回 UserAgent

        :return str: UserAgent
        """
        return UserAgent().random

    def send_req(
        self, url: str, headers={}, proxies={}
    ) -> typing.Tuple[int, requests.Response]:
        """发送请求

        :param str url: 地址
        :param dict headers: 请求头, 默认使用随机请求头
        :param dict proxies: 代理字典, 默认使用类初始化时指定的代理进行配置
        :return tuple[int, requests.Response] 状态码和请求返回值
        关于状态码:
        200: 成功
        404: 未找到
        502: 网络问题
        """
        if headers == {}:
            headers = {"user-agent": self.ua()}
        if proxies == {}:
            proxies = self.proxy_json
        try:
            resp = requests.get(
                url,
                proxies=proxies,
                headers=headers,
            )
            if resp.status_code != 200:
                return 404, None
            return 200, resp
        except Exception as e:
            self.log.error(f"BaseUtil: 访问 {url}: {e}")
            return 502, None

    @staticmethod
    def get_soup(resp: requests.Response) -> BeautifulSoup:
        """从请求结果得到 soup

        :param requests.Response resp: 请求结果
        :return BeautifulSoup
        """
        return BeautifulSoup(resp.text, "lxml")

    @staticmethod
    def write_html(resp: requests.Response):
        """将 html 代码写到 tmp.html

        :param requests.Response resp
        """
        with open(f"./tmp.html", "w") as f:
            f.write(resp.text)


class JavDbUtil(BaseUtil):
    BASE_URL = "https://javdb.com"
    BASE_URL_SEARCH = "https://javdb.com/search?q="

    def get_ids_from_page(self, url: str) -> typing.Tuple[int, list]:
        """从某个页面获取番号列表

        :param str url: 某个页面
        :return typing.Tuple[int, list]: 状态码和番号列表
        """
        code, resp = self.send_req(url=url)
        if code != 200:
            return code, None
        try:
            soup = self.get_soup(resp)
            items = soup.find_all(class_="item")
            ids = []
            for item in items:
                ids.append(item.find(class_="video-title").strong.text)
            if ids == []:
                return 404, None
            return 200, ids
        except Exception as e:
            self.log.error(f"JavDbUtil: 从某个页面获取番号列表: {e}")
            return 404, None

    def get_ids_by_tag(self, tag: str) -> typing.Tuple[int, list]:
        """根据标签获取番号列表

        :param str tag: 标签
        :return typing.Tuple[int, list]: 状态码和番号列表
        """
        url = f"{JavDbUtil.BASE_URL_SEARCH}{tag}"
        return self.get_ids_from_page(url)


class JavLibUtil(BaseUtil):
    BASE_URL = "https://www.javlibrary.com"
    # nice
    BASE_URL_BEST_RATED_LAST_MONTH = BASE_URL + "/cn/vl_bestrated.php?mode=1&page="
    BASE_URL_BEST_RATED_ALL = BASE_URL + "/cn/vl_bestrated.php?mode=2&page="
    BASE_URL_MOST_WANTED_LAST_MONTH = BASE_URL + "/cn/vl_mostwanted.php?&mode=1&page="
    BASE_URL_MOST_WANTED_ALL = BASE_URL + "/cn/vl_mostwanted.php?&mode=2&page="
    # new
    BASE_URL_NEW_RELEASE_HAVE_COMMENT = BASE_URL + "/cn/vl_newrelease.php?&mode=1&page="
    BASE_URL_NEW_RELEASE_ALL = BASE_URL + "/cn/vl_newrelease.php?&mode=2&page="
    BASE_URL_NEW_ENTRIES = BASE_URL + "/cn/vl_newentries.php?page="
    URLS_NICE = [
        BASE_URL_BEST_RATED_LAST_MONTH,
        BASE_URL_BEST_RATED_ALL,
        BASE_URL_MOST_WANTED_LAST_MONTH,
        BASE_URL_MOST_WANTED_ALL,
    ]
    URLS_NEW = [
        BASE_URL_NEW_RELEASE_HAVE_COMMENT,
        BASE_URL_NEW_RELEASE_ALL,
        BASE_URL_NEW_ENTRIES,
    ]
    # search
    BASE_URL_SEARCH_AV = BASE_URL + "/cn/vl_searchbyid.php?keyword="
    # comment
    BASE_URL_COMMENT = BASE_URL + "/cn/videocomments.php?v="
    # review 最佳评论
    BASE_URL_REVIEW = BASE_URL + "/cn/videoreviews.php?v="
    # 排行榜最大页数
    MAX_RANK_PAGE = 25

    def __init__(
        self,
        proxy_addr="",
        max_rank_page=MAX_RANK_PAGE,
    ):
        """初始化

        :param str proxy_addr: 代理服务器地址, 默认为 ''
        :param int max_rank_page: 排行榜的最大页数, 默认为 JavLibUtil.MAX_RANK_PAGE 页
        """
        super().__init__(proxy_addr)
        self.max_rank_page = max_rank_page

    def get_random_ids_from_rank_by_page(
        self, page: int, list_type: int
    ) -> typing.Tuple[int, str]:
        """从排行榜某页中获取该页番号列表

        :param int page: 第几页
        :param int list_type: 排行榜类型 0 nice | 1 new
        :return typing.Tuple[int, list]: 状态码和番号列表
        """
        if list_type == 0:
            url = random.choice(JavLibUtil.URLS_NICE)
        elif list_type == 1:
            url = random.choice(JavLibUtil.URLS_NEW)
        code, resp = self.send_req(url=url + str(page))
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
            self.log.error(f"JavLibUtil: 从排行榜某页中获取该页番号列表: {e}")
            return 404, None

    def get_random_id_from_rank(self, list_type: int) -> typing.Tuple[int, str]:
        """从排行榜中随机获取番号

        :param int list_type: 排行榜类型 0 nice | 1 new
        :return typing.Tuple[int, str]: 状态码和番号
        """
        page = random.randint(1, self.max_rank_page)
        code, ids = self.get_random_ids_from_rank_by_page(
            page=page, list_type=list_type
        )
        if code != 200:
            return code, None
        else:
            return 200, random.choice(ids)

    def get_comments_by_id(self, id: str) -> typing.Tuple[int, list]:
        """根据番号获取评论 (最佳评论, 最多 5 条)

        :param str id: 番号
        :return typing.Tuple[int, list]: 状态码和评论列表
        """
        url = JavLibUtil.BASE_URL_SEARCH_AV + id
        code, resp = self.send_req(url=url)
        if code != 200:
            return code, None
        javlib_av_id = ""
        if resp.url == url:
            try:
                soup = self.get_soup(resp)
                videos = soup.find_all(class_="video")
                video_href = videos[0].a["href"]
                javlib_av_id = video_href[video_href.find("v=") + 2 :]
            except Exception as e:
                self.log.error(f"JavLibUtil: 根据番号 {id} 获取评论失败: {e}")
                return 404, None
        else:
            r_url = resp.url
            javlib_av_id = r_url[r_url.find("v=") + 2 :]
        comment_url = JavLibUtil.BASE_URL_REVIEW + javlib_av_id
        code, resp = self.send_req(url=comment_url)
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
            self.log.error(f"JavLibUtil: 根据番号 {id} 获取评论失败: {e}")
            return 404, None


class DmmUtil(BaseUtil):
    BASE_URL = "https://www.dmm.co.jp"
    BASE_URL_SEARCH_AV = BASE_URL + "/search/=/searchstr="
    BASE_URL_SEARCH_STAR = (
        BASE_URL + "/digital/videoa/-/list/search/=/device=tv/sort=ranking/?searchstr="
    )
    BASE_URL_TOP_STARS = BASE_URL + "/digital/videoa/-/ranking/=/type=actress"

    def get_pv_by_id(self, id: str) -> typing.Tuple[int, str]:
        """根据番号从 DMM 获取预览视频地址

        :param str id: 番号
        :return tuple[int, str]: 状态码和预览视频地址
        """
        # 搜索番号
        url = DmmUtil.BASE_URL_SEARCH_AV + id
        headers = {
            "cookie": "age_check_done=1;",
            "user-agent": self.ua_mobile(),  # 手机端页面更方便爬取
        }
        code, resp = self.send_req(url=url, headers=headers)
        if code != 200:
            return code, None
        try:
            soup = self.get_soup(resp)
            res = soup.find(class_="btn")
            return 200, res.a["href"]
        except Exception as e:
            self.log.error(f"DmmUtil: 根据番号 {id} 从 DMM 获取预览视频地址: {e}")
            return 404, None

    def get_nice_avs_by_star_name(self, star_name: str) -> typing.Tuple[int, list]:
        """根据演员名字获取高分番号列表

        :param str star_name: 演员名字
        :return typing.Tuple[int, list]: 状态码和番号列表
        番号列表单个对象结构:
        {
            'rate': rate, # 评分
            'id': id # 番号
        }
        """
        # 搜索演员
        url = DmmUtil.BASE_URL_SEARCH_STAR + star_name
        headers = {
            "cookie": "age_check_done=1;",
            "user-agent": self.ua_desktop(),  # 桌面端页面更方便爬取
        }
        code, resp = self.send_req(url=url, headers=headers)
        if code != 200:
            return code, resp
        try:
            soup = self.get_soup(resp)
            av_list = soup.find(id="list")
            av_tags = av_list.find_all("li")
            avs = []
            cid_pat = re.compile(r"/cid=.+/")
            cid_pat_real = re.compile(r"[A-Za-z]+0+[0-9]+")
            for av in av_tags:
                try:
                    rate = av.find(class_="rate").span.span.text
                    av_href = av.find(class_="sample").a["href"]
                    match = cid_pat.findall(av_href)
                    cid = match[0].replace("/cid=", "").replace("/", "")
                    cid = cid_pat_real.findall(cid)[0]
                    id_num = cid[-3:]
                    id_pre = re.sub("0*$", "", cid[:-3])
                    id = f"{id_pre}-{id_num}"
                    avs.append({"rate": float(rate), "id": id})
                except Exception as e:
                    pass
            if avs == []:
                return 404, None
            avs = list(filter(lambda av: av["rate"] >= 4.0, avs))
            if len(avs) == 0:
                return 404, None
            return 200, avs
        except Exception as e:
            self.log.error(f"DmmUtil: 根据演员名字 {star_name} 获取高分番号列表: {e}")
            return 404, None

    def get_score_by_id(self, id: str) -> typing.Tuple[int, str]:
        """根据番号返回评分

        :param str id: 番号
        :return tuple[int, str]: 状态码和评分
        """
        # 搜索番号
        url = DmmUtil.BASE_URL_SEARCH_AV + id
        headers = {
            "cookie": "age_check_done=1;",
            "user-agent": self.ua_desktop(),  # 桌面端页面更方便爬取
        }
        code, resp = self.send_req(url=url, headers=headers)
        if code != 200:
            return code, resp
        try:
            soup = self.get_soup(resp)
            res = soup.find(class_="rate")
            return 200, res.span.span.text
        except Exception as e:
            self.log.error(f"DmmUtil: 根据番号 {id}返回评分: {e}")
            return 404, None

    def get_nice_pv_by_src(self, src: str) -> str:
        """根据普通 src 获取更清晰的 src

        :param str src
        :return str: nice src
        """
        return src.replace("_sm_", "_dmb_")

    def get_top_stars(self, page=1) -> typing.Tuple[int, list]:
        """根据页数获取明星排行榜某页中的明星列表

        :param int page: 页数, 共 5 页, 每页 20 位, 共 100 位,  defaults to 1
        :return tuple[int, list]: 状态码和明星列表
        """
        url = DmmUtil.BASE_URL_TOP_STARS + f"/page={page}/"
        headers = {
            "cookie": "age_check_done=1;",
            "user-agent": self.ua_desktop(),
        }
        code, resp = self.send_req(url=url, headers=headers)
        if code != 200:
            return code, None
        try:
            soup = self.get_soup(resp)
            res = soup.find_all(class_="data")
            if not res or len(res) == 0:
                return 404, None
            return 200, [obj.p.a.text for obj in res]
        except Exception as e:
            self.log.error(f"DmmUtil: 获取明星排行榜第 {page} 页中的明星列表: {e}")
            return 404, None

    def get_all_top_stars(self) -> typing.Tuple[int, list]:
        """获取 DMM 排行榜前 100 名女优

        :return tuple[int, list]: 状态码和女优名称列表
        """
        with concurrent.futures.ThreadPoolExecutor(max_workers=6) as executor:
            # 爬取第一到第五页数据
            futures = {
                executor.submit(self.get_top_stars, page): page for page in range(1, 6)
            }
            results = {}
            # 等待并获取数据
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
    BASE_URL_SEARCH_BY_STAR_NAME = f"{BASE_URL}/search"
    BASE_URL_SEARCH_BY_STAR_ID = f"{BASE_URL}/star"
    BASE_URL_SEARCH_STAR = f"{BASE_URL}/searchstar"
    BASE_URL_MAGNET = f"{BASE_URL}/ajax/uncledatoolsbyajax.php?lang=zh"
    BASE_URL_GENRE = f"{BASE_URL}/genre"

    def __init__(
        self,
        proxy_addr="",
        max_home_page_count=100,
        max_new_avs_count=8,
    ):
        """初始化

        :param str proxy_addr: 代理服务器地址, 默认为 ''
        :param int max_home_page_count: 主页最大爬取页数, 默认为 100 页
        :param int max_new_avs_count: 获取最新 AV 数量, 默认为 8 部
        """
        super().__init__(proxy_addr)
        self.max_home_page_count = max_home_page_count
        self.max_new_avs_count = max_new_avs_count

    def get_all_genres(self) -> typing.Tuple[int, list]:
        """获取所有类别

        :return typing.Tuple[int, list]: 状态码和类别列表
        """
        code, resp = self.send_req(url=JavBusUtil.BASE_URL_GENRE)
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
            self.log.error(f"JavBusUtil: 获取所有标签失败: {e}")
            return 404, None

    def get_id_by_genre_id(self, genre: str) -> typing.Tuple[int, str]:
        """通过类别编号获取一个番号

        :param str genre: 类别编号
        :return typing.Tuple[int, str]: 状态码和番号
        """
        return self.get_id_from_page(
            base_page_url=f"{JavBusUtil.BASE_URL_GENRE}/{genre}"
        )

    def get_id_by_genre_name(self, genre: str) -> typing.Tuple[int, str]:
        """通过类别编号获取一个番号

        :param str genre: 类别名称
        :return typing.Tuple[int, str]: 状态码和番号
        """
        return self.get_id_from_page(
            base_page_url=f"{JavBusUtil.BASE_URL_GENRE}/{genre}"
        )

    def get_max_page(self, url: str) -> typing.Tuple[int, int]:
        """获取最大页数(只适用于不超过 10 页的页面)

        :param str url: 页面地址
        :return tuple[int, int]: 状态码和最大页数
        """
        code, resp = self.send_req(url)
        if code != 200:
            return code, None
        try:
            soup = self.get_soup(resp)
            tag_pagination = soup.find(class_="pagination pagination-lg")
            # 如果没有分页块则只有第一页
            if not tag_pagination:
                return 200, 1
            tags_li = tag_pagination.find_all("li")
            return 200, int(tags_li[len(tags_li) - 2].a.text)
        except Exception as e:
            self.log.error(f"JavBusUtil: 从 {url} 获取最大页数: {e}")
            return 404, None

    def get_ids_from_page(self, base_page_url: str, page=-1) -> typing.Tuple[int, list]:
        """从 av 列表页面获取该页面全部番号

        :param str base_page: 基础页地址, 也是第一页地址
        :param int page: 用于指定爬取哪一页的数据, 默认值为 -1, 表示随机获取某一页
        :return tuple[int, str]: 状态码和番号列表
        """
        url = ""
        if page != -1:
            url = f"{base_page_url}/{page}"
        else:
            code, max_page = self.get_max_page(base_page_url)
            if code != 200:
                return code, None
            url = f"{base_page_url}/{random.randint(1, max_page)}"
        code, resp = self.send_req(url=url)
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
            self.log.error(f"JavBusUtil: 从 av 列表页面 {base_page_url} 获取该页面全部番号: {e}")
            return 404, None

    def get_id_from_page(self, base_page_url: str, page=-1) -> typing.Tuple[int, str]:
        """从 av 列表页面获取一个番号

        :param str base_page: 基础页地址, 也是第一页地址
        :param int page: 用于指定爬取哪一页的数据, 默认值为 -1, 表示随机获取某一页
        :return tuple[int, str]: 状态码和番号
        """
        code, ids = self.get_ids_from_page(base_page_url, page)
        if code != 200:
            return code, None
        return 200, random.choice(ids)

    def get_id_from_home(self, page=-1) -> typing.Tuple[int, str]:
        """从 javbus 主页获取一个番号

        :param int page: 用于指定爬取哪一页的数据, 默认值为 -1, 表示随机获取某一页
        :return tuple[int, str]: 状态码和番号
        """
        if page == -1:
            page = random.randint(1, self.max_home_page_count)
        return self.get_id_from_page(
            base_page_url=JavBusUtil.BASE_URL + "/page", page=page
        )

    def get_id_by_star_name(self, star_name: str, page=-1) -> typing.Tuple[int, str]:
        """根据演员名称获取一个番号

        :param str star_name: 演员名称
        :param int page: 用于指定爬取哪一页的数据, 默认值为 -1, 表示随机获取某一页
        :return tuple[int, str]: 状态码和番号
        """
        return self.get_id_from_page(
            base_page_url=f"{JavBusUtil.BASE_URL_SEARCH_BY_STAR_NAME}/{star_name}",
            page=page,
        )

    def get_new_ids_by_star_name(self, star_name: str) -> typing.Tuple[int, list]:
        """根据演员名字获取最新番号列表

        :param str star_name: 演员名称
        :return typing.Tuple[int, list]: 状态码和番号列表
        """
        code, ids = self.get_ids_from_page(
            base_page_url=f"{JavBusUtil.BASE_URL_SEARCH_BY_STAR_NAME}/{star_name}",
            page=1,
        )
        if code != 200:
            return code, None
        return 200, ids[: self.max_new_avs_count]

    def get_id_by_star_id(self, star_id: str, page=-1) -> typing.Tuple[int, str]:
        """根据演员编号获取一个番号

        :param str star_id: 演员编号
        :param int page: 用于指定爬取哪一页的数据, 默认值为 -1, 表示随机获取某一页
        :return tuple[int, str]: 状态码和番号
        """
        return self.get_id_from_page(
            base_page_url=f"{JavBusUtil.BASE_URL_SEARCH_BY_STAR_ID}/{star_id}",
            page=page,
        )

    def get_new_ids_by_star_id(self, star_id: str) -> typing.Tuple[int, list]:
        """根据演员编号获取最新番号

        :param str star_id: 演员编号
        :return tuple[int, list]: 状态码和番号列表
        """
        code, ids = self.get_ids_from_page(
            base_page_url=f"{JavBusUtil.BASE_URL_SEARCH_BY_STAR_ID}/{star_id}", page=1
        )
        if code != 200:
            return code, None
        return 200, ids[: self.max_new_avs_count]

    def get_samples_by_id(self, id: str) -> typing.Tuple[int, list]:
        """根据番号获取截图

        :param str id: 番号
        :return tuple[int, list]: 状态码和截图列表
        """
        samples = []
        url = f"{JavBusUtil.BASE_URL}/{id}"
        code, resp = self.send_req(url=url)
        if code != 200:
            return code, None
        try:
            soup = self.get_soup(resp)
            sample_tags = soup.find_all(class_="sample-box")
            for tag in sample_tags:
                sample_link = tag["href"]
                if sample_link.find("https") == -1:
                    sample_link = JavBusUtil.BASE_URL + sample_link
                samples.append(sample_link)
            if samples == []:
                return 404, None
            return 200, samples
        except Exception as e:
            self.log.error(f"JavBusUtil: 根据番号 {id} 获取截图: {e}")
            return 404, None

    def check_star_exists(self, star_name: str) -> typing.Tuple[int, dict]:
        """根据演员名称确认该演员在 javbus 是否存在, 如果存在则返回演员 id 和演员名称

        :param str star_name: 演员名称
        :return tuple[int, dict]: 状态码, 演员 id 和演员名称
        dict 格式:
        {
            "star_id": star_id,
            "star_name": star_name
        }
        """
        code, resp = self.send_req(url=f"{JavBusUtil.BASE_URL_SEARCH_STAR}/{star_name}")
        if code != 200:
            return code, None
        try:
            soup = self.get_soup(resp)
            star = soup.find(class_="avatar-box text-center")
            star_id = star["href"].split("star/")[1]
            res_star_name = star.find("img")["title"]
            return 200, {"star_id": star_id, "star_name": res_star_name}
        except Exception as e:
            self.log.error(f"JavBusUtil: 根据演员名称 {star_name} 确认该演员在 javbus 是否存在: {e}")
            return 404, None

    def get_av_by_id(
        self,
        id: str,
        is_nice: bool,
        is_uncensored: bool,
        magnet_max_count=10,
    ) -> typing.Tuple[int, dict]:
        """通过 javbus 获取番号对应 av

        :param str id: 番号
        :param bool is_nice: 是否过滤出高清, 有字幕磁链
        :param bool is_uncensored: 是否过滤出无码磁链
        :param int magnet_max_count: 过滤后磁链的最大数目, 默认为 10
        :return tuple[int, dict]: 状态码和 av
        av格式:
        {
            'id': '',      # 番号
            'title': '',   # 标题
            'img': '',     # 封面地址
            'date': '',    # 发行日期
            'tags': '',    # 标签
            'stars': [],   # 演员
            'magnets': [], # 磁链
            'url': '',     # 地址
        }
        磁链格式:
        {
            'link': '', # 链接
            'size': '', # 大小
            'hd': '0',  # 是否高清 0 否 | 1 是
            'zm': '0',  # 是否有字幕 0 否 | 1 是
            'uc': '0',  # 是否未经审查 0 否 | 1 是
            'size_no_unit': 浮点值 # 去除单位后的大小值, 用于排序, 当要求过滤磁链时会存在该字段
        }
        演员格式:
        {
            'name': '', # 演员名称
            'id': ''    # 演员编号
        }
        """
        id = id.lower()  # 部分番号要小写才能在 javbus 查找成功
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
        url = f"{JavBusUtil.BASE_URL}/{id}"
        av["url"] = url
        code, resp = self.send_req(url=url)
        if code != 200:
            return code, None
        soup = self.get_soup(resp)
        html = soup.prettify()
        try:
            # 获取封面和标题
            big_image = soup.find(class_="bigImage")
            img = None
            if big_image:
                img = big_image["href"]
                if img.find("http") == -1:
                    av["img"] = JavBusUtil.BASE_URL + img
                    av["title"] = big_image.img["title"]
            paras = soup.find(class_="col-md-3 info").find_all("p")
            for i, p in enumerate(paras):
                # 获取識別碼
                if p.text.find("識別碼:") != -1:
                    av["id"] = "".join(
                        p.text.replace("識別碼:", "").replace('"', "").split()
                    )
                # 获取发行日期
                elif p.text.find("發行日期:") != -1:
                    av["date"] = "".join(
                        p.text.replace("發行日期:", "").replace('"', "").split()
                    )
                # 获取标签
                elif p.text.find("類別:") != -1:
                    tags = paras[i + 1].find_all("a")
                    for tag in tags:
                        av["tags"] += "".join(tag.text.split()) + " "
                    av["tags"] = av["tags"].strip()
                # 获取演员
                elif i == len(paras) - 1:
                    tags = p.find_all("a")
                    for tag in tags:
                        star = {"name": "", "id": ""}
                        star["name"] = "".join(tag.text.split())
                        star["id"] = tag["href"].split("star/")[1]
                        av["stars"].append(star)
        except Exception as e:
            self.log.error(f"JavBusUtil: 通过 javbus 获取番号 {id} 对应 av: {e}")
        # 获取uc
        uc_pattern = re.compile(r"var uc = .+;")
        match = uc_pattern.findall(html)
        uc = None
        if match:
            uc = match[0].replace("var uc = ", "").replace(";", "")
        # 获取gid
        gid_pattern = re.compile(r"var gid = .+;")
        match = gid_pattern.findall(html)
        gid = None
        if match:
            gid = match[0].replace("var gid = ", "").replace(";", "")
        # 如果不存在磁链则直接返回
        if not uc and not gid:
            return 200, av
        # 得到磁链的ajax请求地址
        url = f"{JavBusUtil.BASE_URL_MAGNET}&gid={gid}&uc={uc}"
        headers = {
            "user-agent": self.ua(),
            "referer": f"{JavBusUtil.BASE_URL}/{id}",
        }
        # 发送请求获取含磁链页
        code, resp = self.send_req(url=url, headers=headers)
        # 如果不存在磁链或请求失败则直接返回
        if code != 200:
            return 200, av
        # 解析页面获取磁链
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
                )  # 过滤高清
                magnets = MagnetUtil.get_nice_magnets(
                    magnets, "zm", expect_val="1"
                )  # 过滤有字幕
                magnets = MagnetUtil.sort_magnets(magnets)  # 从大到小排序
                magnets = magnets[0:magnet_max_count]
                av["magnets"] = magnets
        except Exception as e:
            self.log.error(f"JavBusUtil: 通过 javbus 获取番号 {id} 对应 av: {e}")
        return 200, av


class AvgleUtil(BaseUtil):
    BASE_URL = "https://api.avgle.com"

    def get_video_by_id(self, id: str) -> typing.Tuple[int, dict]:
        """根据番号从 avgle 获取视频
        :param str id: 番号
        :return tuple[int, dict]: 状态码, 视频链接
        视频链接：
        {
            'fv': '', # 完整视频链接
            'pv': ''  # 预览视频链接
        }
        """
        page = 0
        limit = 3
        url = f"{AvgleUtil.BASE_URL}/v1/jav/{id}/{page}?limit={limit}"
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

    def get_pv_by_id(self, id: str) -> typing.Tuple[int, str]:
        """根据番号从 avgle 获取预览视频
        :param str id: 番号
        :return tuple[int, str]: 状态码, 预览视频链接
        """
        code, res = self.get_video_by_id(id)
        if code != 200:
            return code, None
        if res["pv"] != "":
            return 200, res["pv"]
        else:
            return 404, None

    def get_fv_by_id(self, id: str) -> typing.Tuple[int, str]:
        """根据番号从 avgle 获取完整视频
        :param str id: 番号
        :return tuple[int, str]: 状态码, 完整视频链接
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
        """过滤磁链列表

        :param list magnets: 要过滤的磁链列表
        :param str prop: 过滤属性
        :param any expect_val: 过滤属性的期望值
        :return list: 过滤后的磁链列表
        """
        # 已经无法再过滤
        if len(magnets) == 0:
            return []
        if len(magnets) == 1:
            return magnets
        magnets_nice = []
        for magnet in magnets:
            if magnet[prop] == expect_val:
                magnets_nice.append(magnet)
        # 如果过滤后已经没了, 返回原来磁链列表
        if len(magnets_nice) == 0:
            return magnets
        return magnets_nice

    @staticmethod
    def sort_magnets(magnets: list) -> list:
        """根据大小排列磁链列表

        :param list magnets: 磁链列表
        :return list: 排列好的磁链列表
        """
        # 统一单位为 MB
        for magnet in magnets:
            magnet["size_no_unit"] = -1
            size = magnet["size"].lower().replace("gib", "gb").replace("mib", "mb")
            gb_idx = size.find("gb")
            mb_idx = size.find("mb")
            if gb_idx != -1:  # 单位为 GB
                magnet["size_no_unit"] = float(size[:gb_idx]) * 1024
            elif mb_idx != -1:  # 单位为 MB
                magnet["size_no_unit"] = float(size[:mb_idx])
        magnets = list(filter(lambda m: m["size_no_unit"] != -1, magnets))
        # 根据 size_no_unit 大小排序
        magnets = sorted(magnets, key=lambda m: m["size_no_unit"], reverse=True)
        return magnets


class SukebeiUtil(BaseUtil):
    BASE_URL = "https://sukebei.nyaa.si"

    def get_av_by_id(
        self,
        id: str,
        is_nice: bool,
        is_uncensored: bool,
        magnet_max_count=10,
    ) -> typing.Tuple[int, dict]:
        """通过 sukebei 获取番号对应 av

        :param str id: 番号
        :param bool is_nice: 是否过滤出高清, 有字幕磁链
        :param bool is_uncensored: 是否过滤出无码磁链
        :param int magnet_max_count: 过滤后磁链的最大数目, 默认为 10
        :return tuple[int, dict]: 状态码和 av
        av格式:
        {
            'id': '',      # 番号
            'title': '',   # 标题
            'img': '',     # 封面地址 | sukebei 不支持
            'date': '',    # 发行日期 | sukebei 不支持
            'tags': '',    # 标签 | sukebei 不支持
            'stars': [],   # 演员 | sukebei 不支持
            'magnets': [], # 磁链
            'url': '',     # 地址
        }
        磁链格式:
        {
            'link': '', # 链接
            'size': '', # 大小
            'hd': '0',  # 是否高清 0 否 | 1 是 | sukebei 不支持
            'zm': '0',  # 是否有字幕 0 否 | 1 是 | sukebei 不支持
            'uc': '0',  # 是否未经审查 0 否 | 1 是
            'size_no_unit': 浮点值 # 去除单位后的大小值, 用于排序, 当要求过滤磁链时会存在该字段
        }
        演员格式: | sukebei 不支持
        {
            'name': '', # 演员名称
            'id': ''    # 演员编号
        }
        """
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
        qid = id.lower()
        if qid.find("fc2") != -1:
            qid = qid.replace("-", " ")
        # 查找av
        url = f"{SukebeiUtil.BASE_URL}?q={qid}"
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
                    "link": "",  # 链接
                    "size": "",  # 大小
                    "hd": "0",  # 是否高清 0 否 | 1 是
                    "zm": "0",  # 是否有字幕 0 否 | 1 是
                    "uc": "0",  # 是否未经审查 0 否 | 1 是
                }
                for j, td in enumerate(tds):
                    if j == 1:  # 获取标题
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
                    if j == 2:  # 获取磁链
                        magnet["link"] = td.find_all("a")[-1]["href"]
                    if j == 3:  # 获取大小
                        magnet["size"] = td.text
                av["magnets"].append(magnet)
            # 过滤番号
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
            self.log.error(f"SukebeiUtil: 通过 sukebei 获取番号 {id} 对应 av: {e}")
            return 404, None
        return 200, av

    def search_av_by_tag(self, tag: str) -> typing.Tuple[int, list]:
        """根据关键字搜索影片

        :param str tag: 关键字
        :return typing.Tuple[int, list]: 状态码和影片列表
        影片列表单位结构:
        {
            "title": "",
            "loc": "", # /view/{num}
        }
        """
        url = f"{SukebeiUtil.BASE_URL}?q={tag}"
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
            self.log.error(f"SukebeiUtil: 根据关键字{tag}搜索影片: {e}")
            return 404, None

    def get_av_by_url(self, url: str) -> typing.Tuple[int, dict]:
        """根据地址获取 av

        :param str url: 地址
        :return typing.Tuple[int, dict]: 状态码和资源
        资源结构:
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
            self.log.error(f"SukebeiUtil: 根据地址 {url} 获取 av: {e}")
            return 404, None


class WikiUtil(BaseUtil):
    logging.getLogger("wikipediaapi").setLevel(logging.ERROR)
    BASE_URL_JAPAN_WIKI = "https://ja.wikipedia.org/wiki"
    BASE_URL_CHINA_WIKI = "https://zh.wikipedia.org/wiki"

    def get_wiki_page_by_lang(self, topic: str, from_lang: str, to_lang: str) -> dict:
        """根据搜索词和原来语言码返回指定语言维基页, 如果搜索不到结果则返回空, 如果搜索到结果但找不到指定语言维基页则返回原页

        :param str topic: 搜索词
        :param str from_lang: 原来语言码
        :param str to_lang: 目标语言码
        :return dict: 结果集
        {
            'title': '', # 标题
            'url': '', # 地址
            'lang': '' # 语言码
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
                f"WikiUtil: 根据搜索词 {topic} 和原来语言码 {from_lang} 返回指定语言 {to_lang} 维基页: {e}"
            )
            return


class TransUtil(BaseUtil):
    def trans(self, text: str, from_lang="auto", to_lang="zh-CN") -> str:
        """翻译

        :param str text: 要翻译的文本
        :param str from_lang: 原文语言码, defaults to 'auto'
        :param str to_lang: 目标语言码, defaults to 'zh-CN'
        :return str: 翻译结果，如果失败则为 None
        """
        try:
            return GoogleTranslator(
                source=from_lang, target=to_lang, proxies=self.proxy_json
            ).translate(text)
        except Exception as e:
            self.log.error(f"TransUtil: 翻译: {e}")
