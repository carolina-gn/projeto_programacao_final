# Aulas-Flask
Este repo trata das aulas de Flask com Docker + Mysql + Nginx
É base para aulas prioritariamente de frontend
As branhces estão organizadas com a evolução do conteúdo das aulas

## 📌 Introdução ao Flask e Rotas Básicas
Objetivo: Entender o básico do Flask, criar rotas, renderizar templates e passar dados para o front-end.

### Introdução
https://github.com/StorThiago/base-flask/tree/1-1_Introducao
* O que é Flask? Comparação com outros frameworks.
* Configuração do ambiente (Python, Docker Compose e Git). Download do docker compose.yaml para nosso projeto Flask
* "Hello World" no Flask.

### Rotas e Templates
https://github.com/StorThiago/base-flask/tree/1-2_Rotas-e-Templates
* Criando rotas básicas (@app.route).
* Renderização de templates com Jinja2 (usando HTML/CSS/Bootstrap).
* Passando variáveis do Python para o HTML.
* Estrutura de pastas (/templates, /static).

### Formulários Simples
https://github.com/StorThiago/base-flask/tree/1-3_Formularios-Simples-no-Flask
* Métodos GET vs POST.
* Recebendo dados de formulários (request.form).


## 📌 Integração com MySQL e CRUD Básico
Objetivo: Conectar Flask ao MySQL e operações CRUD (Create, Read, Update, Delete).

### Conexão com MySQL
* Instalação do flask-mysqldb
* Configuração da conexão (app.config).
* Executando queries simples (SELECT, INSERT).

### CRUD Básico
* Create: Formulário para adicionar dados ao BD.
* Read: Listar dados em uma tabela HTML.
* Update/Delete: Botões para editar/excluir registros.


## 📁 Estrutura de Diretórios
```
base-flask/
├── app/
│   ├── static/
│   │   ├── css/
│   │   ├── js/
│   │   └── images/
│   ├── templates/
│   ├── app.py
│   ├── wsgi.py
│   ├── Dockerfile
│   └── requirements.txt
├── db/
│   │   ├── .env
│   │   ├── init.sql
├── nginx/
│   └── nginx.conf
└── docker-compose.yaml
```

## ⚙️ Configuração

### Requisitos

- Instale Docker (https://docs.docker.com/install/)

### 🍼 Configuração inicial

- Clone este repositório em sua máquina usando o seguinte comando:
```bash
git clone git@github.com:StorThiago/base-flask
```

- Entre no repositório clonado
```bash
cd base-flask/
```

- Crie a rede `flask-network` caso não exista
```bash
docker network create --driver bridge flask-network
```

- Conecte o container do `flask-nginx_server` na rede `flask-network`
```
docker network connect flask-network flask-nginx_server
```

- No diretório raiz do projeto, execute um dos seguintes comandos para instalar as dependências e rodar a aplicação:
```bash
docker compose up --build -d
```
```bash
docker-compose down && docker-compose up --build -d  
```

- A aplicação estará ouvindo em **web.flask.localtest.me**
- As credenciais de acesso a database podem ser setadas em db/.env


