# 📦 FreteFácil

Aplicação web desenvolvida com **Python** e **Flask** que permite calcular o valor do frete com base no CEP de origem, CEP de destino, dimensões e peso do objeto a ser transportado.

---

## 📋 Sobre o Projeto

O usuário informa os dados do envio e recebe o valor estimado do frete de forma simples e rápida. O sistema calcula automaticamente o **peso cubado**, aplica taxas como GRIS, ADEME e TDA, e ainda suporta a opção de **entrega expressa**. Os cálculos ficam salvos no **histórico** da aplicação para consulta posterior.

Desenvolvido como trabalho acadêmico do curso de **Análise e Desenvolvimento de Sistemas (ADS)**.

---

## ⚙️ Tecnologias Utilizadas

- [Python](https://www.python.org/)
- [Flask](https://flask.palletsprojects.com/)
- HTML5 + CSS3

---

## 🚀 Como Instalar e Executar

### Pré-requisitos

- **Python** instalado — disponível na [Microsoft Store](https://apps.microsoft.com/store/search/python) ou no site oficial [python.org](https://www.python.org/downloads/)

### Passo a Passo

1. **Clone o repositório**
   ```bash
   git clone https://github.com/seu-usuario/fretefacil.git
   cd fretefacil/Calculo-Frete-V2
   ```

2. **Instale as dependências**
   ```bash
   pip install flask
   ```
   > Ou instale todas as dependências de uma vez:
   ```bash
   pip install -r requirements.txt
   ```

3. **Execute a aplicação**
   ```bash
   python app.py
   ```

4. **Acesse no navegador**
   ```
   http://localhost:5000
   ```

---

## 🖥️ Como Usar

1. Preencha os campos na tela principal:
   - **CEP de Origem** e **CEP de Destino**
   - **Peso (kg)**, **Largura**, **Altura** e **Comprimento** (em cm)
   - **Valor do Produto** — utilizado para calcular o GRIS
   - Ative o toggle **Entrega Expressa** se desejar

2. Clique no botão **Calcular Frete**

3. O painel de resultados exibirá:
   - **Total estimado** do frete e prazo de entrega
   - **Região de origem e destino** identificadas pelo CEP
   - **Peso real** e **Peso cubado** calculados automaticamente
   - **Composição do frete** com detalhamento de cada taxa (Frete peso, Taxa interestadual, ADEME, TDA)

4. Os cálculos realizados ficam salvos no **Histórico**, com opção de limpá-lo

---

## 📁 Estrutura de Pastas

```
.
├── .vscode
│   └── settings.json
│
└── Calculo-Frete-V2
    ├── static
    │   └── style.css
    ├── templates
    │   └── index.html
    ├── app.py
    ├── history.json
    ├── README.md
    └── requirements.txt
```

---

## 📄 Licença

Este projeto está sob a licença **MIT**. Consulte o arquivo [LICENSE](LICENSE) para mais detalhes.

---

## 👥 Equipe

| Nome |
|------|
| João Guilherme Borges Lins |
| Ana Cristina Moreira Silva |
| Guilherme Vasconcelos Duarte |
| Luis Miguel de Sousa de Castro |
| Pedro Jonata Damasceno do Nascimento |

---

> Projeto acadêmico — Curso de Análise e Desenvolvimento de Sistemas (ADS)