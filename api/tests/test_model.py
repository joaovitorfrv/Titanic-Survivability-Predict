"""Testes automatizados da Titanic Survivability API.

Cobertura obrigatória:
  1. Integração   – payload válido → HTTP 200, predição binária.
  2. Threshold    – inferência deve completar em < 500 ms.
  3. Resiliência  – payloads inválidos → HTTP 400 (sem quebrar o servidor).

Execução:
    cd api/
    pytest tests/ -v
"""

import json
import os
import sys
import time

import pytest

# Garante que 'api/' esteja no PATH para importar app.py e seus módulos
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app import app as flask_app  # noqa: E402


# ---------------------------------------------------------------------------
# Payload canônico (Jack Dawson – 3ª classe, sexo masculino, Southampton)
# ---------------------------------------------------------------------------
VALID_PAYLOAD: dict = {
    "PassengerId": 1,
    "Pclass": 3.0,
    "Age": 22.0,
    "SibSp": 1.0,
    "Parch": 0.0,
    "Fare": 7.25,
    "Sex_male": 1.0,
    "Embarked_Q": 0.0,
    "Embarked_S": 1.0,
}

THRESHOLD_MS: int = 500


# ---------------------------------------------------------------------------
# Fixture – cliente de teste Flask
# ---------------------------------------------------------------------------
@pytest.fixture(scope="module")
def client():
    """Fornece o test client do Flask para toda a sessão de testes."""
    flask_app.config["TESTING"] = True
    with flask_app.test_client() as test_client:
        yield test_client


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def _post_predict(client, payload: dict):
    """Atalho para POST /predict com Content-Type correto."""
    return client.post(
        "/predict",
        data=json.dumps(payload),
        content_type="application/json",
    )


# ---------------------------------------------------------------------------
# 1. Testes de Integração
# ---------------------------------------------------------------------------
class TestIntegration:
    def test_valid_payload_returns_200(self, client) -> None:
        """Payload completo e correto deve retornar HTTP 200."""
        response = _post_predict(client, VALID_PAYLOAD)
        assert response.status_code == 200

    def test_valid_payload_returns_binary_prediction(self, client) -> None:
        """A predição deve ser exatamente 0 (Óbito) ou 1 (Sobrevivência)."""
        response = _post_predict(client, VALID_PAYLOAD)
        data = response.get_json()
        assert data["status"] == "success"
        assert data["prediction"] in (0, 1)

    def test_valid_payload_returns_correct_message(self, client) -> None:
        """A mensagem deve ser coerente com a predição retornada."""
        response = _post_predict(client, VALID_PAYLOAD)
        data = response.get_json()
        expected_message = "Sobrevivência" if data["prediction"] == 1 else "Óbito"
        assert data["message"] == expected_message

    def test_health_endpoint(self, client) -> None:
        """O endpoint /health deve sempre retornar HTTP 200."""
        response = client.get("/health")
        assert response.status_code == 200
        assert response.get_json()["status"] == "ok"


# ---------------------------------------------------------------------------
# 2. Teste de Threshold (Desempenho)
# ---------------------------------------------------------------------------
class TestPerformance:
    def test_inference_below_500ms(self, client) -> None:
        """A inferência completa (rede + modelo) deve ocorrer em < 500 ms."""
        start = time.perf_counter()
        response = _post_predict(client, VALID_PAYLOAD)
        elapsed_ms = (time.perf_counter() - start) * 1000

        assert response.status_code == 200, "Requisição falhou – verifique o servidor."
        assert elapsed_ms < THRESHOLD_MS, (
            f"Tempo de inferência {elapsed_ms:.1f} ms ultrapassou o threshold de "
            f"{THRESHOLD_MS} ms."
        )


# ---------------------------------------------------------------------------
# 3. Testes de Resiliência
# ---------------------------------------------------------------------------
class TestResilience:
    def test_missing_fields_returns_400(self, client) -> None:
        """Payload incompleto deve retornar HTTP 400."""
        incomplete = {"PassengerId": 1, "Pclass": 3.0}
        response = _post_predict(client, incomplete)
        assert response.status_code == 400

    def test_invalid_pclass_returns_400(self, client) -> None:
        """Pclass fora do conjunto {1.0, 2.0, 3.0} deve retornar HTTP 400."""
        payload = {**VALID_PAYLOAD, "Pclass": 9.0}
        response = _post_predict(client, payload)
        assert response.status_code == 400

    def test_age_out_of_range_returns_400(self, client) -> None:
        """Age > 120 deve retornar HTTP 400."""
        payload = {**VALID_PAYLOAD, "Age": 200.0}
        response = _post_predict(client, payload)
        assert response.status_code == 400

    def test_negative_age_returns_400(self, client) -> None:
        """Age negativa deve retornar HTTP 400."""
        payload = {**VALID_PAYLOAD, "Age": -1.0}
        response = _post_predict(client, payload)
        assert response.status_code == 400

    def test_invalid_sex_male_returns_400(self, client) -> None:
        """Sex_male fora de {0.0, 1.0} deve retornar HTTP 400."""
        payload = {**VALID_PAYLOAD, "Sex_male": 2.0}
        response = _post_predict(client, payload)
        assert response.status_code == 400

    def test_invalid_embarked_q_returns_400(self, client) -> None:
        """Embarked_Q fora de {0.0, 1.0} deve retornar HTTP 400."""
        payload = {**VALID_PAYLOAD, "Embarked_Q": 5.0}
        response = _post_predict(client, payload)
        assert response.status_code == 400

    def test_invalid_embarked_s_returns_400(self, client) -> None:
        """Embarked_S fora de {0.0, 1.0} deve retornar HTTP 400."""
        payload = {**VALID_PAYLOAD, "Embarked_S": -1.0}
        response = _post_predict(client, payload)
        assert response.status_code == 400

    def test_unknown_fields_returns_400(self, client) -> None:
        """Campos extras desconhecidos no payload devem retornar HTTP 400."""
        payload = {**VALID_PAYLOAD, "campo_intruso": 999}
        response = _post_predict(client, payload)
        assert response.status_code == 400

    def test_wrong_content_type_returns_400(self, client) -> None:
        """Requisição sem Content-Type application/json deve retornar HTTP 400."""
        response = client.post(
            "/predict",
            data="PassengerId=1",
            content_type="text/plain",
        )
        assert response.status_code == 400

    def test_empty_payload_returns_400(self, client) -> None:
        """Payload vazio ({}) deve retornar HTTP 400."""
        response = _post_predict(client, {})
        assert response.status_code == 400

    def test_string_value_for_numeric_field_returns_400(self, client) -> None:
        """Tipo errado (string onde se espera número) deve retornar HTTP 400."""
        payload = {**VALID_PAYLOAD, "Age": "vinte e dois"}
        response = _post_predict(client, payload)
        assert response.status_code == 400
