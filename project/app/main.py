import os
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from app.neo4j_client import Neo4jClient
from app.seed import seed_queries
from app.templates import TEMPLATES, pick_template

load_dotenv()

NEO4J_URI = os.getenv("NEO4J_URI", "neo4j://127.0.0.1:7687")
NEO4J_USER = os.getenv("NEO4J_USER", "neo4j")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD", "")

app = FastAPI(title="Fleet Knowledge Graph POC")
client = Neo4jClient(NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD)

class QueryRequest(BaseModel):
    template_id: str
    params: dict

class InvestigateRequest(BaseModel):
    question: str
    params: dict = {}

@app.on_event("shutdown")
def shutdown():
    client.close()

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/ingest/seed")
def ingest_seed(n_vehicles: int = 200, alerts_per_vehicle: int = 20):
    qs = seed_queries(n_vehicles=n_vehicles, alerts_per_vehicle=alerts_per_vehicle)
    for q in qs:
        client.run(q)
    return {"status": "ok", "vehicles": n_vehicles, "alerts_per_vehicle": alerts_per_vehicle}

@app.post("/query")
def run_query(req: QueryRequest):
    tpl = TEMPLATES.get(req.template_id)
    if not tpl:
        raise HTTPException(status_code=400, detail="Unknown template_id")

    missing = [p for p in tpl["required_params"] if p not in req.params]
    if missing:
        raise HTTPException(status_code=400, detail=f"Missing params: {missing}")

    data = client.run(tpl["query"], req.params)
    return {"template_id": req.template_id, "summary": tpl["summary"], "data": data}

@app.post("/investigate")
def investigate(req: InvestigateRequest):
    template_id = pick_template(req.question)
    tpl = TEMPLATES[template_id]

    params = dict(req.params)
    params.setdefault("alert_type", "gps_dropout")
    params.setdefault("from_ts", 0)
    params.setdefault("to_ts", 9999999999999)

    missing = [p for p in tpl["required_params"] if p not in params]
    if missing:
        raise HTTPException(status_code=400, detail=f"Missing params: {missing}")

    data = client.run(tpl["query"], params)

    top = data[0] if data else None
    narrative = f"Template choisi: {template_id}. "
    if top and "firmware" in top:
        narrative += f"Firmware le plus corrélé: {top['firmware']} (count={top['alert_count']})."
    else:
        narrative += "Aucun résultat."

    return {"question": req.question, "template_id": template_id, "params": params, "narrative": narrative, "data": data}

@app.post("/reset")
def reset_db():
    client.run("MATCH (n) DETACH DELETE n;")
    return {"status": "ok"}

