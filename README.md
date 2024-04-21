# Jvav

Useful tools for Jav. Supports Python library operations and command-line usage, with additional proxy options and cache support.

## INSTALL

```
# python >= 3.7
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
- RankUtil

```py
# A sample for DmmUtil
import jvav

util = jvav.DmmUtil()
util.get_nice_avs_by_star_name('小倉由菜')
util.get_score_by_id('cawd-441')
util.get_all_top_stars()
```

## CMD

```shell
usage: cmd.py [-h] [-v] [-av1 AV1] [-av2 AV2] [-av3 AV3] [-sg SG] [-auth AUTH]
              [-nc] [-uc] [-sr SR] [-srn SRN] [-tg TG] [-pv1 PV1] [-pv2 PV2]
              [-tp] [-p PROXY]

optional arguments:
  -h, --help            show this help message and exit
  -v, --version         Check version
  -av1 AV1              Followed by a code, search this code on JavBus
  -av2 AV2              Followed by a code, search this code on Sukebei
  -av3 AV3              Followed by a code, search this code on JavDb
  -sg SG                Followed by a code, search the explainer video of this
                        code
  -auth AUTH            Followed by a authentication code for JavBus, get it
                        from cookie key: bus_auth
  -nc                   Filter out high-definition subtitles magnet links
  -uc                   Filter out uncoded magnet links
  -sr SR                Followed by an actress name, get a list of high-rated
                        codes based on the actress name
  -srn SRN              Followed by an actress name, get a list of the most
                        recent codes based on the actress name
  -tg TG                Followed by a keyword, search for codes based on the
                        keyword
  -pv1 PV1              Followed by a code, get the corresponding preview
                        video of the code on DMM
  -pv2 PV2              Follow a code, get the corresponding preview video of
                        the code on Avgle
  -tp                   Get the top 25 ranking of DMM actresses
  -p PROXY, --proxy PROXY
                        Followed by a proxy server address (by default reads
                        the value of the environment variable http_proxy)
```

## DEV

I use python-3.7.12 for development, please use python <= 3.7. 

And it is recommended to use python virtual environment to avoid some unnecessary problems.

Here is my developing steps:

```shell
git clone https://github.com/akynazh/jvav.git
cd jvav
~/.pyenv/versions/3.7.12/bin/python -m venv .venv
source ./.venv/bin/activate
pip3 install -r requirements.txt
```

And then you can enjoy coding! Remember to write or run test cases in `tests/test.py`.
Please make sure the test is okay before submitting your code~

## TODO

The following are some functions to be implemented, and I look forward to your contribution~ 

- [ ] fix SgpUtil(currently not work)
- [ ] support RankUtil in CMD
- [ ] fix JavLibUtil(currently not work because of cloudflare)
- [x] cache the successful query results locally (Thanks: [@akynazh](https://github.com/akynazh))
- [x] support javdb.com (Thanks: [@Steven-Fake](https://github.com/Steven-Fake))
- [ ] support db.msin.jp
- [x] support JavDbUtil in cmd (Thanks: [@akynazh](https://github.com/akynazh))

## Thanks

<a href="https://www.jetbrains.com/">
<img src="https://resources.jetbrains.com/storage/products/company/brand/logos/jb_beam.png" alt="JetBrains Logo (Main) logo." style="width: 200px;"></a>

Thanks to JetBrains for their support to this project!