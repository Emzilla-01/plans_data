from os import environ as env
from pymongo import MongoClient
import env_public

ca= env.get("CA_PATH")
u= env.get("MONGO_USER")
pw= env.get("MONGO_PW")
clust = env.get("MONGO_CLUST")
rep=env.get("MONGO_REP")
dbname= env.get("MONGO_DBNAME")
p = int(env.get("MONGO_PORT"))

ep=rf'mongodb+srv://{u}:{pw}@{clust}/{dbname}?authSource=admin&replicaSet={rep}&tls=true&tlsCAFile={ca}'
client=MongoClient(ep, port=p)

db = client[dbname]