import unittest
from unittest.mock import patch
from fastapi import FastAPI
from fastapi.testclient import TestClient
from accounts_navigation import build_navigation_router, ROUTES

class NavigationTests(unittest.TestCase):
    def test_routes(self):
        source=FastAPI()
        def calculate(station_id: str):
            return {"station_id":station_id}
        for path in ROUTES:
            source.add_api_route(path,calculate,methods=["GET"])
        preview=FastAPI()
        preview.include_router(build_navigation_router(source,{"CUR001","CUR002"}))
        client=TestClient(preview)
        headers={"Authorization":"Bearer test"}
        for path in ROUTES:
            self.assertEqual(client.get("/private"+path,params={"station_id":"CUR001"}).status_code,401)
            with patch("accounts_station_guard.session_account",return_value="account"), patch("accounts_station_guard.require_station",side_effect=PermissionError):
                self.assertEqual(client.get("/private"+path,params={"station_id":"CUR002"},headers=headers).status_code,403)
            with patch("accounts_station_guard.session_account",return_value="account"), patch("accounts_station_guard.require_station"):
                self.assertEqual(client.get("/private"+path,params={"station_id":"CUR001"},headers=headers).json(),{"station_id":"CUR001"})
    def test_missing_route_fails_closed(self):
        with self.assertRaises(RuntimeError):
            build_navigation_router(FastAPI(),{"CUR001"})
