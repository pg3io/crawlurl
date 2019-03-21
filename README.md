# POC - Check liste site web - Python

![langage](https://img.shields.io/badge/Langage-Python-green.svg) 
![version](https://img.shields.io/badge/version-Alpha-red.svg)
[![Twitter](https://img.shields.io/twitter/follow/pg3io.svg?style=social)](https://twitter.com/intent/follow?screen_name=pg3io)

Vérifie qu'une liste de site internet est bien fonction

## Fonction
### Input
Lister vos urls dans un fichier "txt" et un mot à chercher en fin de page (pour vérifier le chargement total de la page)

### output
logging "stdout" format "Json"
```
{"retcode": <CODE>, "url": <URLw>, "status_code": <CODE>, "result": <RES>, "timereq": <TEMPS_DE_REQUETE>, "message": <MESSAGE_RETOUR>}
```
Le "status_code" peut prendre différentes valeurs :
* 0 = Success
* 1 = Warning, temps de réponse trop long
* 2 = Critical, timeout et 404

Exemple
```
{"retcode": 200, "url": "https://www.theverge.com", "status_code": 0, "timereq": 0.023188114166259766, "message": "ok"}
{"retcode": 200, "url": "https://www.impots.gouv.fr/portail/", "status_code": 0, "timereq": 0.012618064880371094, "message": "ok"}
```

### Synthaxe Yaml
```
<URL> <CONTENT_TO_MATCH> <TIME_WARNING||default:0.1> <TIME_CRITICAL||default:0.2>
```

Exemple "list.yml"
```
  - url: https://theverge.com
    search: 
    warning: 1
    critical: 0.15
    tags:
      - tech
```

## Exécution
* La variable d'environnement "DELAY" est optionelle, par défaut elle sera d'une valeur de 30 secondes
* La variable d'environnement "THREAD" est optionelle, par défaut elle sera d'une valeur de 2
```
export DELAY=<DELAI_ENTRE_TESTS>
export THREAD=<NOMBRE_THREAD_MAX>
export LIST=${PWD}/list.yml
python check-url.py
```

### Docker
```
docker build -t monit/crawl:1.0 . --no-cache
docker run -d -v ${PWD}/list.txt:/sources/list.txt -e LIST=/sources/list.txt --name crawl monit/crawl:1.0
```
### Docker Stack (+ logging gelf dans logstash)
Pas besoin de builder l'image, elle est disponible sur notre registry
```
VERSION=0.8.1 docker stack deploy <NOM_STACK> -c docker-compose.yml
```

## Fonctionnalitées futures
- [x] Code fonctionnel (mais pas très optimisé ...)
- [x] Creation d'une variable "return" (on sait plus ce qu'elle fait)
- [x] Source url/mot file txt
- [x] Variabiliser la tempo entre chaque lot de test
- [x] Multithread des requêtes
- [x] Variabiliser le nombre de Thread
- [x] Support du format yaml pour le fichier source
- [ ] Source url/mot db (mariadb)
- [ ] Ajout d'informations dans le log json (taille de la page ...)

# License

![Apache 2.0 Licence](https://img.shields.io/hexpm/l/plug.svg)

This project is licensed under the [Apache 2.0](https://www.apache.org/licenses/LICENSE-2.0) license - see the [LICENSE](LICENSE) file for details.

# Author Information
This role was created in 21/12/2018 by [PG3](https://pg3.io)
