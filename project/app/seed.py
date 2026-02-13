import random
import time

REGIONS = ["IDF", "NAQ", "OCC", "ARA", "PACA", "HDF"]
VEH_MODELS = ["Clio", "Megane", "Captur", "Austral"]
DEV_MODELS = ["TBox-A", "TBox-B", "TBox-C"]
FIRMWARES = ["1.8.1", "1.8.2", "1.8.3", "1.9.0"]
ALERT_TYPES = ["gps_dropout", "speed_jitter", "battery_drain"]

def now_ms():
    return int(time.time() * 1000)

def seed_queries(n_vehicles=200, alerts_per_vehicle=20):
    # Pattern injecté: firmware 1.8.3 -> gps_dropout plus fréquent
    t0 = now_ms() - 7 * 24 * 3600 * 1000
    t1 = now_ms()

    queries = []

    # Constraints (Neo4j 5+)
    queries.append("CREATE CONSTRAINT vehicle_id IF NOT EXISTS FOR (v:Vehicle) REQUIRE v.id IS UNIQUE;")
    queries.append("CREATE CONSTRAINT device_id IF NOT EXISTS FOR (d:Device) REQUIRE d.id IS UNIQUE;")
    queries.append("CREATE CONSTRAINT alert_id IF NOT EXISTS FOR (a:Alert) REQUIRE a.id IS UNIQUE;")
    queries.append("CREATE CONSTRAINT incident_id IF NOT EXISTS FOR (i:Incident) REQUIRE i.id IS UNIQUE;")

    for i in range(n_vehicles):
        vid = f"veh_{i:04d}"
        vin = f"VF1{i:014d}"
        region = random.choice(REGIONS)
        model = random.choice(VEH_MODELS)
        dev_id = f"dev_{i:04d}"
        dev_model = random.choice(DEV_MODELS)

        fw = random.choices(FIRMWARES, weights=[3, 3, 6, 2])[0]  # bias vers 1.8.3

        queries.append(
            f"""
            MERGE (v:Vehicle {{id:'{vid}', vin:'{vin}', model:'{model}', region:'{region}'}})
            MERGE (d:Device {{id:'{dev_id}', model:'{dev_model}'}})
            MERGE (f:Firmware {{version:'{fw}'}})
            MERGE (v)-[:HAS_DEVICE]->(d)
            MERGE (v)-[:RUNS_FIRMWARE]->(f);
            """
        )

        for j in range(alerts_per_vehicle):
            aid = f"al_{i:04d}_{j:03d}"
            ts = random.randint(t0, t1)

            if fw == "1.8.3":
                atype = random.choices(ALERT_TYPES, weights=[7, 2, 1])[0]
            else:
                atype = random.choices(ALERT_TYPES, weights=[2, 2, 1])[0]

            queries.append(
                f"""
                MATCH (v:Vehicle {{id:'{vid}'}})
                MERGE (a:Alert {{id:'{aid}'}})
                SET a.type = '{atype}', a.ts = {ts}
                MERGE (v)-[:EMITTED]->(a);
                """
            )


    # Incidents (regroupement simple)
    for k in range(10):
        inc_id = f"inc_{k:03d}"
        inc_type = "gps_dropout"
        severity = random.choice(["low", "medium", "high"])
        start_ts = t0 + k * 12 * 3600 * 1000
        end_ts = start_ts + 6 * 3600 * 1000

        queries.append(
            f"MERGE (i:Incident {{id:'{inc_id}', type:'{inc_type}', severity:'{severity}', start_ts:{start_ts}, end_ts:{end_ts}}});"
        )

        queries.append(
            f"""
            MATCH (a:Alert {{type:'gps_dropout'}})
            WITH a ORDER BY rand() LIMIT 200
            MATCH (i:Incident {{id:'{inc_id}'}})
            MERGE (a)-[:GROUPED_INTO]->(i);
            """
        )

    return queries
