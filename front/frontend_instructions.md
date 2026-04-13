# Instruções de Desenvolvimento: Frontend Titanic Predictor

**Objetivo:** Criar uma interface web moderna, responsiva e temática para coletar dados de passageiros e exibir predições de sobrevivência via API.

## 1. Estrutura de Arquivos
O frontend deve ser isolado na pasta `/front` com a seguinte estrutura:
* `index.html`: Estrutura semântica e formulário.
* `css/styles.css`: Estilização temática (Titanic/Náutico).
* `js/app.js`: Lógica de captura, mapeamento de dados e requisição Fetch.

## 2. Requisitos de Input e Mapeamento (Data Mapping)
O script `app.js` deve garantir que os dados enviados ao backend sigam estritamente o formato `float`.

| Campo UI | Tipo Input | Regra de Transformação para o JSON |
| :--- | :--- | :--- |
| **Classe Econômica** | Select (1, 2, 3) | `parseFloat(value)` |
| **Idade** | Number (0-120) | `parseFloat(value)` |
| **Irmãos/Cônjuges** | Number (0-10) | `parseFloat(value)` |
| **Pais/Filhos** | Number (0-10) | `parseFloat(value)` |
| **Tarifa** | Text/Number | `parseFloat(value)` (Range 0.0 a 550.0) |
| **Sexo** | Radio/Select | Masculino -> `1.0`, Feminino -> `0.0` |
| **Embarque** | Select | **Southampton**: `S=1.0, Q=0.0`<br>**Queenstown**: `S=0.0, Q=1.0`<br>**Cherbourg**: `S=0.0, Q=0.0` |

*Nota: O campo `PassengerId` deve ser enviado como um valor padrão (ex: `1.0`) para manter a compatibilidade com as 9 dimensões da API.*

## 3. Design e Experiência (UX)
* **Paleta de Cores:** Azul marinho, branco gelo, cinza metálico e detalhes em dourado/latão.
* **Feedback Visual:** * Exibir um *spinner* de carregamento durante a requisição.
    * Resultado positivo (Sobrevivência): Fundo verde suave ou ícone de bote salva-vidas.
    * Resultado negativo (Óbito): Fundo cinza/azulado ou ícone neutro.
* **Validação:** Impedir o envio se campos obrigatórios estiverem vazios.

## 4. Comunicação com a API
* **Endpoint:** `POST http://127.0.0.1:5000/api/predict`
* **Headers:** `Content-Type: application/json`