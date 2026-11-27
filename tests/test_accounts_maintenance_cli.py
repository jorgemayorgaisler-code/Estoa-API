import unittest
from unittest.mock import patch
from accounts_maintenance_cli import main

class MaintenanceCliTests(unittest.TestCase):
    def test_disabled(self):
        with patch.dict("os.environ",{"ESTOA_MAINTENANCE_PREVIEW":"false","ESTOA_MP_MODE":"sandbox"}), patch("accounts_maintenance_cli.prune_auth_records") as prune:
            with self.assertRaises(RuntimeError): main()
            prune.assert_not_called()
    def test_production_blocked(self):
        with patch.dict("os.environ",{"ESTOA_MAINTENANCE_PREVIEW":"true","ESTOA_MP_MODE":"production"}), patch("accounts_maintenance_cli.prune_auth_records") as prune:
            with self.assertRaises(RuntimeError): main()
            prune.assert_not_called()
    def test_sandbox(self):
        with patch.dict("os.environ",{"ESTOA_MAINTENANCE_PREVIEW":"true","ESTOA_MP_MODE":"sandbox"}), patch("accounts_maintenance_cli.prune_auth_records",return_value={}) as prune, patch("accounts_maintenance_cli.reconcile_due_periods",return_value=0) as reconcile, patch("accounts_maintenance_cli.operational_counts",return_value={}) as counts, patch("builtins.print") as output:
            main()
            prune.assert_called_once()
            reconcile.assert_called_once()
            counts.assert_called_once()
            output.assert_called_once()
