from sys import argv

from db_conf import db
################################################################################
class UserQuery():
    def __init__(self, db, user_id):
        self.db=db
        self.user_id=str(user_id)
        self.plans_dict=dict()
        self.user_doc = db.users.find_one({'user_id':self.user_id})
        self.eligible_plans_oop_dict = {p.get("plan_id"):p.get("oop") for p in self.user_doc.get("eligible_plans")} # Extra step? dict makes it easier to check by plan_id key than many [p for p in plans if p.get('plan_id')==plan_id][0]
        self.enrolled_plan = self.user_doc.get('enrolled_plan')

    def get_pred_costs_per_plan(self, plan_id, v=False):
        if plan_id:
            self.plans_dict.setdefault(plan_id, db.plans.find_one({"plan_id":plan_id}))
            try:
                self.plans_dict[plan_id].setdefault("oop", float(self.eligible_plans_oop_dict.get(plan_id)))
            except AttributeError as e:
                print(f"user_id:{self.user_id} missing data on plan_id: {plan_id}")
            
            pred_cost =  round(float(self.plans_dict.get(plan_id).get('premium')) + self.plans_dict.get(plan_id).get('oop'), 2)
            self.plans_dict[plan_id].setdefault("pred_cost", pred_cost)
            if v:
                print(f"\nHello {self.user_id}, the predicted cost of your plan is {pred_cost}.")
            # return(plan_id, pred_cost)
        return
        
    def populate_plans_dict_w_pred_cost(self):
        [self.get_pred_costs_per_plan(plan_id) for plan_id in self.eligible_plans_oop_dict ]

    def get_comparison_rows(self):
        self.populate_plans_dict_w_pred_cost()
        row_keys = ['plan_id', 'metal_level', 'oop', 'premium', 'pred_cost']
        comparison_rows = list()
        for plan_id in self.eligible_plans_oop_dict:
            comparison_rows.append([self.plans_dict.get(plan_id).get(k) for k in row_keys])
        comparison_rows.sort(key=lambda r: r[4])
        self.comparison_rows=comparison_rows

    def get_plan_name(self, plan_id):
            return(f"{self.plans_dict.get(plan_id).get('metal_level')} {plan_id.title()}")   
             
    def textfmt_ix_nth(self, ix):
        if ix in range(4, 21):
            return(f"{ix}th")
        ix_lang_nth_dict = {0 : "th",
                            1 : "st", 
                            2 : "nd",
                            3 : "rd",
                            4 : "th"}
        for i in range(4, 10):
            ix_lang_nth_dict.setdefault(i, f"th")
        return(str(ix)+ix_lang_nth_dict.get(ix % 10))

    def rank_plan(self, plan_id):
        try:
            self.comparison_rows
        except AttributeError as e:
            self.get_comparison_rows()
        plan_row = [p for p in self.comparison_rows if [p[0]==plan_id]][0]
        ix = self.comparison_rows.index(plan_row)+1
        return(self.textfmt_ix_nth(ix))
        
    
    def view_available_plans(self):
        s=""
        for ix, p in enumerate(self.comparison_rows):
            # s+=f"\n{self.get_plan_name(p[0])}, predicted cost:{p[4]}, rank: {self.rank_plan(p[0])}"
            s+=f"\n{self.get_plan_name(p[0])}, predicted cost: {p[4]}, value rank: {self.textfmt_ix_nth(ix+1)}"
        return(s)

    def view_comparison(self):
        not_enrolled=False
        try:
            self.comparison_rows
        except AttributeError as e:
                self.get_comparison_rows()
        try:
            self.get_plan_name(self.user_doc.get("enrolled_plan"))
        except AttributeError as e:
            not_enrolled=True
        if not_enrolled:
            str_view = "Our records indicate that you are not enrolled in any health plan, but you are eligible for these available plans:\n"
        else:
            view_dict = {"user_name":self.user_id.title(),
                    "enrolled_plan_name": self.get_plan_name(self.user_doc.get("enrolled_plan")),
                    "enrolled_nth_rank": self.rank_plan(self.user_doc.get("enrolled_plan")),
                    }
            str_view=f"""Our records show that you are enrolled in {view_dict.get('enrolled_plan_name')}.\nAccording to our estimation, this plan ranks {view_dict.get('enrolled_nth_rank')} in lowest cost compared to other available plans.
            
            Available plans:"""
        str_view+=self.view_available_plans()
        str_view+="\neggs\nspam"
        print(str_view)

################################################################################

if __name__ == "__main__":
    u = UserQuery(db, argv[1])
    u.get_pred_costs_per_plan(u.user_doc.get("enrolled_plan"), v=True)
    u.view_comparison()