# TP2 - Ingestion mensuelle, validation et snapshots

## Exercice 1 :


### État initial du dépôt
> *ls*

![Screenshot](/screenshots/TP2Q1.jpg)

> *git status*

![Screenshot](/screenshots/TP2Q1a.jpg)

> *tree .*

![Screenshot](/screenshots/TP2Q1b.jpg)

### Structure des données

> *ls data/seeds/month_000*

![Screenshot](/screenshots/TP2Q1c.jpg)

> *ls data/seeds/month_001*

![Screenshot](/screenshots/TP2Q1d.jpg)

## Exercice 2 :

### Schéma PostgreSQL

Le fichier `db/init/001_schema.sql` a été créé

### Fichier .env

Ce fichier contient les variables d’environnement pour la base de données. Il sert à séparer la configuration du code.

> *cat .\docker-compose.yml*

![Screenshot](/screenshots/TP2Q2a.jpg)

> *docker compose up -d postgres*

![Screenshot](/screenshots/TP2Q2b.jpg)

> *docker compose ps*

![Screenshot](/screenshots/TP2Q2c.jpg)

> *docker compose exec postgres psql -U streamflow -d streamflow*

Commande : `\dt`

![Screenshot](/screenshots/TP2Q2d.jpg)

- *users* : informations sur les utilisateurs
- *subscriptions* : détails des abonnements des utilisateurs.  
- *usage_agg_30d* : usage sur 30 jours. 
- *payments_agg_90d* : paiements échoués sur 90 jours  
- *support_agg_90d* : tickets de support sur 90 jours.  
- *labels* : étiquettes churn des utilisateurs.

## Exercice 3 :

### Le service Prefect

Le conteneur Prefect orchestre le pipeline d’ingestion : il lit les CSV, les charge dans PostgreSQL et peut appliquer des validations et des snapshots temporels.

La fonction `upsert_csv` crée une table temporaire, y copie les données du CSV, puis fait un INSERT ... ON CONFLICT DO UPDATE pour mettre à jour ou insérer chaque ligne. Elle garantit l'idempotence.

> *docker compose up -d prefect*

![Screenshot](/screenshots/TP2Q3a.jpg)

> *docker compose up -d prefect*

![Screenshot](/screenshots/TP2Q3b.jpg)

> *docker compose exec -e SEED_DIR=/data/seeds/month_000 -e AS_OF=2024-01-31 prefect python ingest_flow.py*

![Screenshot](/screenshots/TP2Q3c.jpg)

> *docker compose exec postgres psql -U streamflow -d streamflow*

![Screenshot](/screenshots/TP2Q3d.jpg)

On dispose de 7043 clients après month_000.

## Exercice 4 :

### Validation des données

`validate_with_ge` contrôle la qualité des données. Elle vérifie que la structure et les valeurs des tables sont cohérentes (colonnes attendues et valeurs non négatives).
Si une règle échoue, le pipeline s’arrête pour éviter d’introduire des données corrompues dans la suite.

> *docker compose exec -e SEED_DIR=/data/seeds/month_000 -e AS_OF=2024-01-31 prefect python ingest_flow.py*

![Screenshot](/screenshots/TP2Q3e.jpg)

La pipeline s'est terminée sans erreur.

Pour usage_agg_30d :

*gdf.expect_column_values_to_be_between("watch_hours_30d", min_value=0)*
*gdf.expect_column_values_to_be_between("avg_session_mins_7d", min_value=0)*

Ces bornes sont choisies car les valeurs négatives sont impossibles : un utilisateur ne peut pas regarder un nombre d’heures négatif ou avoir une durée de session négative.

Ces validations empêchent d’ingérer des données corrompues, ce qui protège le futur modèle en évitant qu’il apprenne à partir de valeurs absurdes.

## Exercice 5 :

### Snapshots

- *snapshot_month(as_of)* copie les données des tables live dans des tables _snapshots, en ajoutant le champ as_of pour figer l’état des données à la fin du mois.


> *docker compose exec -e SEED_DIR=/data/seeds/month_001 -e AS_OF=2024-02-29 prefect python ingest_flow.py*

![Screenshot](/screenshots/TP2Q5a.jpg)

> *docker compose exec postgres psql -U streamflow -d streamflow*

![Screenshot](/screenshots/TP2Q5b.jpg)

- Pour 2024-01-31, il n’y a aucune ligne.

- Pour 2024-02-29, il y a 7043 lignes.

Conclusion: Les snapshots existent uniquement pour les mois où le flow a été exécuté avec snapshot_month. Pour 2024-02-29, toutes les lignes sont copiées, tandis que 2024-01-31 reste vide car aucune ingestion snapshot n’a été faite pour ce mois.

### Synthèse

![Screenshot](/screenshots/TP2Q5d.jpg)

Les tables live se mettent à jour en continu, ce qui pose 2 problèmes:

- Data leakage : Les tables live contiennent des corrections/mises à jour faites après la période d'étude. Un modèle entraîné dessus utilise des infos qui n'existaient pas au moment de la prédiction réelle.
- Non-reproductibilité : Si on ré-entraîne par exemple 6 mois plus tard, les tables ont changé, donc impossible de reconstruire le même modèle.

*Prévention du data leakage*

Le snapshot du 31/01 contient uniquement ce qui était disponible ce jour-là. Aucune correction ultérieure ne peut "polluer" l'historique.

*Reproductibilité temporelle*

On peut reconstruire l'état exact des données à n'importe quel mois historique. Un modèle entraîné sur un snapshot produit tuojours le même résultat

### Réflexion personnelle 

Le serveur Prefect ne démarrait pas (erreur *Connection refused*).

Ce problème a été résolu avec l'ajout de la ligne: *prefect server start --host 0.0.0.0*
