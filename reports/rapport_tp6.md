# TP6 - CI/CD pour systèmes ML + réentraînement automatisé + promotion MLflow

## Mise en place du rapport et vérifications de départ

> *docker compose up -d*

```
PS C:\Users\LENOVO\Desktop\TP1-Docker> docker compose up -d
[+] Running 8/8
 ✔ Network tp1-docker_default       Created
            0.0s
 ✔ Container tp1-docker-mlflow-1    Started
            2.4s
 ✔ Container tp1-docker-postgres-1  Started
            2.5s
 ✔ Container tp1-docker-feast-1     Started
            4.0s
 ✔ Container tp1-docker-prefect-1   Started
            3.8s
 ✔ Container tp1-docker-api-1       Started
            5.4s
 ✔ Container streamflow-prometheus  Started
            6.3s
 ✔ Container streamflow-grafana     Started
```

> *docker compose ps*

```
streamflow-grafana      grafana/grafana:11.2.0          "/run.sh"                grafana      12 seconds ago   Up 6 seconds    0.0.0.0:3000->3000/tcp, [::]:3000->3000/tcp
streamflow-prometheus   prom/prometheus:v2.55.1         "/bin/prometheus --c…"   prometheus   12 seconds ago   Up 7 seconds    0.0.0.0:9090->9090/tcp, [::]:9090->9090/tcp
tp1-docker-api-1        tp1-docker-api                  "uvicorn app:app --h…"   api          13 seconds ago   Up 8 seconds    0.0.0.0:8000->8000/tcp, [::]:8000->8000/tcp
tp1-docker-feast-1      tp1-docker-feast                "bash -lc 'tail -f /…"   feast        13 seconds ago   Up 10 seconds
tp1-docker-mlflow-1     ghcr.io/mlflow/mlflow:v2.16.0   "mlflow server --bac…"   mlflow       13 seconds ago   Up 11 seconds   0.0.0.0:15000->5000/tcp, [::]:15000->5000/tcp
tp1-docker-postgres-1   postgres:16                     "docker-entrypoint.s…"   postgres     13 seconds ago   Up 11 seconds   0.0.0.0:5432->5432/tcp, [::]:5432->5432/tcp
tp1-docker-prefect-1    tp1-docker-prefect              "/usr/bin/tini -g --…"   prefect      13 seconds ago   Up 10 seconds   0.0.0.0:4200->4200/tcp, [::]:4200->4200/tcp
```

![Screenshot](/screenshots/TP6Q1a.jpg)

![Screenshot](/screenshots/TP6Q1b.jpg)


## Ajouter une logique de décision testable (unit test)

> *pytest -q*

```
PS C:\Users\LENOVO\Desktop\TP1-Docker> pytest -q
..                                                                                                                                                                                                                                            [100%] 
2 passed in 0.12s
```

![Screenshot](/screenshots/TP6Q2a_1.jpg)

- On extrait une fonction pure pour pouvoir tester la logique de décision de promotion de manière isolée et déterministe.

## Créer le flow Prefect train_and_compare_flow (train → eval → compare → promote)

> *docker compose exec prefect python train_and_compare_flow.py*

```
09:36:56.726 | INFO    | Task run 'evaluate_production-d23' - Finished in state Completed()
[COMPARE] candidate_auc=0.8193 vs prod_auc=0.9639 (delta=0.0100)
[DECISION] skipped
09:36:56.814 | INFO    | Task run 'compare_and_promote-ebe' - Finished in state Completed()
[SUMMARY] as_of=2024-02-29 cand_v=3 cand_auc=0.8193 prod_v=1 prod_auc=0.9639 -> skipped
09:36:56.892 | INFO    | Flow run 'remarkable-honeybee' - Finished in state Completed()
```

![Screenshot](/screenshots/TP6Q3a.jpg)

- Le modèle candidat n’a pas été promu car sa performance (AUC) était inférieure à celle du modèle actuellement en production.

- Le delta permet d’éviter des promotions dues à des fluctuations statistiques mineures et garantit que seuls les modèles apportant une amélioration significative sont mis en production.

## Connecter drift → retraining automatique

> *docker compose exec prefect python monitor_flow.py*

```
10:15:23.476 | INFO    | Task run 'evaluate_production-3fc' - Finished in state Completed()
[COMPARE] candidate_auc=0.8193 vs prod_auc=0.9639 (delta=0.0100)
[DECISION] skipped
10:15:23.639 | INFO    | Task run 'compare_and_promote-bac' - Finished in state Completed()
[SUMMARY] as_of=2024-02-29 cand_v=4 cand_auc=0.8193 prod_v=1 prod_auc=0.9639 -> skipped
10:15:23.731 | INFO    | Flow run 'imported-barracuda' - Finished in state Completed()
10:15:23.739 | INFO    | Task run 'decide_action-0b7' - Finished in state Completed()
[Evidently] report_html=/reports/evidently/drift_2024-01-31_vs_2024-02-29.html report_json=/reports/evidently/drift_2024-01-31_vs_2024-02-29.json drift_share=0.06 -> RETRAINING_TRIGGERED drift_share=0.06 >= 0.02 -> skipped
10:15:23.802 | INFO    | Flow run 'romantic-avocet' - Finished in state Completed()
```

![Screenshot](/screenshots/TP6Q4a.jpg)


## Redémarrage API pour charger le nouveau modèle Production + test /predict

```
Invoke-RestMethod `
>>   -Uri "http://localhost:8000/predict" `
>>   -Method POST `
>>   -ContentType "application/json" `
>>   -Body '{"user_id":"7590-VHVEG"}'
```

```
user_id    prediction features_used
-------    ---------- -------------
7590-VHVEG          0 @{plan_stream_tv=False; paperless_billing=True; net_service=DSL; monthly_fee=29.850000381469727; plan_stream_movies=False; months_active=1; rebuffer_events_7d=1; watch_hours_30d=24.48365020751953; avg_session_mins_7d=29...
```

- L’API doit être redémarrée car le modèle MLflow est chargé au démarrage du service et une promotion vers production n’est prise en compte qu’après rechargement du modèle.

## CI GitHub Actions (smoke + unit) avec Docker Compose

![Screenshot](/screenshots/TP6Q5a.jpg)

- Docker Compose est utilisé dans la CI afin de valider l’intégration entre les services dans un environnement proche de la production.

## Synthèse finale : boucle complète drift → retrain → promotion → serving

- Le drift des données est mesuré à l’aide d’Evidently en comparant les distributions de features entre les deux mois. Le *drift_share* représente la proportion de variables en drift. Le seuil de 0.02 est utilisé dans ce TP mais en pratique, ce seuil serait plus élevé.

- Lorsque le seuil est dépassé, le flow Prefect train_and_compare_flow est automatiquement déclenché. Il entraîne un modèle candidat, évalue sa performance (AUC), puis la compare à celle du modèle actuellement en production. La promotion est décidée uniquement si le gain dépasse un delta minimal, garantissant que seules les améliorations significatives sont déployées.

- Prefect est responsable de l’orchestration MLOps (monitoring, retraining, décision), tandis que GitHub Actions assure la qualité du code via des tests unitaires et des tests d’intégration multi-services exécutés dans Docker Compose.

## Limites et améliorations

- La CI ne doit pas entraîner le modèle complet car l’entraînement est lent et non déterministe.

- Des tests pourraient être ajoutés comme la validation de données et du schéma des features par exemple.

- L’approbation humaine est nécessaire car la mise en production d'un modèle impacte directement les clients ou le business.