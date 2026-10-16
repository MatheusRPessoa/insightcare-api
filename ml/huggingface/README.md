
---
language:
- pt
tags:
- scikit-learn
- text-classification
- tf-idf
- logistic-regression
- portuguese
- customer-support
metrics:
- accuracy
- f1
---

# InsightCare AI — Intent Classifier

Modelo de classificação de intenções em conversas de atendimento
ao cliente em português brasileiro.

Desenvolvido como parte do projeto InsightCare AI.

## Arquitetura

- Linguagem: Python 3.12
- Vetorização: TF-IDF (unigramas e bigramas)
- Algoritmo: Logistic Regression
- Biblioteca: scikit-learn
- Melhor hiperparâmetro: C = 10.0

## Dataset

Fonte:
RichardSakaguchiMS/brazilian-customer-service-conversations

https://huggingface.co/datasets/RichardSakaguchiMS/brazilian-customer-service-conversations

Dataset sintético com 944 conversas.

- Treinamento: 755 registros
- Validação: 94 registros
- Teste: 95 registros

O modelo final foi ajustado com treinamento + validação,
após a seleção de hiperparâmetros.

## Classes

- cancelamento
- compra
- duvida_produto
- duvida_servico
- elogio
- outros
- reclamacao
- saudacao
- suporte_tecnico

## Resultados

Avaliação em 95 exemplos de teste:

| Métrica | Resultado |
|---|---:|
| Accuracy | 0.8316 |
| Precision macro | 0.84 |
| Recall macro | 0.80 |
| F1 macro | 0.80 |

## Exemplo de utilização

```python
import joblib

model = joblib.load("intent_classifier.joblib")

text = ["Quero cancelar meu plano de saúde."]

prediction = model.predict(text)[0]
probabilities = model.predict_proba(text)[0]

print("Intenção:", prediction)
print("Probabilidade:", probabilities.max())
```

## Limitações

- Treinado com conversas sintéticas.
- Não validado com atendimentos reais de operadoras de saúde.
- Pode apresentar erros em categorias ambíguas.
- As probabilidades não foram calibradas.
- Não deve ser utilizado para decisões automatizadas de alto impacto.

## Segurança

O arquivo joblib utiliza serialização baseada em pickle.
Carregue apenas artefatos de fontes confiáveis.

## Projeto

InsightCare AI — API desenvolvida com FastAPI,
PostgreSQL, scikit-learn e Amazon Bedrock.
