from os import environ as env
[env.setdefault(k,v) for k,v in {
"CA_PATH":"",
"MONGO_USER":"",
"MONGO_PORT": "",
"MONGO_PW":   '',
"MONGO_CLUST":'',
"MONGO_REP" : "",
"MONGO_DBNAME": '',
"USERS_URL":  "",
"USERS_HASH": "",
"PLANS_URL" : "",
"PLANS_HASH" : "",
}.items()]