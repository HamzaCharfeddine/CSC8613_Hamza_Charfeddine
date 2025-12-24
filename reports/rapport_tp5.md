# TP5 - Monitoring et observabilité

## Démarrer la stack pour l'observabilité

> *docker compose up -d*

![Screenshot](/screenshots/TP5Q1a.jpg)

> *docker compose ps*

![Screenshot](/screenshots/TP5Q1b.jpg)

- Prometheus :

![Screenshot](/screenshots/TP5Q1c.jpg)

- Grafana :

![Screenshot](/screenshots/TP5Q1d.jpg)

- Dans le Docker Compose, les conteneurs communiquent entre eux via leurs noms de service (comme dans `docker-compose.yml`). Donc, Promotheus parle aux services via le nom du service Docker Compose.

## Instrumentation de FastAPI avec de métriques Prometheus

- On exécute cette commande 3 fois :

> Invoke-WebRequest `
>   -Uri http://localhost:8000/predict `
>   -Method POST `
>   -Headers @{ "Content-Type" = "application/json" } `
>   -Body '{"user_id":"7590-VHVEG"}'

> *curl http://localhost:8000/metrics*

![Screenshot](/screenshots/TP5Q2a_1.jpg)

- Un histogramme capture la distribution complète des latences via des buckets prédéfinis, permettant de calculer des percentiles (p50, p95, p99) qui révèlent les outliers. Une moyenne simple masque les outliers qui sont les requêtes très lentes.


## Exploration de Prometheus

![Screenshot](/screenshots/TP5Q3a.jpg)

- La target api est bien en état UP, ce qui confirme que Prometheus scrape correctement l’endpoint /metrics exposé par l’API.

![Screenshot](/screenshots/TP5Q3b.jpg)

- Elle indique si une cible est joignable par Prometheus (1 = UP, 0 = DOWN).

![Screenshot](/screenshots/TP5Q3c.jpg)

- C'est un compteur cumulatif du nombre total de requêtes traitées par l’API depuis son démarrage.

![Screenshot](/screenshots/TP5Q3d.jpg)

- C'est le nombre moyen de requêtes par seconde sur les 5 dernières minutes.

![Screenshot](/screenshots/TP5Q3e.jpg)

- Cette valeur représente une approximation de la latence moyenne des requêtes sur une fenêtre glissante de 5 minutes.

## Setup de Grafana Setup et création d'un dashboard minimal

- Le dashboard avant la génération du trafic :

![Screenshot](/screenshots/TP5Q4.jpg)

- Le dashboard après la génération du trafic :

![Screenshot](/screenshots/TP5Q4b.jpg)

- L’éditeur de requête :

![Screenshot](/screenshots/TP5Q4c.jpg)


- Les métriques exposées permettent de détecter des problèmes d’infrastructure ou de performance, comme une hausse du trafic, une augmentation de la latence ou une indisponibilité de l’API. Par contre, elles ne donnent aucune information sur la qualité du modèle ou un éventuel drift des données.

## Drift Detection with Evidently

> *docker compose exec -e REPORT_DIR=/reports/evidently prefect python /opt/prefect/flows/monitor_flow.py*

```
[Evidently] report_html=/reports/evidently/drift_2024-01-31_vs_2024-02-29.html report_json=/reports/evidently/drift_2024-01-31_vs_2024-02-29.json drift_share=0.06 -> NO_ACTION drift_share=0.06 < 0.30 (target_drift=0.0)
```

- Vérification des fichiers JSON et HTML:

![Screenshot](/screenshots/TP5Q5a.jpg)

- Capture des résultats de la commande :

![Screenshot](/screenshots/TP5Q5b.jpg)

- Vérification du contenu du rapport:

![Screenshot](/screenshots/TP5Q5c.jpg)

- Le covariate drift correspond à un changement dans la distribution des features d’entrée entre deux périodes, indépendamment des labels. Par contre, le target drift correspond à un changement dans la distribution de la variable cible (ici churn_label), par exemple une variation du taux de churn.

