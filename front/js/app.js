/* =====================================================================
   Titanic Predictor — app.js
   Captura o formulário, monta o payload e chama POST /api/predict
===================================================================== */

'use strict';

const API_URL = 'http://127.0.0.1:5000/api/predict';

/* --- Referências ao DOM --- */
const form       = document.getElementById('predict-form');
const submitBtn  = document.getElementById('submit-btn');
const feedback   = document.getElementById('feedback');
const fbIcon     = document.getElementById('feedback-icon');
const fbTitle    = document.getElementById('feedback-title');
const fbMessage  = document.getElementById('feedback-message');

/* -----------------------------------------------------------------------
   Helpers
----------------------------------------------------------------------- */

/** Ativa/desativa o estado de carregamento do botão. */
function setLoading(active) {
  submitBtn.disabled = active;
  submitBtn.classList.toggle('loading', active);
}

/**
 * Exibe a área de feedback com o estado visual, ícone, título e mensagem.
 *
 * @param {'survived'|'died'|'api-error'|'net-error'|'validation-error'} state
 * @param {string} icon   Emoji ou caractere usado como ícone.
 * @param {string} title  Título em destaque.
 * @param {string} message Texto descritivo.
 */
function showFeedback(state, icon, title, message) {
  /* Reseta classes anteriores e aplica o novo estado */
  feedback.className = `feedback ${state}`;
  fbIcon.textContent    = icon;
  fbTitle.textContent   = title;
  fbMessage.textContent = message;
  feedback.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
}

function hideFeedback() {
  feedback.className = 'feedback hidden';
}

/**
 * Converte o porto de embarque selecionado nos dois campos binários
 * que a API espera (Embarked_S e Embarked_Q).
 *
 * Mapeamento:
 *   Southampton (S) → Embarked_S=1.0, Embarked_Q=0.0
 *   Queenstown  (Q) → Embarked_S=0.0, Embarked_Q=1.0
 *   Cherbourg   (C) → Embarked_S=0.0, Embarked_Q=0.0
 *
 * @param {'S'|'Q'|'C'} value
 * @returns {{ Embarked_S: number, Embarked_Q: number }}
 */
function embarkedFlags(value) {
  if (value === 'S') return { Embarked_S: 1.0, Embarked_Q: 0.0 };
  if (value === 'Q') return { Embarked_S: 0.0, Embarked_Q: 1.0 };
  /* 'C' — Cherbourg: ambos em zero */
  return { Embarked_S: 0.0, Embarked_Q: 0.0 };
}

/* -----------------------------------------------------------------------
   Submit handler
----------------------------------------------------------------------- */
form.addEventListener('submit', async (event) => {
  event.preventDefault();

  /* ── 1. Validação de campos obrigatórios ─────────────────────────── */
  const fieldIds = ['pclass', 'sex', 'age', 'fare', 'sibsp', 'parch', 'embarked'];

  const firstEmpty = fieldIds.find((id) => {
    const el = document.getElementById(id);
    return el.value === '' || el.value === null;
  });

  if (firstEmpty) {
    showFeedback(
      'validation-error',
      '⚠️',
      'Campos obrigatórios',
      'Por favor, preencha todos os campos antes de continuar.'
    );
    document.getElementById(firstEmpty).focus();
    return;
  }

  /* ── 2. Data Mapping — conversão rigorosa para float ─────────────── */
  const embarked = document.getElementById('embarked').value;
  const { Embarked_S, Embarked_Q } = embarkedFlags(embarked);

  const payload = {
    PassengerId: 1.0,
    Pclass:      parseFloat(document.getElementById('pclass').value),
    Age:         parseFloat(document.getElementById('age').value),
    SibSp:       parseFloat(document.getElementById('sibsp').value),
    Parch:       parseFloat(document.getElementById('parch').value),
    Fare:        parseFloat(document.getElementById('fare').value),
    Sex_male:    parseFloat(document.getElementById('sex').value),
    Embarked_Q,
    Embarked_S,
  };

  /* ── 3. Estado de carregamento ───────────────────────────────────── */
  hideFeedback();
  setLoading(true);

  /* ── 4. Requisição fetch ─────────────────────────────────────────── */
  try {
    const response = await fetch(API_URL, {
      method:  'POST',
      headers: { 'Content-Type': 'application/json' },
      body:    JSON.stringify(payload),
    });

    const data = await response.json();

    /* ── 5a. Sucesso HTTP 200 ─────────────────────────────────────── */
    if (response.ok) {
      if (data.prediction === 1) {
        showFeedback(
          'survived',
          '🛟',
          'Sobrevivência!',
          `${data.message} — Este passageiro teria sobrevivido ao naufrágio do Titanic.`
        );
      } else {
        showFeedback(
          'died',
          '⚓',
          'Óbito',
          `${data.message} — Este passageiro não teria sobrevivido ao naufrágio do Titanic.`
        );
      }
    } else {
      /* ── 5b. Erro HTTP (400 / 500) ─────────────────────────────── */
      const errorText = data.error || `Erro HTTP ${response.status}`;
      showFeedback(
        'api-error',
        '⛔',
        `Erro na Predição (HTTP ${response.status})`,
        errorText
      );
    }

  } catch {
    /* ── 5c. Erro de rede — servidor indisponível ──────────────────── */
    showFeedback(
      'net-error',
      '🔌',
      'Servidor Indisponível',
      'Não foi possível conectar à API. Verifique se o servidor Flask está rodando em http://127.0.0.1:5000.'
    );
  } finally {
    setLoading(false);
  }
});
