# crawlurl - Check liste site web

![langage](https://img.shields.io/badge/Langage-Python-green.svg) 
![Apache 2.0 Licence](https://img.shields.io/hexpm/l/plug.svg)

Vérifie qu'une liste de site internet est bien en fonction.
Transmet des informations sur la réponse de ces sites à une base de données.
Affiche les indices de bon fonctionnement de ces sites sur Grafana.

[Documentation](https://github.com/pg3io/crawlurl/wiki)

## Exécution

Le script peut etre utilisé pour logger les indices ou les transmettre à InfluxDB qui affiche ces indices dans Grafana.

* La variable d'environnement LIST est obligatoire, elle doit pointer sur le fichier yaml de configuration
* Toutes les autres variables d'environnement concernent la base de données et sont donc optionnelles.
* Si la variable d'environnement INFLUXDB-HOST est définie et n'est pas vide, crawlurl fonctionnera avec Grafana

### sans InfluxDB (indices loggés dans le terminal)
```
export LIST=${PWD}/list.yml
python check-url.py
```
### avec InfluxDB
```
export "LIST=${PWD}/list.yml"
export "INFLUXDB-HOST=http://localhost:8086"
export "INFLUXDB-BUCKET=bucket"
export "INFLUXDB-TOKEN=token"
export "INFLUXDB-ORG=org"
python check-url.py
```

### Docker
```
docker-compose build --no-cache && docker-compose up -d
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
Ce projet a été maintenu par [PG3](https://pg3.io) en juillet 2021.
