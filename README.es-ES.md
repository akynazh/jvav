

# Jvav

[NSFW] Herramientas útiles para recopilar recursos de aprendizaje para adultos. Soporta operaciones como librería de Python y uso desde línea de comandos, con opciones adicionales de proxy y soporte de caché.

## INSTALACIÓN

```
# python >= 3.9
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
- RankUtil

```py
# Un ejemplo para DmmUtil
import jvav

util = jvav.DmmUtil()
util.get_nice_avs_by_star_name('小倉由菜')
util.get_score_by_id('cawd-441')
util.get_all_top_stars()
```

## CMD

```shell
usage: cmd.py [-h] [-v] [-av1 AV1] [-av2 AV2] [-av3 AV3] [-auth AUTH] [-nc] [-uc] [-sr SR] [-srn SRN] [-tg TG] [-pv1 PV1] [-pv2 PV2] [-rk1] [-rk2] [-p PROXY]

opciones:
  -h, --help            muestra este mensaje de ayuda y sale
  -v, --version         Verifica la versión
  -av1 AV1              Seguido por un código, busca este código en JavBus
  -av2 AV2              Seguido por un código, busca este código en Sukebei
  -av3 AV3              Seguido por un código, busca este código en JavDb
  -auth AUTH            Seguido por un código de autenticación para JavBus, úsalo si falló la búsqueda en JavBus, obtén el código de la clave de la cookie: bus_auth
  -nc                   Filtra enlaces magnet con subtítulos en alta definición
  -uc                   Filtra enlaces magnet sin codificar
  -sr SR                Seguido por el nombre de una actriz, obtén una lista de códigos con alta valoración según el nombre de la actriz
  -srn SRN              Seguido por el nombre de una actriz, obtén una lista de los códigos más recientes según el nombre de la actriz
  -tg TG                Seguido por una palabra clave, busca códigos basados en dicha palabra clave
  -pv1 PV1              Seguido por un código, obtén el video de vista previa correspondiente en DMM
  -pv2 PV2              Seguido por un código, obtén el video de vista previa correspondiente en Avgle
  -rk1                  Obtén el ranking de las top 25 actrices de DMM
  -rk2                  Obtén el ranking de los top 25 AVs
  -p PROXY, --proxy PROXY
                        Seguido por una dirección de servidor proxy (por defecto lee el valor de la variable de entorno http_proxy)
```

## DEV

Utilizo python-3.9.13 para el desarrollo, por favor usa python <= 3.9. 

Y se recomienda usar un entorno virtual de Python para evitar algunos problemas innecesarios.

Estos son mis pasos de desarrollo:

```shell
git clone https://github.com/akynazh/jvav.git
cd jvav
~/.pyenv/versions/3.9.13/bin/python -m venv .venv
source ./.venv/bin/activate
pip3 install -r requirements.txt
```

¡Y luego puedes disfrutar programando! Recuerda escribir o ejecutar los casos de prueba en `tests/test.py`.
Por favor, asegúrate de que las pruebas estén bien antes de enviar tu código~

## TODO

A continuación se encuentran algunas funciones por implementar, y espero su contribución~ 

- [ ] support db.msin.jp
- [x] support RankUtil in CMD (Thanks: [@akynazh](https://github.com/akynazh))
- [x] cache the successful query results locally (Thanks: [@akynazh](https://github.com/akynazh))
- [x] support javdb.com (Thanks: [@Steven-Fake](https://github.com/Steven-Fake))
- [x] support JavDbUtil in cmd (Thanks: [@akynazh](https://github.com/akynazh))

## AGRADECIMIENTOS

<a href="https://www.jetbrains.com/">
<img src="https://resources.jetbrains.com/storage/products/company/brand/logos/jb_beam.png" alt="JetBrains Logo (Main) logo." style="width: 200px;"></a>

¡Gracias a JetBrains por su apoyo a este proyecto!
