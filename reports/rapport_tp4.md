# TP4 - Entraînement end-to-end : MLflow Registry → API de prédiction

## Mise en route

> *docker compose down*

> *docker compose up -d --build*

![Screenshot](/screenshots/TP4Q1aa.jpg)

![Screenshot](/screenshots/TP4Q1b.jpg)

![Screenshot](/screenshots/TP4Q1c.jpg)

> *curl http://localhost:8000/features/7590-VHVEG*

![Screenshot](/screenshots/TP4Q1d.jpg)

- Tous les composants tournent car : PostgreSQL stocke les snapshots et labels, Feast gère les features, Prefect orchestre les flows, MLflow trace les runs, API sert les prédictions.


## Créer un script d’entraînement + tracking MLflow

> *docker compose exec -e TRAIN_AS_OF=2024-01-31 prefect python /opt/prefect/flows train_baseline.py*

![Screenshot](/screenshots/TP4Q2a.jpg)

- *AS_OF* : 2024-01-31
- *Nombre de lignes du dataset*: 7043
- Les colonnes catégorielles : net_service

- Métriques calculées:
    - AUC : 0.8098
    - F1 : 0.5313
    - Accuracy : 0.7916
    - Temps d’entraînement : 2.71 sec

![Screenshot](/screenshots/TP4Q2b.jpg)

- Fixer AS_OF permet de figer le jeu de données d’entraînement à un instant temporel précis.
- Le paramètre random_state est fixé afin de rendre déterministes les opérations aléatoires du pipeline (split train/validation, initialisation du modèle). Cela garantit que les résultats sont reproductibles.


## Explorer l’interface MLflow et promouvoir un modèle


![Screenshot](/screenshots/TP4Q3a.jpg)

![Screenshot](/screenshots/TP4Q3b.jpg)

![Screenshot](/screenshots/TP4Q3c_1.png)

![Screenshot](/screenshots/TP4Q3d.jpg)


- La promotion via une interface (stages None, Staging, Production) est préférable. En effet, elle centralise la gestion des versions et garantit qu'une seule version est marquée comme "Production" à un instant donné. 
De plus, le référencement via *models:/streamflow_churn/Production* permet à l'API de charger automatiquement la dernière version promue sans modification de code .

## Étendre l’API pour exposer /predict


> *docker compose build api*

> *docker compose up -d api*

![Screenshot](/screenshots/TP4Q4a.jpg)

![Screenshot](/screenshots/TP4Q4b.jpg)

```
Response body
{
  "user_id": "7590-VHVEG",
  "prediction": 0,
  "features_used": {
    "plan_stream_tv": false,
    "months_active": 1,
    "paperless_billing": true,
    "monthly_fee": 29.850000381469727,
    "net_service": "DSL",
    "plan_stream_movies": false,
    "avg_session_mins_7d": 29.14104461669922,
    "unique_devices_30d": 3,
    "rebuffer_events_7d": 1,
    "skips_7d": 4,
    "watch_hours_30d": 24.48365020751953,
    "failed_payments_90d": 1,
    "ticket_avg_resolution_hrs_90d": 16,
    "support_tickets_90d": 0
  }
}

Response headers
 content-length: 423  content-type: application/json  date: Tue,23 Dec 2025 22:56:53 GMT  server: uvicorn 
```

- Le modèle chargé par l'API doit pointer vers *models:/streamflow_churn/Production* plutôt qu'un fichier local. En effet, cette URI MLflow garantit que l'API charge toujours la version validée et promue, sans nécessiter de redéploiement lors d'un changement de modèle. Alors qu'un fichier .pkl local créerait un couplage fort entre le code et un modèle spécifique, rendant les mises à jour plus complexes.

## Robustesse du serving : cas d’échec réalistes

- Pour un user_id existant, on utilise l'exemple dans la réponse précédente:

```
Response body
{
  "user_id": "7590-VHVEG",
  "prediction": 0,
  "features_used": {
    "plan_stream_tv": false,
    "months_active": 1,
    "paperless_billing": true,
    "monthly_fee": 29.850000381469727,
    "net_service": "DSL",
    "plan_stream_movies": false,
    "avg_session_mins_7d": 29.14104461669922,
    "unique_devices_30d": 3,
    "rebuffer_events_7d": 1,
    "skips_7d": 4,
    "watch_hours_30d": 24.48365020751953,
    "failed_payments_90d": 1,
    "ticket_avg_resolution_hrs_90d": 16,
    "support_tickets_90d": 0
  }
}

Response headers
 content-length: 423  content-type: application/json  date: Tue,23 Dec 2025 22:56:53 GMT  server: uvicorn 
```

- Pour un user_id non existant, on utilise l'exemple ci-dessous avec "user_id": "999999" :

![Screenshot](/screenshots/TP4Q5a.jpg)

- Le premier cas est l’entité absente : le user_id demandé n’existe pas dans l’online store Feast, ce qui conduit à des valeurs nulles lors de la récupération des features.

- Le second cas est un online store incomplet ou obsolète, par exemple lorsque la matérialisation n’a pas été exécutée récemment ou a échoué partiellement.
Dans ces situations, l’API détecte précocement les valeurs manquantes et renvoie une erreur explicite avec la liste des features absentes, évitant ainsi de produire une prédiction silencieusement incorrecte.

## Réflexion de synthèse

- MLflow assure la traçabilité des entraînements en enregistrant les paramètres, métriques, artefacts et le code associé à chaque run. Il garantit aussi l’identification des modèles servis via le Model Registry, en liant chaque version de modèle à un run donné.

- Le stage Production indique quelle version du modèle est considérée comme stable et prête à être utilisée en serving.
Au démarrage, l’API charge dynamiquement le modèle pointé par *models:/streamflow_churn/Production*, sans dépendre d’un fichier local.
Cette approche permet des mises à jour de modèle sans redéploiement de l'API.

- Limites de la reproductibilité:

    - Les données sources peuvent évoluer ou être corrigées sans versionnement strict.
    - Le code d’entraînement ou de feature engineering peut changer hors tracking MLflow.
    - MLflow log `requirements.txt` mais pas l'environnement système complet (versions de librairies etc.)
    