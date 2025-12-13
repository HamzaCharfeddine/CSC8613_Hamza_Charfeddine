from feast import Entity

# TODO: définir l'entité principale "user"
user = Entity(
    name="user",
    join_keys=["user_id"],
    description="Utilisateur de la plateforme StreamFlow."
)

