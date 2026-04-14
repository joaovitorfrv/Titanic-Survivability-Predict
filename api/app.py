import logging
import json

from flask import jsonify, make_response
from flask import redirect
from flask.wrappers import Response
from flask_cors import CORS
from flask_openapi3 import Info, OpenAPI, Tag
from pydantic import ValidationError

from model.model_loader import build_feature_array, load_model, run_inference
from schemas.predict_schema import (
    ErrorResponse,
    HealthResponse,
    PredictOutput,
    PredictSchema,
)

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s – %(message)s",
)
logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# OpenAPI 3 metadata
# ---------------------------------------------------------------------------
_info = Info(
    title="Titanic Survivability Prediction API",
    version="1.0.0",
    description=(
        "API REST para predição binária de sobrevivência de passageiros "
        "do Titanic usando um RandomForestClassifier (Scikit-Learn)."
    ),
)

_tag_health = Tag(name="Saúde", description="Verificação de disponibilidade da API")
_tag_predict = Tag(name="Inferência", description="Predição de sobrevivência")


# ---------------------------------------------------------------------------
# Validation error callback → garante HTTP 400 (ao invés do padrão 422)
# ---------------------------------------------------------------------------
def _on_validation_error(exc: ValidationError) -> Response:
    """Converte falhas de validação Pydantic em resposta HTTP 400 padronizada."""
    safe_errors = json.loads(exc.json())
    logger.warning("Payload inválido detectado pelo schema.")
    
    # Empacota o JSON e o Status 400 em um único Objeto de Resposta (Response)
    # Isso impede o LookupError no abort() do flask_openapi3
    return make_response(jsonify({
        "error": "Payload inválido", 
        "details": safe_errors
    }), 400)

# ---------------------------------------------------------------------------
# App
# ---------------------------------------------------------------------------
app = OpenAPI(
    __name__,
    info=_info,
    validation_error_status=400,
    validation_error_callback=_on_validation_error,
)

CORS(app, resources={r"/*": {"origins": "*"}})

# ---------------------------------------------------------------------------
# Singleton – modelo carregado na inicialização (fail-fast)
# ---------------------------------------------------------------------------
model = load_model()
logger.info("Modelo carregado com sucesso. API pronta para inferência.")

# ---------------------------------------------------------------------------
# Rotas
# ---------------------------------------------------------------------------

@app.get("/", tags=[_tag_health], responses={"302": None})
def index():
    """Redireciona a raiz para o painel central da documentação (OpenAPI)."""
    return redirect("/openapi")



@app.post(
    "/api/predict",
    tags=[_tag_predict],
    responses={
        "200": PredictOutput,
        "400": ErrorResponse,
        "500": ErrorResponse,
    },
)
def predict(body: PredictSchema) -> Response:
    """Prediz a sobrevivência de um passageiro do Titanic.

    Recebe 9 features numéricas e retorna a classe binária:
    **0** = Óbito · **1** = Sobrevivência.
    """
    try:
        feature_array = build_feature_array(body.model_dump())
        prediction: int = run_inference(model, feature_array)
    except RuntimeError as exc:
        logger.error("Falha na inferência: %s", exc)
        return jsonify({"error": "Falha na inferência", "details": str(exc)}), 500

    message = "Sobrevivência" if prediction == 1 else "Óbito"
    logger.info("Predição: %d (%s)", prediction, message)

    return jsonify({"status": "success", "prediction": prediction, "message": message}),200


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)