TEMPLATES = {
    "top_firmware_by_alert_type": {
        "query": """
        MATCH (v:Vehicle)-[:RUNS_FIRMWARE]->(f:Firmware)
        MATCH (v)-[:EMITTED]->(a:Alert {type: $alert_type})
        WHERE a.ts >= $from_ts AND a.ts <= $to_ts
        RETURN f.version AS firmware, count(a) AS alert_count
        ORDER BY alert_count DESC
        LIMIT 10;
        """,
        "required_params": ["alert_type", "from_ts", "to_ts"],
        "summary": "Top firmwares corrélés au type d’alerte demandé."
    },
    "vehicles_by_incident": {
        "query": """
        MATCH (i:Incident {id: $incident_id})<-[:GROUPED_INTO]-(a:Alert)<-[:EMITTED]-(v:Vehicle)
        RETURN v.id AS vehicle_id, v.region AS region, count(a) AS alerts
        ORDER BY alerts DESC
        LIMIT 50;
        """,
        "required_params": ["incident_id"],
        "summary": "Véhicules les plus impactés par l’incident."
    }
}

def pick_template(question: str) -> str:
    q = question.lower()
    if "firmware" in q and ("gps" in q or "dropout" in q or "alerte" in q):
        return "top_firmware_by_alert_type"
    if "incident" in q and ("véhicule" in q or "vehicle" in q):
        return "vehicles_by_incident"
    return "top_firmware_by_alert_type"
