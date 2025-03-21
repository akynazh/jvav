# -*- coding: UTF-8 -*-
import jvav
import unittest

PROXY_ADDR = ""


def assert_code(code: int, res):
    """确认状态码是否为 200, 如果是则打印结果

    :param int code: 状态码
    :param any res: 结果
    """
    assert code == 200, f"code={code}"
    print(res)


def assert_res(res):
    assert res != None, f"res=None"
    print(res)


class RankUtilTest(unittest.TestCase):
    util = jvav.RankUtil(proxy_addr=PROXY_ADDR, use_cache=True)

    def test_random_get_av_from_rank(self):
        assert_code(*RankUtilTest.util.random_get_av_from_rank())

    def test_get_av_250_rank(self):
        assert_code(*RankUtilTest.util.get_av_250_rank())


class BaseUtilTest(unittest.TestCase):
    util = jvav.BaseUtil(proxy_addr=PROXY_ADDR, use_cache=False)

    def test_1(self):
        headers = {
            "authority": "api.cbbee0.com",
            "accept": "application/json, text/plain, */*",
            "accept-language": "zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6,zh-TW;q=0.5",
            "content-type": "application/json;charset=UTF-8",
            "origin": "http://www.fpie2.com",
            "referer": "http://www.fpie2.com/",
            "sec-ch-ua": '"Not.A/Brand";v="8", "Chromium";v="114", "Microsoft Edge";v="114"',
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": '"macOS"',
            "sec-fetch-dest": "empty",
            "sec-fetch-mode": "cors",
            "sec-fetch-site": "cross-site",
            "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36 Edg/114.0.1823.82",
        }
        data = {
            "conditions": "ipx-828",
            "field": 0,
            "target": 1,
            "sort": 1,
            "userToken": "",
            "hm": "008-api",
            "device_id": "",
        }
        assert_code(
            *BaseUtilTest.util.send_req(
                url="https://api.cbbee0.com/v1_2/articleSearch",
                m=1,
                headers=headers,
                data=data,
            )
        )

    def test_2(self):
        print(BaseUtilTest.util.ua_mobile())


class JavDbUtilTest(unittest.TestCase):
    util = jvav.JavDbUtil(proxy_addr=PROXY_ADDR, use_cache=False)

    def test_fuzzy_search_stars(self):
        assert_code(*JavDbUtilTest.util.fuzzy_search_stars("柠檬"))

    def test_get_new_ids(self):
        assert_code(*JavDbUtilTest.util.get_new_ids())

    def test_get_nice_avs_by_star_name(self):
        assert_code(
            *JavDbUtilTest.util.get_nice_avs_by_star_name(
                "西元めいさ",
                cookie="_jdb_session=us8u%2BKc%2F8kraWTG6T5jKrHIkPOmQn3fs2xeSfCoRMqRT7JbCzOBDVG%2FAaYaj5SGVcxe8Dvbu1nXi7NJaw8ssVHBbMstublR1jc2qFt494rs5%2BsGeYiod6oiaF2zc5%2FRPlzXZv3iBX%2B471W7hFB%2BnR0Ix8bVFezmpNZ7FyrX0AclEn7LTM%2FzXm70CBveFkOnUMG9RcMorGV0SRDB6E0Cn8RrFit7E7uFMjWzua4DAIaoFP85Cj42y23zQ0t74KLltuz9%2BOYffVphnBE7LKTPFFH93RBowITxUyDwULz9XWOe%2Bvg2Hh3UN%2BwM8QkVmORKHb5l6mTu7pglc3WtLeB0wxrGQ0e0qFIy7RIzNq15kSZjOPWI65UpPy8I%2BL5u7Gt8yqGA%3D--i3%2Bm3PvAsjdJZbsT--Qt5tsiW5xsjOvpCkDb8ILw%3D%3D",
            )
        )

    def test_get_max_page(self):
        assert_code(*JavDbUtilTest.util.get_max_page("https://javdb.com/actors/EvkJ"))

    def test_get_star_page_by_star_name(self):
        assert_code(*JavDbUtilTest.util.get_star_page_by_star_name("河北彩花"))

    def test_get_id_by_star_name(self):
        assert_code(*JavDbUtilTest.util.get_id_by_star_name("河北彩花"))

    def test_get_ids_by_star_name(self):
        assert_code(*JavDbUtilTest.util.get_ids_by_star_name("河北彩花", page=2))

    def test_get_new_ids_by_star_name(self):
        assert_code(*JavDbUtilTest.util.get_new_ids_by_star_name("河北彩花"))

    def test_get_javdb_id_by_id(self):
        assert_code(*JavDbUtilTest.util.get_javdb_id_by_id("IPX-580"))

    def test_get_ids_from_page(self):
        assert_code(
            *JavDbUtilTest.util.get_ids_from_page("https://javdb.com/search?q=中出")
        )

    def test_get_javdb_ids_from_page(self):
        assert_code(
            *JavDbUtilTest.util.get_javdb_ids_from_page(
                "https://javdb.com/search?q=中出"
            )
        )

    def test_get_id_from_home(self):
        assert_code(*JavDbUtilTest.util.get_id_from_home())

    def test_get_javdb_id_from_home(self):
        assert_code(*JavDbUtilTest.util.get_javdb_id_from_home())

    def test_get_ids_from_home(self):
        assert_code(*JavDbUtilTest.util.get_ids_from_home())

    def test_get_javdb_ids_from_home(self):
        assert_code(*JavDbUtilTest.util.get_javdb_ids_from_home())

    def test_get_ids_by_tag(self):
        assert_code(*JavDbUtilTest.util.get_ids_by_tag("出轨"))

    def test_get_javdb_ids_by_tag(self):
        assert_code(*JavDbUtilTest.util.get_javdb_ids_by_tag("数位马赛克"))

    def test_get_cover_by_id(self):
        assert_code(*JavDbUtilTest.util.get_cover_by_id("IPX-580"))

    def test_get_cover_by_javdb_id(self):
        assert_code(*JavDbUtilTest.util.get_cover_by_javdb_id("68YVQ"))

    def test_get_pv_by_id(self):
        assert_code(*JavDbUtilTest.util.get_pv_by_id("IPZZ-154"))

    def test_get_samples_by_id(self):
        assert_code(*JavDbUtilTest.util.get_samples_by_id("SSIS-586"))

    def test_get_av_by_id(self):
        assert_code(*JavDbUtilTest.util.get_av_by_id("IPX-580", False, False, True))

    def test_get_av_by_javdb_id(self):
        assert_code(*JavDbUtilTest.util.get_av_by_javdb_id("68YVQ", True, False, False))


class JavLibUtilTest(unittest.TestCase):
    util = jvav.JavLibUtil(proxy_addr=PROXY_ADDR, use_cache=False)

    def test_get_random_id_from_rank(self):
        assert_code(*JavLibUtilTest.util.get_random_id_from_rank(1))

    def test_get_random_ids_from_rank_by_page(self):
        assert_code(*JavLibUtilTest.util.get_random_ids_from_rank_by_page(2, 0))

    def test_get_comments_by_id(self):
        assert_code(*JavLibUtilTest.util.get_comments_by_id(id="ipx-985"))


class DmmUtilTest(unittest.TestCase):
    util = jvav.DmmUtil(proxy_addr=PROXY_ADDR, use_cache=False)

    def test_get_cids_by_tag(self):
        assert_code(*DmmUtilTest.util.get_cids_by_tag("ssis"))

    def test_get_cids_by_tag_monthly(self):
        assert_code(*DmmUtilTest.util.get_cids_by_tag_monthly("arm"))

    def test_get_cids_by_link(self):
        assert_code(
            *DmmUtilTest.util.get_cids_by_link(
                "https://www.dmm.co.jp/digital/videoa/-/list/=/article=series/id=217566/?dmmref=h%5Cu005f1209exfe00050&i3_ref=detail&i3_ord=1&i3_pst=info_series"
            )
        )

    def test_get_cids_by_link_monthly(self):
        assert_code(
            *DmmUtilTest.util.get_cids_by_link_monthly(
                "https://www.dmm.co.jp/monthly/dream/-/list/search/=/limit=120/n1=DgRJTglEBQ4GwOSdlJOP/sort=ranking/?searchstr=arm"
            )
        )

    def test_get_pv_by_id(self):
        assert_code(*DmmUtilTest.util.get_pv_by_id("ipx-365"))

    def test_get_nice_avs_by_star_name(self):
        assert_code(*DmmUtilTest.util.get_nice_avs_by_star_name("浅野こころ"))

    def test_get_score_by_id(self):
        assert_code(*DmmUtilTest.util.get_score_by_id("ipx-365"))

    def test_get_nice_pv_by_src(self):
        pass

    def test_get_top_stars(self):
        assert_code(*DmmUtilTest.util.get_top_stars(1))

    def test_get_all_top_stars(self):
        assert_code(*DmmUtilTest.util.get_all_top_stars())


class JavBusUtilTest(unittest.TestCase):
    util = jvav.JavBusUtil(
        bus_auth="ba50WJ3DouyEDdVF5L%2BBAHavxC6NH%2BiZXV7f04MisHvkwny3RIejXRqC4%2BCAw79ZbsM",
        proxy_addr=PROXY_ADDR,
        max_home_page_count=100,
        max_new_avs_count=10,
        use_cache=False,
    )

    def test_get_all_genres(self):
        assert_code(*JavBusUtilTest.util.get_all_genres())

    def test_get_id_by_genre_id(self):
        assert_code(*JavBusUtilTest.util.get_id_by_genre_id("3s"))

    def test_get_max_page(self):
        assert_code(
            *JavBusUtilTest.util.get_max_page("https://www.javbus.com/star/okq")
        )

    def test_get_ids_from_page(self):
        assert_code(
            *JavBusUtilTest.util.get_ids_from_page(
                base_page_url="https://www.javbus.com/star/okq"
            )
        )

    def test_fuzzy_search_stars(self):
        assert_code(*JavBusUtilTest.util.fuzzy_search_stars("未久"))

    def test_get_id_from_page(self):
        assert_code(
            *JavBusUtilTest.util.get_id_from_page(
                base_page_url="https://www.javbus.com/star/okq"
            )
        )

    def test_get_id_from_home(self):
        assert_code(*JavBusUtilTest.util.get_id_from_home())

    def test_get_id_by_star_name(self):
        assert_code(*JavBusUtilTest.util.get_id_by_star_name(star_name="三上悠亜"))

    def test_get_ids_by_star_name(self):
        assert_code(*JavBusUtilTest.util.get_ids_by_star_name(star_name="三上悠亜"))

    def test_get_new_ids_by_star_name(self):
        assert_code(*JavBusUtilTest.util.get_new_ids_by_star_name(star_name="三上悠亜"))

    def test_get_id_by_star_id(self):
        assert_code(*JavBusUtilTest.util.get_id_by_star_id(star_id="okq"))

    def test_get_new_ids_by_star_id(self):
        assert_code(*JavBusUtilTest.util.get_new_ids_by_star_id(star_id="okq"))

    def test_get_samples_by_id(self):
        assert_code(*JavBusUtilTest.util.get_samples_by_id(id="ipx-365"))

    def test_check_star_exists(self):
        assert_code(*JavBusUtilTest.util.check_star_exists(star_name="三上"))

    def test_get_av_by_id(self):
        assert_code(
            *JavBusUtilTest.util.get_av_by_id(
                id="juq-589", is_nice=True, is_uncensored=False
            )
        )


class AvgleUtilTest(unittest.TestCase):
    util = jvav.AvgleUtil(proxy_addr=PROXY_ADDR, use_cache=False)

    def test_get_video_by_id(self):
        assert_code(*AvgleUtilTest.util.get_video_by_id("ipx-369"))

    def test_get_pv_by_id(self):
        assert_code(*AvgleUtilTest.util.get_pv_by_id("ipx-369"))

    def test_get_fv_by_id(self):
        assert_code(*AvgleUtilTest.util.get_fv_by_id("ipx-369"))


class MagnetUtilTest(unittest.TestCase):
    util = jvav.MagnetUtil()
    magnets = [
        {
            "link": "#",  # 链接
            "size": "1.2GB",  # 大小
            "hd": "1",  # 是否高清 0 否 | 1 是
            "zm": "0",  # 是否有字幕 0 否 | 1 是
            "uc": "1",  # 是否未经审查 0 否 | 1 是
        },
        {
            "link": "#",  # 链接
            "size": "998MB",  # 大小
            "hd": "0",  # 是否高清 0 否 | 1 是
            "zm": "0",  # 是否有字幕 0 否 | 1 是
            "uc": "1",  # 是否未经审查 0 否 | 1 是
        },
        {
            "link": "#",  # 链接
            "size": "3.2GiB",  # 大小
            "hd": "0",  # 是否高清 0 否 | 1 是
            "zm": "0",  # 是否有字幕 0 否 | 1 是
            "uc": "1",  # 是否未经审查 0 否 | 1 是
            "size_no_unit": 1055.324,  # 去除单位后的大小值, 用于排序, 当要求过滤磁链时会存在该字段
        },
    ]

    def test_get_nice_magnets(self):
        print(
            MagnetUtilTest.util.get_nice_magnets(
                magnets=MagnetUtilTest.magnets, prop="hd", expect_val="1"
            )
        )

    def test_sort_magnets(self):
        print(MagnetUtilTest.util.sort_magnets(MagnetUtilTest.magnets))


class SukebeiUtilTest(unittest.TestCase):
    util = jvav.SukebeiUtil(proxy_addr=PROXY_ADDR, use_cache=False)

    def test_get_av_by_id(self):
        assert_code(
            *SukebeiUtilTest.util.get_av_by_id(
                "fc2-3237415", is_nice=True, is_uncensored=False, magnet_max_count=3
            )
        )

    def test_search_av_by_tag(self):
        assert_code(*SukebeiUtilTest.util.search_av_by_tag("出轨"))

    def test_get_av_by_url(self):
        assert_code(
            *SukebeiUtilTest.util.get_av_by_url("https://sukebei.nyaa.si/view/3873249")
        )


class WikiUtilTest(unittest.TestCase):
    util = jvav.WikiUtil(proxy_addr=PROXY_ADDR, use_cache=False)

    def test_get_wiki_page_by_lang(self):
        assert_res(
            WikiUtilTest.util.get_wiki_page_by_lang(
                topic="七沢みあ", from_lang="ja", to_lang="zh"
            )
        )


class TransUtilTest(unittest.TestCase):
    util = jvav.TransUtil(proxy_addr=PROXY_ADDR, use_cache=False)

    def test_trans(self):
        assert_res(
            TransUtilTest.util.trans(
                text="催淫洗脳されたスレンダー美乳妻は嫌がりながらも淫乱ビッチになっていた 美谷朱里",
                from_lang="ja",
                to_lang="zh-CN",
            )
        )


# python3 -m unittest tests.test.RankUtilTest
# python3 -m unittest tests.test.RankUtilTest.test_random_get_av_from_rank
if __name__ == "__main__":
    unittest.main()
