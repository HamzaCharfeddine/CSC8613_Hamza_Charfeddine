# TP1 - Fondamentaux du MLOps

## Exercice 1 :

### Question 1 :

> *docker run hello-world*
![Screenshot](/screenshots/Q1b.jpg)

> *docker ps -a*
![Screenshot](/screenshots/Q1c.jpg)

Cette liste contient tous les conteneurs présents sur ma machine, qu’ils soient : 
* en cours d’exécution
* arrêtés

Dans mon cas, elle contient:
* hello-world → conteneur de test qui vient d'être exécuté.

* gotenberg/gotenberg:8 → ancien conteneur d’un service de conversion de documents

* n8nio/n8n → ancien conteneur d’un outil d’automatisation.

## Exercice 2 :

### Question 2 :

Une image est un modèle qui contient tout le nécessaire pour exécuter une application (fichiers, dépendances, configuration). Alors qu'un conteneur est une instance créée à partir de cette image.

> *docker run alpine echo "Bonjour depuis un conteneur Alpine"*
![Screenshot](/screenshots/Q2b.jpg)

→ Docker télécharge l’image alpine si elle n’est pas déjà présente, crée un conteneur, exécute la commande echo, puis arrête le conteneur une fois la commande terminée.

> *docker ps -a*
![Screenshot](/screenshots/Q2c.jpg)

→ Le conteneur alpine s’est terminé juste après avoir exécuté echo, donc il apparaît comme “Exited”.

> *docker run -it alpine sh*
![Screenshot](/screenshots/Q2d.jpg)

* *ls* : affiche le contenu du conteneur
* *uname -a* : affiche les informations du système: noyau Linux donné par Docker/le backend WSL2.

* *exit* : ferme le shell

→ Je remarque que le conteneur s’arrête immédiatement après la fermeture du shell.

→ Ceci montre que le conteneur dispose de son propre environnement Linux isolé.

## Exercice 3 :

### Question 3 :

> *app.py*
```
# TODO: importer FastAPI
from fastapi import FastAPI

# TODO: créer une instance FastAPI
app = FastAPI()

# TODO: définir une route GET /health
@app.get("/health")
def health():
    return {"status": "ok"}
```

> *Dockerfile*

```
# TODO: choisir une image de base Python
FROM python:3.11-slim

# TODO: définir le répertoire de travail dans le conteneur
WORKDIR /app

# TODO: copier le fichier app.py
COPY app.py /app/app.py

# Installer FastAPI et Uvicorn
RUN pip install fastapi uvicorn

# TODO: lancer le serveur au démarrage du conteneur
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
```

> *C:\Users\LENOVO\Desktop\TP1-Docker\simple-api>docker build -t simple-api .*
![Screenshot](/screenshots/Q3c.jpg)


## Exercice 4 :

### Question 4 :
> *docker run -p 8000:8000 simple-api*
![Screenshot](/screenshots/Q3cbis.jpg)

> *http://localhost:8000/health*
![Screenshot](/screenshots/Q3cbisbis.jpg)

> *docker ps*
![Screenshot](/screenshots/Q4c.jpg)

* le nom du conteneur: quirky_benz
* l'image utilisée: simple-api
* le port mappé: 0.0.0.0:8000 -> 8000/tcp

> *docker stop quirky_benz*

![Screenshot](/screenshots/Q4_reponse.jpg)

* *docker ps* : affiche uniquement les conteneurs actuellement en cours d’exécution.

* *docker ps -a* : affiche tous les conteneurs, y compris ceux qui sont arrêtés ou qui se sont terminés après exécution.

## Exercice 5 :

### Question 5 :

> *docker compose up -d*
![Screenshot](/screenshots/Q5a.jpg)

>*docker compose ps*
![Screenshot](/screenshots/Q5abis.jpg)

![Screenshot](/screenshots/Q5b.jpg)

>*docker compose down*
![Screenshot](/screenshots/Q5c.jpg)

* *docker stop <id>* : arrête uniquement un conteneur spécifique, sans supprimer quoi que ce soit.

* *docker compose down* : arrête tous les conteneurs du fichier docker-compose.yml et supprime : les conteneurs, le réseau créé et les ressources associées.

## Exercice 6 :

### Question 6 :

>docker compose up -d

>docker compose ps

![Screenshot](/screenshots/Q6a.jpg)

>*docker compose exec db psql -U demo -d demo*
* *exec* : exécute une commande dans un conteneur en cours d’exécution.

* *db* : nom du service ou conteneur cible (dans notre cas : PostgreSQL).

* *-U demo* : se connecter avec l’utilisateur demo.

* *-d demo* : se connecter à la base de données demo.


>SELECT version();

→ PostgreSQL 16.11 (Debian 16.11-1.pgdg13+1) on x86_64-pc-linux-gnu, compiled by gcc (Debian 14.2.0-19) 14.2.0, 64-bit
>SELECT current_database();

→ current_database demo (1 row)

![Screenshot](/screenshots/Q6b.jpg)

Pour qu’un autre service Docker (comme l’API FastAPI) se connecte à la base PostgreSQL :

* Hostname : "db" (le nom du service)
* Port : 5432
* Utilisateur : demo
* Mot de passe : demo
* Nom de la base : demo

>*docker compose down*

>*docker compose down -v*

![Screenshot](/screenshots/Q6c.jpg)

→ L’option -v supprime les volumes créés et toutes les données de la base sont perdues.

## Exercice 7 :

### Question 7 :

> *docker compose logs -f api*

![Screenshot](/screenshots/Q7a.jpg)
→ Au démarrage de l’API: les logs indiquent que Uvicorn écoute sur le port 8000.

→ Lorsqu’une requête /health est faite: une entrée de log apparaît confirmant le GET.

>*docker compose exec api sh*

![Screenshot](/screenshots/Q7b.jpg)

* *ls* : montre les fichiers copiés dans le conteneur
* *python --version* : confirme la version Python utilisée dans le conteneur.
* *exit* : permet de sortir du conteneur.

![Screenshot](/screenshots/Q7c.jpg)
→ Après redémarrage, l’API reste accessible sur /health.

→ Le redémarrage peut être utile pour appliquer des modifications de configuration.

![Screenshot](/screenshots/Q7d.jpg)

→ Les logs indiquent l’erreur Python: *NameError: name 'appi' is not defined. Did you mean: 'app'?*

→ Cela permet d’identifier la cause du problème.

![Screenshot](/screenshots/Q7e.jpg)

→ Ce nettoyage permet d'éviter l’encombrement du disque avec des conteneurs et images obsolètes.

## Exercice 8 :

### Question 8.1 :

Les notebooks ne garantissent pas la reproductibilité: les environnements, les dépendances et l’ordre d’exécution peuvent varier. En plus, ils ne sont pas faciles à automatiser et à déployer.

### Question 8.2 :

* Permet de définir tous les services et leurs dépendances dans un seul fichier (docker-compose.yml).
* Facilite le démarrage et l’arrêt d’un système qui contient plusieurs conteneurs avec une seule commande.
* Assure que les services (comme les API et les DB) partagent un réseau interne.