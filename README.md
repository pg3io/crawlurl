# crawlurl - Check liste site web

![langage](https://img.shields.io/badge/Langage-Python-green.svg) 
![Apache 2.0 Licence](https://img.shields.io/hexpm/l/plug.svg)

Vérifie qu'une liste de site internet est bien en fonction.
[Docuementation](https://github.com/pg3io/crawlurl/wiki)

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
Ce projet est sous licence [Apache 2.0](https://www.apache.org/licenses/LICENSE-2.0) consulter le fichier [LICENSE](LICENSE) pour plus de détails.


# Informations sur l'auteur
Ce projet a été créé par [PG3](https://pg3.io) en décembre 2018. 
