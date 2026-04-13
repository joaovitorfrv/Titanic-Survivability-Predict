import os
from typing import Any

import joblib
import numpy as np
from numpy.typing import NDArray


_MODEL_PATH: str = os.path.join(os.path.dirname(__file__), "modelo_titanic_rf.joblib")

# Ordem das features exigida pelo modelo treinado
FEATURE_ORDER: list[str] = [
    "PassengerId",
    "Pclass",
    "Age",
    "SibSp",
    "Parch",
    "Fare",
    "Sex_male",
    "Embarked_Q",
    "Embarked_S",
]


def load_model() -> Any:
    """Carrega o RandomForestClassifier do disco via joblib.

    Returns:
        Instância do modelo treinado pronta para inferência.

    Raises:
        FileNotFoundError: Se o arquivo .joblib não for encontrado.
        RuntimeError: Se a desserialização falhar por qualquer motivo.
    """
    if not os.path.exists(_MODEL_PATH):
        raise FileNotFoundError(
            f"Arquivo de modelo não encontrado em: {_MODEL_PATH}\n"
            "Certifique-se de que 'modelo_titanic_rf.joblib' está em api/model/."
        )

    try:
        model = joblib.load(_MODEL_PATH)
    except Exception as exc:
        raise RuntimeError(
            f"Falha ao desserializar o modelo em '{_MODEL_PATH}': {exc}"
        ) from exc

    return model


def build_feature_array(validated_data: dict[str, float]) -> NDArray[np.float64]:
    """Constrói o array NumPy na ordem exata esperada pelo modelo.

    Args:
        validated_data: Dicionário já validado pelo PredictSchema.

    Returns:
        Array de shape (1, 9) com dtype float64.
    """
    features: list[float] = [validated_data[field] for field in FEATURE_ORDER]
    return np.array(features, dtype=np.float64).reshape(1, -1)


def run_inference(model: Any, feature_array: NDArray[np.float64]) -> int:
    """Executa a predição e retorna a classe como inteiro (0 ou 1).

    Args:
        model: Modelo carregado via load_model().
        feature_array: Array (1, 9) gerado por build_feature_array().

    Returns:
        0 (Óbito) ou 1 (Sobrevivência).

    Raises:
        RuntimeError: Se a inferência falhar inesperadamente.
    """
    try:
        prediction: NDArray = model.predict(feature_array)
        return int(prediction[0])
    except Exception as exc:
        raise RuntimeError(f"Erro durante a inferência: {exc}") from exc
