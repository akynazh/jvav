# Jvav

Useful tools for Jav.

## INSTALL

```
pip install jvav -U
```

## LIB

- DmmUtil
- JavLibUtil
- JavBusUtil
- AvgleUtil
- MagnetUtil
- SukebeiUtil
- WikiUtil
- TransUtil

```py
# A sample for DmmUtil
import jvav

util = jvav.DmmUtil(proxy_addr='http://127.0.0.1:7890')
util.get_nice_avs_by_star_name('小倉由菜')
util.get_score_by_id('cawd-441')
util.get_all_top_stars()
```

## CMD

```
$ jvav -h
usage: cmd.py [-h] [-v] [-av1 AV1] [-av2 AV2] [-nc] [-uc] [-sr SR] [-srn SRN]
              [-tg TG] [-pv1 PV1] [-pv2 PV2] [-tp] [-p PROXY]

optional arguments:
  -h, --help            show this help message and exit
  -v, --version         查看版本号
  -av1 AV1              后接番号，通过 JavBus 搜索该番号
  -av2 AV2              后接番号，通过 Sukebei 搜索该番号
  -nc                   过滤出高清有字幕磁链
  -uc                   过滤出无码磁链
  -sr SR                后接演员名字, 根据演员名字获取高分番号列表
  -srn SRN              后接演员名字, 根据演员名字获取最新番号列表
  -tg TG                后接关键字, 根据关键字搜索番号列表
  -pv1 PV1              后接番号, 通过 DMM 获取番号对应预览视频
  -pv2 PV2              后接番号, 通过 Avgle 获取番号对应预览视频
  -tp                   获取 DMM 女优排行榜前 25 位
  -p PROXY, --proxy PROXY
                        后接代理服务器地址, 默认读取环境变量 http_proxy 的值
```

## TODO

以下是一些待实现的功能, 期待各位贡献代码哦~

- [ ] 将查询成功的结果缓存本地
- [ ] 支持 javdb.com
- [ ] 支持 db.msin.jp