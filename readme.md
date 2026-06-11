# VagaBot - Sistema de Alertas de Vagas

## Resumo do Projeto
O **VagaBot** é uma aplicação web full-stack desenvolvida como atividade acadêmica. O sistema atua como um gerenciador e notificador de vagas de emprego/estágio, cobrindo todas as operações CRUD. Ele possui uma interface web dinâmica e moderna, um **Chatbot híbrido** (que une consultas determinísticas ao banco e Inteligência Artificial Generativa via Google Gemini para perguntas abertas), e utiliza **Automação RPA** para disparar notificações reais via e-mail (Gmail) e WhatsApp Web (via navegador Firefox) buscando os dados dos candidatos diretamente do banco de dados.

## Tecnologias Utilizadas
* **Backend:** Python com Flask (API REST) e Flask-CORS.
* **Frontend:** HTML5, CSS3 moderno (UI com Glassmorphism) e JavaScript (Vanilla), consumindo a API nativamente via `fetch`.
* **Banco de Dados:** MongoDB (NoSQL) integrado via `pymongo`.
* **Inteligência Artificial:** `google-generativeai` (Integração com a rede neural do Google Gemini).
* **Automação (RPA):**
  * `selenium` (controlando o **Firefox** para o WhatsApp Web).
  * `smtplib` nativo do Python para disparos de e-mail via SMTP do Gmail.

---

## Passo a Passo para rodar o Projeto

### 1. Pré-requisitos
Certifique-se de ter instalado em sua máquina:
* **Python** (versão 3.8 ou superior).
* **MongoDB** (Serviço rodando localmente na porta padrão `27017`).
* Navegador **Mozilla Firefox** (necessário para a automação do WhatsApp).
* Uma chave de API gratuita do Google AI Studio

### 2. Instalação das Dependências
Abra o terminal na pasta raiz do projeto e instale as bibliotecas Python necessárias executando:
```bash
pip install flask pymongo flask-cors selenium google-generativeai
```
### 3. Configurações Prévias (RPA e IA)

Antes de executar o projeto, é necessário configurar as credenciais:

1. Configuração do E-mail (RPA):
Abra o arquivo rpa.py. Na função enviar_email(), substitua EMAIL_ORIGEM pelo seu e-mail do Gmail e insira sua Senha de Aplicativo de 16 dígitos (gerada nas configurações de segurança em duas etapas do Google).

2. Configuração da Inteligência Artificial:
Abra o arquivo app.py. Na seção de configuração da IA (linha 11), insira sua chave gerada no Google AI Studio dentro das aspas em genai.configure(api_key=""). O código buscará automaticamente o melhor modelo de texto disponível.

### 4. Executando a Aplicação

1. Inicie o Banco de Dados: Garanta que o serviço do MongoDB está ativo (net start MongoDB no Windows ou via interface do MongoDB Compass).

2. Inicie o Servidor Backend: No terminal, dentro da pasta do projeto, execute:
```bash
python app.py
```
3. Acesse a Aplicação: O Flask foi configurado para servir a interface principal. Abra o seu navegador e acesse: http://127.0.0.1:5000
