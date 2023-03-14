# -*- coding: UTF-8 -*-
import os
import utils
import argparse


class ArgsParser:

    def __init__(self):
        parser = argparse.ArgumentParser()
        # 搜索番号
        parser.add_argument('-av1',
                            type=str,
                            default='',
                            help='后接番号，通过 JavBus 搜索该番号')
        parser.add_argument('-av2',
                            type=str,
                            default='',
                            help='后接番号，通过 Sukebei 搜索该番号')
        parser.add_argument('-nc', action='store_true', help='过滤出高清有字幕磁链')
        parser.add_argument('-uc', action='store_true', help='过滤出无码磁链')
        # 搜索演员
        parser.add_argument('-sr',
                            type=str,
                            default='',
                            help='后接演员名字, 根据演员名字获取高分番号列表')
        parser.add_argument('-srn',
                            type=str,
                            default='',
                            help='后接演员名字, 根据演员名字获取最新番号列表')
        # 获取预览视频
        parser.add_argument('-pv1',
                            type=str,
                            default='',
                            help='后接番号, 通过 DMM 获取番号对应预览视频')
        parser.add_argument('-pv2',
                            type=str,
                            default='',
                            help='后接番号, 通过 Avgle 获取番号对应预览视频')
        # 获取排行榜
        parser.add_argument('-tp',
                            action='store_true',
                            help='获取 DMM 女优排行榜前 25 位')
        # 配置代理
        parser.add_argument('-p',
                            '--proxy',
                            type=str,
                            default='',
                            help='后接代理服务器地址, 默认读取环境变量 http_proxy 的值')
        self.parser = parser
        self.args = None

    def handle_code(self, code: int, res):
        '''处理结果

        :param int code: 状态码
        :param any res: 结果
        '''
        if code != 200:
            print('操作失败, 请重试')
            return
        print(res)

    def parse(self):
        '''解析命令行参数
        '''
        parser = self.parser
        self.args = parser.parse_args()

    def exec(self):
        '''根据参数表自行相应操作
        '''
        if not self.args:
            self.parser.print_help()
            return
        args = self.args
        env_proxy = os.getenv('http_proxy')
        if args.proxy == '' and env_proxy:
            args.proxy = env_proxy
        if args.av1 != '':
            self.handle_code(*utils.JavBusUtil(
                proxy_addr=args.proxy).get_av_by_id(
                    id=args.av1, is_nice=args.nc, is_uncensored=args.uc))
        elif args.av2 != '':
            self.handle_code(*utils.SukebeiUtil(
                proxy_addr=args.proxy).get_av_by_id(
                    id=args.av2, is_nice=args.nc, is_uncensored=args.uc))
        elif args.tp:
            self.handle_code(*utils.DmmUtil(
                proxy_addr=args.proxy).get_top_stars(1))
        elif args.sr != '':
            self.handle_code(*utils.DmmUtil(
                proxy_addr=args.proxy).get_nice_avs_by_star_name(args.sr))
        elif args.srn != '':
            self.handle_code(*utils.JavBusUtil(
                proxy_addr=args.proxy).get_new_ids_by_star_name(args.srn))
        elif args.pv1 != '':
            self.handle_code(*utils.DmmUtil(
                proxy_addr=args.proxy).get_pv_by_id(args.pv1))
        elif args.pv2 != '':
            self.handle_code(*utils.AvgleUtil(
                proxy_addr=args.proxy).get_pv_by_id(args.pv2))
        else:
            self.parser.print_help()


if __name__ == '__main__':
    parser = ArgsParser()
    parser.parse()
    parser.exec()