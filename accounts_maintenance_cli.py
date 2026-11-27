import os
import json
from accounts_maintenance import prune_auth_records,operational_counts
from accounts_period_maintenance import reconcile_due_periods

def main():
    if os.environ.get("ESTOA_MAINTENANCE_PREVIEW")!="true" or os.environ.get("ESTOA_MP_MODE")!="sandbox":
        raise RuntimeError("Maintenance preview disabled")
    print(json.dumps({"pruned":prune_auth_records(),"reconciled":reconcile_due_periods(),"counts":operational_counts()}))

if __name__=="__main__":
    main()
