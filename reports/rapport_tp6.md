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

