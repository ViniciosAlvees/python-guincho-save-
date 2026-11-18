"""Testa o contrato HTTP sem chamar Java ou gravar dados reais."""
import hashlib
import os
import secrets
import time
import unittest
from unittest.mock import patch

import httpx
from fastapi.testclient import TestClient

import api
import employee_auth


class EmployeeAPITest(unittest.TestCase):
    def setUp(self):
        self.pin = str(secrets.randbelow(90000000) + 10000000)
        salt = secrets.token_bytes(16)
        digest = hashlib.pbkdf2_hmac("sha256", self.pin.encode(), salt, 600000)
        self.configuration = {
            "EMPLOYEE_PIN_HASH": f"pbkdf2_sha256$600000${salt.hex()}${digest.hex()}",
            "EMPLOYEE_SESSION_SECRET": secrets.token_urlsafe(48),
        }
        self.environment = patch.dict(os.environ, self.configuration)
        self.environment.start()
        self.addCleanup(self.environment.stop)
        employee_auth._attempts.clear()
        self.client = TestClient(api.app)

    def login(self):
        response = self.client.post("/funcionarios/sessao", json={"pin": self.pin})
        self.assertEqual(response.status_code, 200)
        return response.json()["token"]

    def test_login_contract_and_no_cache(self):
        response = self.client.post("/funcionarios/sessao", json={"pin": self.pin})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers["cache-control"], "no-store")
        self.assertRegex(response.json()["token"], r"^[A-Za-z0-9_-]{86}$")
        self.assertNotIn(self.pin, response.text)
        self.assertIn("expiresAt", response.json())
        self.assertNotEqual(response.json()["token"], self.login())

    def test_wrong_pin(self):
        wrong = str((int(self.pin) + 1) % 100000000).zfill(8)
        self.assertEqual(self.client.post("/funcionarios/sessao", json={"pin": wrong}).status_code, 401)

    def test_bad_format(self):
        for value in (None, 12345678, "1234", "abcdefgh", "１２３４５６７８", "1" * 1000):
            response = self.client.post("/funcionarios/sessao", json={"pin": value})
            self.assertEqual(response.status_code, 400)

    def test_missing_or_bad_configuration_fails_closed(self):
        for value in ("", "invalid", "pbkdf2_sha256$1$aa$bb"):
            with patch.dict(os.environ, {"EMPLOYEE_PIN_HASH": value}):
                response = self.client.post("/funcionarios/sessao", json={"pin": self.pin})
                self.assertEqual(response.status_code, 503)

    def test_anonymous_requests_never_call_java(self):
        with patch("api.chamar_java") as java:
            for path in ("/funcionarios/solicitacoes", "/solicitacoes"):
                response = self.client.get(path)
                self.assertEqual(response.status_code, 401)
                self.assertEqual(response.headers["cache-control"], "no-store")
            java.assert_not_called()

    def test_tampered_expired_and_random_tokens_fail(self):
        token = self.login()
        altered = ("A" if token[0] != "A" else "B") + token[1:]
        for value in (altered, "A" * 86, "bad", token + "="):
            self.assertEqual(self.client.get("/funcionarios/solicitacoes", headers={
                "Authorization": f"Bearer {value}"}).status_code, 401)
        with patch("employee_auth.time.time", return_value=time.time() + 601):
            self.assertEqual(self.client.get("/funcionarios/solicitacoes", headers={
                "Authorization": f"Bearer {token}"}).status_code, 401)

    def test_valid_session_reads_java_without_forwarding_python_token(self):
        token = self.login()
        with patch("api.chamar_java", return_value=[]) as java:
            response = self.client.get("/funcionarios/solicitacoes", headers={
                "Authorization": f"Bearer {token}"})
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.json(), [])
            self.assertEqual(java.call_args.args[1], "/solicitacoes")
            self.assertFalse(java.call_args.kwargs["forward_authorization"])

    def test_pin_rotation_invalidates_existing_sessions(self):
        token = self.login()
        with patch.dict(os.environ, {"EMPLOYEE_SESSION_SECRET": secrets.token_urlsafe(48)}):
            self.assertEqual(self.client.get("/funcionarios/solicitacoes", headers={
                "Authorization": f"Bearer {token}"}).status_code, 401)

    def test_rate_limit(self):
        wrong = str((int(self.pin) + 1) % 100000000).zfill(8)
        for _ in range(5):
            self.assertEqual(self.client.post("/funcionarios/sessao", json={"pin": wrong}).status_code, 401)
        response = self.client.post("/funcionarios/sessao", json={"pin": self.pin})
        self.assertEqual(response.status_code, 429)
        self.assertIn("retry-after", response.headers)

    def test_logout_contract(self):
        token = self.login()
        response = self.client.delete("/funcionarios/sessao", headers={"Authorization": f"Bearer {token}"})
        self.assertEqual(response.status_code, 204)
        self.assertEqual(response.content, b"")
        self.assertEqual(response.headers["cache-control"], "no-store")
        self.assertEqual(self.client.delete("/funcionarios/sessao").status_code, 401)

    def test_java_authorization_and_internal_errors(self):
        token = self.login()
        with patch.object(api, "JAVA_API_URL", "https://java.example.test"):
            for status in (401, 500):
                with patch("api.httpx.Client") as factory:
                    java = factory.return_value.__enter__.return_value
                    java.request.return_value = httpx.Response(status, json={"sql": "INTERNAL_SENTINEL"})
                    response = self.client.get("/funcionarios/solicitacoes", headers={"Authorization": f"Bearer {token}"})
                    self.assertEqual(response.status_code, status if status < 500 else 502)
                    self.assertNotIn("INTERNAL_SENTINEL", response.text)
                    self.assertNotIn("Authorization", java.request.call_args.kwargs["headers"])

    def test_estimation_unchanged(self):
        response = self.client.get("/estimativa", params={"preco_base": 180, "km": 10})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"valor_estimado": 225, "moeda": "BRL"})


if __name__ == "__main__":
    unittest.main()
