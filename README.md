# graph-vehicles

# test ps : znfui78Y_
url neo4j://127.0.0.1:7687


Neo4j Desktop local avec un petit graphe “Fleet Entity Graph”
Une API FastAPI :
POST /ingest/seed → génère et charge des données
POST /investigate → exécute un “playbook” (ex: GPS dropout)
POST /query → exécute une requête templatisée
Un mini “agent” :
prend une question (“quel firmware cause le plus d’alertes GPS ?”)
choisit un template (ex: top_firmware_by_alert_type)
exécute la requête + renvoie un résumé (sans LLM, ou LLM optionnel)

