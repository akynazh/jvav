# -*- coding: UTF-8 -*-
from jvav import utils
import unittest

# PROXY_ADDR = ''
PROXY_ADDR = 'http://127.0.0.1:7890'


def assert_code(code: int, res):
    '''确认状态码是否为 200, 如果是则打印结果

    :param int code: 状态码
    :param any res: 结果
    '''
    assert code == 200, f'code={code}'
    print(res)


def assert_res(res):
    assert res != None, f'res=None'
    print(res)


class JavLibUtilTest(unittest.TestCase):
    util = utils.JavLibUtil(proxy_addr=PROXY_ADDR, max_rank_page=20)

    def test_get_random_id_from_rank(self):
        assert_code(*JavLibUtilTest.util.get_random_id_from_rank(1))


class DmmUtilTest(unittest.TestCase):
    util = utils.DmmUtil(proxy_addr=PROXY_ADDR)

    def test_get_pv_by_id(self):
        assert_code(*DmmUtilTest.util.get_pv_by_id('ipx-365'))

    def test_get_nice_avs_by_star_name(self):
        assert_code(*DmmUtilTest.util.get_nice_avs_by_star_name('小倉由菜'))

    def test_get_score_by_id(self):
        assert_code(*DmmUtilTest.util.get_score_by_id('ipx-365'))

    def test_get_nice_pv_by_src(self):
        pass

    def test_get_top_stars(self):
        assert_code(*DmmUtilTest.util.get_top_stars(1))

    def test_get_all_top_stars(self):
        assert_code(*DmmUtilTest.util.get_all_top_stars())


# python -m unittest discover -s tests -k JavBusUtilTest
class JavBusUtilTest(unittest.TestCase):
    util = utils.JavBusUtil(proxy_addr=PROXY_ADDR,
                            max_home_page_count=100,
                            max_new_avs_count=10)

    # python -m unittest discover -s tests -k test_get_max_page
    def test_get_max_page(self):
        assert_code(*JavBusUtilTest.util.get_max_page(
            'https://www.javbus.com/star/okq'))

    def test_get_ids_from_page(self):
        assert_code(*JavBusUtilTest.util.get_ids_from_page(
            base_page_url='https://www.javbus.com/star/okq'))

    def test_get_id_from_page(self):
        assert_code(*JavBusUtilTest.util.get_id_from_page(
            base_page_url='https://www.javbus.com/star/okq'))

    def test_get_id_from_home(self):
        assert_code(*JavBusUtilTest.util.get_id_from_home())

    def test_get_id_by_star_name(self):
        assert_code(*JavBusUtilTest.util.get_id_by_star_name(star_name='三上悠亜'))

    def test_get_new_ids_by_star_name(self):
        assert_code(*JavBusUtilTest.util.get_new_ids_by_star_name(
            star_name='三上悠亜'))

    def test_get_id_by_star_id(self):
        assert_code(*JavBusUtilTest.util.get_id_by_star_id(star_id='okq'))

    def test_get_new_ids_by_star_id(self):
        assert_code(*JavBusUtilTest.util.get_new_ids_by_star_id(star_id='okq'))

    def test_get_samples_by_id(self):
        assert_code(*JavBusUtilTest.util.get_samples_by_id(id='ipx-365'))

    def test_check_star_exists(self):
        assert_code(*JavBusUtilTest.util.check_star_exists(star_name='三上悠亜'))

    def test_get_av_by_id(self):
        assert_code(*JavBusUtilTest.util.get_av_by_id(
            id='ipx-365', is_nice=True, is_uncensored=False))


class AvgleUtilTest(unittest.TestCase):
    util = utils.AvgleUtil(proxy_addr=PROXY_ADDR)

    def test_get_video_by_id(self):
        assert_code(*AvgleUtilTest.util.get_video_by_id('ipx-369'))

    def test_get_pv_by_id(self):
        assert_code(*AvgleUtilTest.util.get_pv_by_id('ipx-369'))

    def test_get_fv_by_id(self):
        assert_code(*AvgleUtilTest.util.get_fv_by_id('ipx-369'))


class MagnetUtilTest(unittest.TestCase):
    util = utils.MagnetUtil()
    magnets = [
        {
            'link': '#',  # 链接
            'size': '1.2GB',  # 大小
            'hd': '1',  # 是否高清 0 否 | 1 是
            'zm': '0',  # 是否有字幕 0 否 | 1 是
            'uc': '1',  # 是否未经审查 0 否 | 1 是
        },
        {
            'link': '#',  # 链接
            'size': '998MB',  # 大小
            'hd': '0',  # 是否高清 0 否 | 1 是
            'zm': '0',  # 是否有字幕 0 否 | 1 是
            'uc': '1',  # 是否未经审查 0 否 | 1 是
        },
        {
            'link': '#',  # 链接
            'size': '3.2GiB',  # 大小
            'hd': '0',  # 是否高清 0 否 | 1 是
            'zm': '0',  # 是否有字幕 0 否 | 1 是
            'uc': '1',  # 是否未经审查 0 否 | 1 是
            'size_no_unit': 1055.324  # 去除单位后的大小值, 用于排序, 当要求过滤磁链时会存在该字段
        },
    ]

    def test_get_nice_magnets(self):
        print(
            MagnetUtilTest.util.get_nice_magnets(
                magnets=MagnetUtilTest.magnets, prop='hd', expect_val='1'))

    def test_sort_magnets(self):
        print(MagnetUtilTest.util.sort_magnets(MagnetUtilTest.magnets))


class SukebeiUtilTest(unittest.TestCase):
    util = utils.SukebeiUtil(proxy_addr=PROXY_ADDR)

    def test_get_av_by_id(self):
        assert_code(*SukebeiUtilTest.util.get_av_by_id(
            'ipx-365', is_nice=True, is_uncensored=False, magnet_max_count=3))


class WikiUtilTest(unittest.TestCase):
    util = utils.WikiUtil(proxy_addr=PROXY_ADDR)

    def test_get_wiki_page_by_lang(self):
        assert_res(
            WikiUtilTest.util.get_wiki_page_by_lang(topic='七沢みあ',
                                                    from_lang='ja',
                                                    to_lang='zh'))


if __name__ == '__main__':
    unittest.main()