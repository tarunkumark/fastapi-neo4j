from fastapi import FastAPI
import journey
import atexit
from fastapi.middleware.cors import CORSMiddleware

uri = "neo4j+s://d9b2e68a.databases.neo4j.io:7687"
user = "neo4j"
password = "r5jEriMLjfN2IN9AQaFUSm505xJ-JpDfCRd4-4k8h1w"
neo_db = journey.Journey(uri, user, password)

def exit_application():
    neo_db.close()
atexit.register(exit_application)

app = FastAPI()
origins = [
    "*"
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get('/get-station')
async def get_station():
    result = neo_db.find_all()
    return result

@app.get('/get-journey')
async def get_journey(start: str, end: str, count: int):
    result = neo_db.find_journey(start, end, count)
    
    journey = []
    
    # loop over the result, each row contains path and weight
    for row in result:
        paths = []
        # used to store the last node information for synchronization
        last_node_id = -1
        last_node_mrt = "x"

        for path in row['path']:
            # get all the nodes in the path
            nodes = [n for n in path.nodes]

            # append the result if it is the first node, mostly for visualization purpose
            if(last_node_id == -1):
                id = 0
                if(nodes[0]['name'] != start):
                    id = 1
                paths.append({"name": nodes[id]['name'].title(), "mrt": nodes[id]['mrt'], "time": "start here"})
                last_node_id = nodes[id].id
                last_node_mrt = nodes[id]['mrt']

            # flag to determine is we should use the first element or the second element as they are marked by id and might not be in order
            id = 0
            if(last_node_id != nodes[1].id):
                id = 1

            # use information from the previous node if it is an interchange
            mrt = nodes[id]['mrt']
            if(nodes[id]['mrt'] == 'x'):
                mrt = last_node_mrt

            paths.append({"name": nodes[id]['name'].title(), "mrt": mrt,"time": "%s minutes" % (path['time'])})
            last_node_id = nodes[id].id
            last_node_mrt = mrt
        journey.append({"path": paths, "weight": row['weight']})

    return journey


