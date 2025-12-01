# Desafio Full-Stack – Weather Insights ☁️

## Link do desafio
https://github.com/GDASH-io/desafio-gdash-2025-02

Backend em **Django REST + Celery + RabbitMQ** que:

- Coleta dados de clima na API **OpenWeather**;
- Salva os registros em `WeatherLog`;
- Gera **insights de IA** em `WeatherInsight`;
- Disponibiliza endpoints para um dashboard (React, etc).

---

## 1. Como clonar e subir com Docker

```bash
# 1. Clonar o repositório
git clone https://github.com/sergiohscl/Desafio_GDASH-2025
cd desafio_gdash_2025/backend

    # 1.1 Criar virtual venv.

        python3 -m venv venv
        . venv/Scripts/activate

    # 1.2 Instalar as dependências no projeto.

        pip install -r requirements.txt

    # 1.3 Roda o banco de dados e cria super usuario.

        python manage.py migrate
        python manage.py createsuperuser

    # 1.4 Rodar o sistema e acessar o admin.

        python manage.py runserver (`http://localhost:8000/admin`)

    #  1.5 Documentação das API's (swagger).

      (`http://localhost:8000/swagger/`)

# 2. Criar o arquivo de variáveis de ambiente
cp .env.example .env
# editar .env e preencher:
# - DB (se necessário)
# - RABBITMQ (CELERY_BROKER_URL)
# - OPENWEATHER_API_KEY
# - OPENAI_API_KEY (opcional, para IA)

# 3. Subir tudo com Docker Compose
docker compose up -d --build
```

Serviços principais:

- `web`   → Django + DRF (`http://localhost:8000/`)
- `rabbitmq` → Broker de mensagens (painel em `http://localhost:15672/`)
- `celery` → Worker que processa tasks
- `beat`  → Scheduler (dispara as tasks periódicas)

### Comandos úteis

```bash
# Parar tudo
docker compose down

# Ver logs gerais
docker compose logs -f

# Ver logs só do worker Celery
docker compose logs -f celery

# Ver logs só do beat
docker compose logs -f beat

# (Opcional) aplicar migrações manualmente dentro do container web
docker compose exec web python manage.py migrate

# Criar superusuário
docker compose exec web python manage.py createsuperuser
```

---

## 2. Fluxo simples de dados

1. **Coleta periódica (Celery Beat → Celery Worker)**  
   - A cada **1 hora** o `beat` dispara a task `collect_weather_task`.
   - A task chama a API do clima (OpenWeather) com latitude/longitude configuradas.
   - O resultado é normalizado e salvo em `WeatherLog` (incluindo campo `raw` com o JSON original).

2. **Geração de insights (IA + resumo numérico)**  
   - A cada **2 horas** o `beat` dispara `generate_insights_task`.
   - A task lê os últimos registros (ex.: últimas 24h), calcula médias/máx/mín
     e gera um texto:
     - primeiro usando uma regra numérica;
     - depois, opcionalmente, refinando o texto via OpenAI (`OPENAI_API_KEY`).
   - O resultado é salvo em `WeatherInsight`.

3. **Consumo pela API**  
   - O frontend (React) consome os endpoints:
     - lista de registros;
     - exportações CSV/XLSX;
     - último insight;
     - geração sob demanda de novo insight;
     - coleta de clima para outra cidade.

---

## 3. Endpoints principais

Base: `http://localhost:8000/api/v1`

### Logs de clima

- `GET  /weather/logs/`  
  Lista registros (`WeatherLog`) com paginação.

- `POST /weather/logs/`  
  Cria um registro manualmente (caso outro serviço queira publicar dados de clima).

- `GET  /weather/logs/export.csv/`  
  Exporta todos os logs em CSV.

- `GET  /weather/logs/export.xlsx/`  
  Exporta todos os logs em XLSX.

- `POST /weather/logs/fetch-city/`  
  Coleta clima **em tempo real** de uma cidade informada e salva em `WeatherLog`.  
  Exemplo de corpo:

  ```json
  {
    "city_name": "São Paulo"
  }
  ```

### Insights

- `GET  /weather/logs/insights/`  
  Lista todos os insights (`WeatherInsight`).

- `GET  /weather/logs/insights/latest/`  
  Retorna o insight mais recente.

- `POST /weather/logs/insights/`  
  Gera insight sob demanda (usa Celery) a partir dos últimos `hours`:

  ```json
  {
    "hours": 24,
    "city": "Brasília"   // opcional, para focar em uma cidade
  }
  ```

Resposta (202 Accepted) inclui o `task_id` da task Celery.

---

## 4. Resumo rápido da arquitetura

- **Django + DRF**  
  - Modelos `WeatherLog` e `WeatherInsight`;
  - ViewSets com endpoints REST;
  - Exportação CSV/XLSX.

- **Celery + RabbitMQ**  
  - `collect_weather_task` → busca clima e grava log;
  - `generate_insights_task` → gera texto de insight;
  - **Beat** agenda essas tasks (coleta 1h / insight 2h).

- **APIs externas**  
  - **OpenWeather** → clima atual (usando lat/lon ou nome da cidade);
  - **OpenAI** (opcional) → deixa o texto dos insights mais natural.

Com isso, você tem um pipeline completo:  
**dados reais de clima → fila → banco → IA → endpoints para o dashboard.**


---

## 5. Frontend – Weather Dashboard (React + Vite + Tailwind + shadcn/ui)

O frontend deste desafio foi desenvolvido em **React + TypeScript**, utilizando:

- **Vite** como bundler;
- **Tailwind CSS** para estilização;
- **shadcn/ui** para componentes reutilizáveis (Button, Card, Table, Dialog, Toast, etc.);
- Integração direta com a API do backend (`/api/v1/...`) usando **axios**;
- Autenticação por **Token** (compatível com o backend em Django REST).

### 5.1. Principais funcionalidades

- **Autenticação**
  - Tela de **Login** (usuário + senha, com feedback de erro);
  - Tela de **Cadastro** (quando necessário);
  - Armazena o token no `localStorage` e configura o `Authorization: Token ...` nos serviços.

- **Weather Dashboard (Home)**
  - Exibe um **resumo do clima mais recente** (cards com temperatura, umidade, pressão, vento, condição etc.);
  - Renderiza um **gráfico de temperatura ao longo do tempo** (`WeatherTemperatureChart`);
  - Exibe os registros em uma **tabela paginada** (`WeatherTable`);
  - Permite **exportar logs** em CSV/XLSX;
  - Mostra **insights de IA** no card `WeatherInsightsCard`:
    - Ao carregar a tela, traz o **último insight** (`/weather/logs/insights/latest/`);
    - Ao selecionar uma linha na tabela, busca o insight correspondente àquela cidade;
    - Ao gerar clima para uma cidade, dispara também a geração de um novo insight.

- **Seleção de cidade (Dashboard)**
  - O componente `AppHeader` exibe a cidade atual e oferece um **modal "Gerar clima"**:
    - Select com todas as **capitais do Brasil** (`BRAZIL_CAPITALS`);
    - Ao confirmar, chama:
      - `POST /weather/logs/fetch-city/` → coleta clima em tempo real para a cidade;
      - `POST /weather/logs/insights/`   → dispara geração de insight para a cidade;
      - Em seguida, atualiza tabela, gráfico e card de insights.

- **Relatórios**
  - **Listar usuários**
    - Página `UsersListPage` acessível via menu **Relatórios → Listar usuários** no header;
    - Consome:
      - `GET    /api/v1/users/`  → lista de usuários;
      - `DELETE /api/v1/users/<id>/` → remove usuário (somente admin; backend valida);
    - Tabela com:
      - Avatar,
      - Nome de usuário,
      - E-mail,
      - ID,
      - Ação (botão/ícone para remover usuário);
    - Feedback visual com `toast` para sucesso/erro.

  - **Listar Star Wars (API pública – SWAPI)**
    - Página `StarWarsPage` acessível via **Relatórios → Listar Star Wars**;
    - Consome a API pública **SWAPI** (`https://swapi.dev/api/people/`) com paginação;
    - Lista personagens com:
      - Nome,
      - Altura,
      - Peso,
      - Gênero,
      - Ano de nascimento,
      - Cores (cabelo, pele, olhos);
    - Cada personagem é exibido em um `StarWarsCard` (componente de card).

---

### 5.2. Estrutura simplificada do frontend

```bash
frontend/
├── src/
│   ├── components/
│   │   ├── layout/
│   │   │   ├── AppHeader.tsx
│   │   │   └── ...
│   │   ├── ui/               # componentes shadcn/ui
│   │   └── star-wars/
│   │       └── StarWarsCard.tsx
│   ├── interfaces/
│   │   ├── auth.ts           # tipos de usuário, login, etc.
│   │   ├── weather.ts        # tipos de WeatherLog, WeatherInsight
│   │   └── starWars.ts       # tipos da SWAPI
│   ├── pages/
│   │   ├── LoginPage.tsx
│   │   ├── RegisterPage.tsx
│   │   ├── HomePage.tsx      # Dashboard de clima
│   │   ├── UsersListPage.tsx # Relatório de usuários
│   │   └── StarWarsPage.tsx  # Relatório SWAPI
│   ├── services/
│   │   ├── authService.ts    # login, logout, listar/deletar usuários
│   │   ├── weatherService.ts # integrações com /weather/logs e insights
│   │   └── starWarsService.ts# chamadas à SWAPI
│   ├── config/
│   │   └── api.ts            # API_BASE_URL do backend
│   └── main.tsx / App.tsx    # rotas, provider de Toast etc.
├── Dockerfile
├── docker-compose.yml (opcional, apenas frontend)
└── README.md
```

---

### 5.3. Como rodar o frontend em modo desenvolvimento

Dentro da pasta `frontend/`:

```bash
# 1. Instalar dependências
npm install

# 2. Rodar em modo dev (Vite)
npm run dev
```

Por padrão, o Vite sobe em `http://localhost:5173`.

O arquivo `src/config/api.ts` deve apontar para o backend Django, por exemplo:

```ts
export const API_BASE_URL = "http://localhost:8000";
```

Se preferir usar variáveis de ambiente, pode configurar `VITE_API_BASE_URL` e ler com `import.meta.env.VITE_API_BASE_URL`.

---

### 5.4. Rodando o frontend com Docker

Na pasta `frontend/`, você pode usar o `Dockerfile` criado para desenvolvimento:

```bash
# build da imagem
docker build -t weather-frontend .

# sobe o container em modo dev
docker run --name weather_frontend   -p 5173:5173   weather-frontend
```

Ou usando um `docker-compose.yml` simples (dentro de `frontend/`):

```yaml
version: "3.9"

services:
  frontend:
    build: .
    container_name: weather_frontend
    ports:
      - "5173:5173"
    volumes:
      - .:/app
      - /app/node_modules
    command: npm run dev -- --host 0.0.0.0 --port 5173
    environment:
      - VITE_API_BASE_URL=http://localhost:8000
```

Então:

```bash
docker compose up --build
```

Frontend disponível em: `http://localhost:5173`.

---

### 5.5. Autenticação no frontend

- Após login bem-sucedido, o frontend:
  - Armazena o token de autenticação no `localStorage` (chave `authToken`);
  - Configura o interceptor do `axios` para enviar `Authorization: Token <token>` em todas as requisições.
- O `authService` expõe utilitários como:
  - `login`, `logout`, `getAuthUser`, `listUsers`, `deleteUser` etc.
- Páginas protegidas (Home, Relatórios) assumem que o backend está validando o token.

---

### 5.6. Navegação principal

- **`/`** → Login
- **`/register`** → Cadastro de usuário (opcional)
- **`/home`** → Weather Dashboard (clima + insights)
- **`/reports/users`** → Relatório: Listar usuários
- **`/reports/star-wars`** → Relatório: Listar personagens de Star Wars (SWAPI)

O componente `AppHeader` oferece navegação via:

- Logo **Weather Dashboard** (volta para `/home`);
- Menu **Relatórios** com:
  - **Listar usuários** → `/reports/users`
  - **Listar Star Wars** → `/reports/star-wars`
- Botão **Gerar clima** → abre modal para escolher a cidade e atualizar o dashboard.

---

### 5.7. Próximos passos / possíveis melhorias

- Exibir na UI quando o usuário atual é admin vs. comum;
- Permitir filtros por cidade/intervalo de datas diretamente na tabela de clima;
- Adicionar gráficos adicionais (chuva, vento, etc.) usando as mesmas bases do `WeatherLog`;
- Salvar preferências de cidade do usuário no perfil (backend) para carregar automaticamente.

### 5.8. Link Video Apresentação

  https://youtu.be/XrshD3lISaA