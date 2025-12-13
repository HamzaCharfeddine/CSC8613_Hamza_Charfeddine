# TP3 - Introduction à Feast et au Feature Store pour StreamFlow

## Contexte

- Dans ce TP, on dispose déjà des données du TP2 càd des snapshots mensuels pour deux périodes, contenant les tables utilisateurs, usage agrégé, abonnements, paiements agrégés etc.

- L’objectif du TP3 est de connecter ces données au Feature Store Feast pour permettre la récupération de features en mode offline (pour l’entraînement) et online (pour l’inférence).

## Mise en place de Feast

> *docker compose up -d --build*

![Screenshot](/screenshots/TP3Q1a.jpg)

![Screenshot](/screenshots/TP3Q1b.jpg)

Le conteneur feast contient tout le Feature Store de StreamFlow.

Il charge le repository situé dans /repo, où sont définis les Entities, DataSources et FeatureViews.

Je l’utilise pour appliquer la configuration du Feature Store et matérialiser les features en exécutant les commandes:

- *docker compose exec feast feast apply*

- *docker compose exec feast feast materialize*

## Définition du Feature Store

Une Entity dans Feast représente l’unité métier pour laquelle les features seront calculées. Ici, l’entité est le user.

C’est un bon choix car toutes les tables de snapshots comportent cette colonne et suivent les utilisateurs dans le temps.


- Nom d’une table de snapshot: *usage_agg_30d_snapshots*

- Exemples de features: *watch_hours_30d, avg_session_mins_7d, unique_devices_30d, skips_7d*


> *docker compose exec feast feast apply*

![Screenshot](/screenshots/TP3Q3a.jpg)

![Screenshot](/screenshots/TP3Q3b.jpg)

- *feast apply* lit la définition du Feature Store, valide les FeatureViews et les sources, puis met à jour le registre interne (registry.db qui est apparu). Ce registre stocke la structure du feature store : noms des features, tables sources, schémas et métadonnées.

## Récupération offline & online

> *docker compose exec prefect python build_training_dataset.py*

![Screenshot](/screenshots/TP3Q4a.jpg)

> *Get-Content data/processed/training_df.csv -TotalCount 5*

![Screenshot](/screenshots/TP3Q4b.jpg)


Feast garantit la temporal correctness car :

- La colonne timestamp_field = "as_of" dans chaque datasource indique précisément la date à laquelle les features sont valides.

- L’entity_df contient (user_id, event_timestamp) => Feast ne retourne que les features dont le timestamp est <= event_timestamp. Impossible d’utiliser des données futures, donc pas de data leakage.

> *docker compose exec feast python /repo/debug_online_features.py*

> Online features for user: 7590-VHVEG

> {'user_id': ['7590-VHVEG'], 'monthly_fee': [29.850000381469727], 'paperless_billing': [True], 'months_active': [1]}

- Si on interroge un user_id qui n’a pas de features matérialisées, Feast retourne None pour chaque feature, car aucune ligne correspondante n’a été chargée dans le Online Store.

![Screenshot](/screenshots/TP3Q4c.jpg)

![Screenshot](/screenshots/TP3Q4d.jpg)

> *docker compose up -d --build*

![Screenshot](/screenshots/TP3Q4e.jpg)

> *curl http://localhost:8000/health*

```StatusCode        : 200
StatusDescription : OK
Content           : {"status":"ok"}
RawContent        : HTTP/1.1 200 OK
                    Content-Length: 15
                    Content-Type: application/json
                    Date: Fri, 12 Dec 2025 23:54:15 GMT
                    Server: uvicorn

                    {"status":"ok"}
Forms             : {}
Headers           : {[Content-Length, 15], [Content-Type, application/json], [Date, Fri, 12 Dec 2025 23:54:15 GMT], [Server, uvicorn]}
Images            : {}
InputFields       : {}
Links             : {}
ParsedHtml        : mshtml.HTMLDocumentClass
RawContentLength  : 15
```
> *curl http://localhost:8000/features/7590-VHVEG*

```
StatusCode        : 200
StatusDescription : OK
Content           : {"user_id":"7590-VHVEG","features":{"user_id":"7590-VHVEG","months_active":1,"paperless_billing":true,"monthly_fee":29.850000381469727}}
RawContent        : HTTP/1.1 200 OK
                    Content-Length: 136
                    Content-Type: application/json
                    Date: Fri, 12 Dec 2025 23:53:41 GMT
                    Server: uvicorn

                    {"user_id":"7590-VHVEG","features":{"user_id":"7590-VHVEG","months_active"...
Forms             : {}
Headers           : {[Content-Length, 136], [Content-Type, application/json], [Date, Fri, 12 Dec 2025 23:53:41 GMT], [Server, uvicorn]}
Images            : {}
InputFields       : {}
Links             : {}
ParsedHtml        : mshtml.HTMLDocumentClass
RawContentLength  : 136
```



## Réflexion

- L’endpoint */features/{user_id}* permet de récupérer en temps réel les mêmes features que celles utilisées pour entraîner le modèle. Feast garantit la cohérence temporelle grâce au champ timestamp_field et à la structure de entity_df, réduisant les risques de training-serving skew. 

- Si un user_id n’a pas de features matérialisées, Feast renverra None ou un dictionnaire vide pour ces features.