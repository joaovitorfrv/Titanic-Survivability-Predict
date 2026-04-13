# 🚢 Sistema de Predição de Sobrevivência do Titanic

> **MVP — Engenharia de Sistemas de Software Inteligentes**

Aplicação Full Stack que consome um modelo de Machine Learning embarcado no backend para realizar predições binárias sobre a sobrevivência de passageiros do Titanic. O usuário preenche um formulário na interface web, os dados são enviados via HTTP para a API Flask, que aplica o modelo treinado e retorna a predição: **0 = Óbito** ou **1 = Sobrevivência**.

A arquitetura é totalmente desacoplada — o frontend é servido de forma estática e se comunica com o backend exclusivamente via requisições REST, sem qualquer dependência de build ou framework adicional.

---

## 🗂️ Arquitetura

```text
/
├── api/                           # Backend (Microsserviço Flask)
│   ├── model/                     # Modelo ML exportado (.joblib) e script de carga
│   ├── schemas/                   # Contratos de validação (Pydantic)
│   ├── tests/                     # Testes automatizados (PyTest)
│   ├── app.py                     # Entrypoint da API
│   └── requirements.txt           # Dependências do backend
├── front/                         # Frontend (Interface Web Vanilla)
│   ├── index.html                 # Estrutura e formulário
│   ├── css/styles.css             # Estilização náutica
│   └── js/app.js                  # Lógica de client HTTP e Data Mapping
├── notebook/                      # Data Science
│   └── mvp_classificacao.ipynb    # Pipeline de Treinamento
└── README.md                      # Esta documentação
```

### Separação de Contextos

| Camada | Responsabilidade |
|---|---|
| `api/` | Exposição do modelo via REST, validação de entrada, documentação OpenAPI |
| `front/` | Interface de usuário estática, coleta de dados e exibição do resultado |
| `notebook/` | Exploração, pré-processamento, treinamento e exportação do modelo |

A comunicação entre frontend e backend ocorre exclusivamente via `Fetch API` (HTTP/JSON), garantindo total independência entre as camadas.

---

## ⚙️ Como Executar — Backend

### Pré-requisitos

- Python 3.9 ou superior instalado
- Terminal com acesso à raiz do projeto

### Passo a Passo

**1. Acesse a pasta da API:**

```bash
cd api
```

**2. Crie o ambiente virtual:**

```bash
python -m venv .venv
```

**3. Ative o ambiente virtual:**

No **Windows (PowerShell)**:
```bash
.venv\Scripts\Activate.ps1
```

No **Linux / macOS**:
```bash
source .venv/bin/activate
```

**4. Instale as dependências:**

```bash
pip install -r requirements.txt
```

**5. Inicie a API:**

```bash
python app.py
```

### Endpoints

| Recurso | URL |
|---|---|
| API REST | `http://127.0.0.1:5000` |
| Documentação Swagger (OpenAPI) | `http://127.0.0.1:5000/openapi/swagger` |

---

## 🌐 Como Executar — Frontend

O frontend não possui etapa de build. Basta abrir o arquivo diretamente no navegador:

```text
front/index.html
```

> **Atenção:** certifique-se de que a API está em execução antes de realizar predições pelo formulário.

---

## 🧪 Testes Automatizados

Os testes são executados com **PyTest** a partir da pasta `api/`. Eles cobrem:

- ✅ Integração com os endpoints da API
- ✅ Validação de tipagem via schemas Pydantic
- ✅ Latência de resposta (limiar: < 500ms por requisição)

### Executando os testes

Com o ambiente virtual ativo e dentro da pasta `api/`, execute:

```bash
pytest tests/
```

Para uma saída mais detalhada:

```bash
pytest tests/ -v
```

---

## 🧠 Pipeline de Machine Learning

O notebook de treinamento está localizado em:

```text
notebook/mvp_classificacao.ipynb
```

### Execução no Google Colab

O notebook pode ser aberto diretamente no Google Colab via importação de URL (opção **Arquivo → Abrir notebook → GitHub/URL**), sem necessidade de configuração de ambiente local.

### Etapas do Pipeline

| Etapa | Descrição |
|---|---|
| Carregamento | Leitura do dataset original do Titanic |
| Análise Exploratória | Verificação de distribuições, nulos e correlações |
| Imputação de Nulos | Substituição de valores ausentes por mediana/moda |
| Encoding | One-Hot Encoding para variáveis categóricas |
| Treinamento | `RandomForestClassifier` do Scikit-Learn |
| Avaliação | Métricas de acurácia, precisão, recall e F1-Score |
| Exportação | Serialização do modelo via `joblib` para `api/model/` |

---

## 🎬 Vídeo de Apresentação

Assista à demonstração completa do projeto no link abaixo:

> 📹 **[Insira o link do vídeo aqui]**

---

## 📄 Licença

Este projeto foi desenvolvido para fins acadêmicos como MVP do curso de **Engenharia de Sistemas de Software Inteligentes**.
