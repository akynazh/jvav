# Jvav

Useful tools for Jav.

## INSTALL

```
# python >= 3.7.9
pip install jvav -U
```

## LIB

- DmmUtil
- JavDbUtil
- JavLibUtil
- JavBusUtil
- AvgleUtil
- MagnetUtil
- SukebeiUtil
- WikiUtil
- TransUtil
- SgpUtil

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
  -v, --version         View the version number
  -av1 AV1              Followed by a code, search for the code on JavBus
  -av2 AV2              Followed by a code, search for the code on Sukebei
  -nc                   Filter out high-definition torrents with subtitles
  -uc                   Filter out uncensored torrents
  -sr SR                Followed by an actress name, get a list of high-rated codes based on the actress name
  -srn SRN              Followed by an actress name, get a list of the latest codes based on the actress name
  -tg TG                Followed by a keyword, search for codes based on the keyword
  -pv1 PV1              Followed by a code, get the preview video corresponding to the code from DMM
  -pv2 PV2              Followed by a code, get the preview video corresponding to the code from Avgle
  -tp                   Get the top 25 ranking of DMM actresses
  -p PROXY, --proxy PROXY
                        Followed by the proxy server address, by default reads the value of the http_proxy environment variable.
```

## TODO

The following are some functions to be implemented, and I look forward to your contribution~ 

- [ ] cache the successful query results locally
- [x] support javdb.com (Thanks: [@Steven-Fake](https://github.com/Steven-Fake))
- [ ] support db.msin.jp
- [ ] support JavDbUtil in cmd
- [ ] support SgpUtil in cmd
- [ ] support JavDbUtil in cmd