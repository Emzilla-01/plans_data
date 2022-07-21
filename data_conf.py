from os import environ as env
data_url_md5_dict={"users": {"url": env.get("USERS_URL"),
                            "md5": env.get("USERS_HASH"),
                            "unique_ix":"user_id"},
                  "plans": {"url":env.get("PLANS_URL"),
                            "md5": env.get("PLANS_HASH"),
                            "unique_ix":"plan_id"}
                    }