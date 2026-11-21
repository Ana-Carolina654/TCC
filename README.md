# TCC

Código do Projeto de Conclusão de Curso referente ao artigo **"Técnicas de Machine Learning na Identificação do Transtorno do Espectro Autista em Adultos"**.

## Estrutura do projeto

O repositório está organizado da seguinte maneira:

```text
TCC/
├── data/               # Dados brutos
│   └── xai/            # Resultados das análises realizadas pelo SHAP
├── experiment/         # Classes orquestradoras do projeto
├── mlflow_log/         # Logs do MLflow
├── mlruns/             # Logs do MLflow
├── models/             # Classes de implementação dos modelos
├── pipeline/           # Pipeline de limpeza dos dados
├── strategies/         # Definição das classes abstratas do projeto
└── README.md           # Documentação do projeto
```

## Como executar o projeto

Para executar o projeto, abra o terminal na pasta raiz do repositório e execute o seguinte comando:

```bash
python -m experiment.main
```
