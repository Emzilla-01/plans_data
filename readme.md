# plans_data

Work sample for a company in the healthcare insurance space.


- **requirements.txt**

    PyPi requirements - prepared in Win10 / WSL Ubuntu 20.04.1 LTS, Python 3.8.10.    
- **db_conf.py**

    PyMongo database connector
- **data_conf.py**

    config related to the origin & shape of the data 
- **data_setup.py**

    convenience script to get, unpack, insert, and teardown client dataset
- **main.py**

    wireframe for some user session to view comparison of their available healthcare plans


## How to use

1. You need `env_secret.py` & relevant `ca-certificate.crt` for the db. Place those in `/plans_data` (base dir of this repo). Without those, this will not work.
2. Create a venv, activate, & `pip install -r requirements.txt`
3. `python data_setup.py` will download, unpack, and insert the data to the db. If you are connecting with provided secrets, you can probably skip this step.
4. `python main.py {user_id}` will query the db for plans data relevant to that user, and print lines to stdout regarding that user's eligible plan, particularly:

>Given a user_id, what is the total predicted cost for the plan they enrolled in? 

>Given a user_id, how does the enrolled plan rank amongst their eligible plans by total predicted cost?


You can also `from main import UserQuery` and invoke like

 `u0 = UserQuery({PyMongo db object}, {user_id per client data})`


Thank you & best regards,

-Emy