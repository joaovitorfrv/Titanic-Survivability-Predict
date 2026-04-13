from typing import Any

from pydantic import BaseModel, ConfigDict, Field, field_validator


# ---------------------------------------------------------------------------
# Request body schema
# ---------------------------------------------------------------------------

class PredictSchema(BaseModel):
    """Schema de validação para o payload de entrada da rota POST /predict.

    Exige exatamente 9 campos numéricos na ordem esperada pelo modelo.
    Campos ausentes, tipos errados ou valores fora de domínio disparam
    ValidationError → HTTP 400 (fail-fast).
    """

    model_config = ConfigDict(
        extra="forbid",  # Rejeita campos desconhecidos
    )

    PassengerId: float = Field(description="Identificador único do passageiro")
    Pclass: float = Field(description="Classe socioeconômica (1ª, 2ª ou 3ª)")
    Age: float = Field(ge=0.0, le=120.0, description="Idade em anos (0–120)")
    SibSp: float = Field(description="Número de irmãos/cônjuges a bordo")
    Parch: float = Field(description="Número de pais/filhos a bordo")
    Fare: float = Field(description="Tarifa paga pelo passageiro")
    Sex_male: float = Field(description="Sexo: 1.0 = masculino, 0.0 = feminino")
    Embarked_Q: float = Field(description="Embarcou em Queenstown: 1.0 = sim")
    Embarked_S: float = Field(description="Embarcou em Southampton: 1.0 = sim")

    @field_validator("Pclass")
    @classmethod
    def validate_pclass(cls, v: float) -> float:
        if v not in (1.0, 2.0, 3.0):
            raise ValueError("Pclass deve ser 1.0, 2.0 ou 3.0")
        return v

    @field_validator("Sex_male", "Embarked_Q", "Embarked_S")
    @classmethod
    def validate_binary_flag(cls, v: float) -> float:
        if v not in (0.0, 1.0):
            raise ValueError("O campo deve ser 0.0 ou 1.0")
        return v


# ---------------------------------------------------------------------------
# Response schemas  (usados pelo flask-openapi3 para gerar o spec OpenAPI 3)
# ---------------------------------------------------------------------------

class HealthResponse(BaseModel):
    """Resposta do endpoint GET /health."""

    status: str = Field(examples=["ok"], description="Estado da API")


class PredictOutput(BaseModel):
    """Resposta de predição bem-sucedida (HTTP 200)."""

    status: str = Field(examples=["success"], description="Estado da operação")
    prediction: int = Field(
        examples=[0],
        description="Classe predita: 0 = Óbito, 1 = Sobrevivência",
    )
    message: str = Field(examples=["Óbito"], description="Rótulo legível da predição")


class ErrorResponse(BaseModel):
    """Resposta de erro (HTTP 400 / 500)."""

    error: str = Field(description="Mensagem de erro resumida")
    details: Any = Field(default=None, description="Detalhes técnicos do erro")
