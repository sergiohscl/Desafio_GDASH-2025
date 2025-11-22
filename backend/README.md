# Desafio Full-Stack – Weather Insights (Django REST + Celery + RabbitMQ)

## Link do desafio
https://github.com/GDASH-io/desafio-gdash-2025-02

Este projeto é uma base em **Django Rest Framework + Celery + RabbitMQ** estendida para atender ao desafio de:

- Coletar dados climáticos de uma API pública (ex.: **Open-Meteo**);
- Enviar esses dados periodicamente para uma **fila** (Message Broker – RabbitMQ);
- Processar os dados por um **worker** e armazenar em uma API (DRF);
- Gerar **insights de IA** a partir do histórico climático;
- Disponibilizar endpoints REST para consumo por um frontend (React, etc.), incluindo exportação **CSV/XLSX**.

---

## 1. Visão geral da arquitetura

Componentes principais:

1. **Django + DRF (backend / API)**
   - Exposição de endpoints REST.
   - Modelagem da entidade `WeatherLog` para armazenar dados de clima.
   - Geração de insights (camada de “IA” baseada nos dados históricos).

2. **Celery + RabbitMQ**
   - `fetch_weather_data` → **produtor**: coleta dados no provedor de clima e gera um JSON normalizado.
   - `store_weather_log` → **worker**: consome o JSON da fila e salva no banco.

3. **Banco de Dados (PostgreSQL ou outro configurado no projeto)**  
   - Armazena registros históricos de clima (`weather_weatherlog`).

4. **Frontend (fora deste repositório)**
   - Pode consumir endpoints `/api/weather/...` para montar dashboards, gráficos, alertas, etc.

Fluxo resumido:

1. **Celery Beat** dispara periodicamente a task `fetch_weather_data` (ex.: a cada 1 hora);
2. A task consulta a API externa de clima (Open-Meteo / OpenWeather), extrai os campos relevantes e produz um JSON normalizado;
3. Esse JSON é enviado para a fila (RabbitMQ) chamando `store_weather_log.delay(payload)`;
4. O **Celery Worker** consome a mensagem e grava em `WeatherLog` no banco;
5. O backend DRF expõe endpoints de listagem, exportação e geração de insights;
6. O frontend consome esses endpoints para exibir dashboards e relatórios.

---

## 2. Coleta e envio para a fila (Celery Producer)

A coleta de dados é feita por uma task Celery (produtor), que:

1. Busca dados em uma API de clima (ex.: **Open-Meteo**);
2. Normaliza as informações principais para um dicionário/JSON;
3. Opcionalmente grava esse JSON em arquivo para auditoria;
4. Envia o payload para outra task (`store_weather_log`) via RabbitMQ.

Exemplo conceitual (simplificado):

```python
@shared_task
def fetch_weather_data():
    params = {
        "latitude": -15.7801,
        "longitude": -47.9292,
        "hourly": "temperature_2m,relativehumidity_2m,windspeed_10m,precipitation_probability,weathercode",
        "timezone": "auto",
    }

    response = requests.get(OPEN_METEO_URL, params=params, timeout=10)
    data = response.json()

    # normalização (último registro horário)
    normalized = {...}

    # envia para worker
    store_weather_log.delay(normalized)
```

Essa task é **agendada** pelo Celery Beat (por exemplo, a cada 1 hora):

```python
from celery.schedules import crontab

app.conf.beat_schedule = {
    'fetch-weather-every-hour': {
        'task': 'weather.tasks.fetch_weather_data',
        'schedule': crontab(minute=0, hour='*'),
    },
}
```

---

## 3. Worker: armazenamento na API (WeatherLog)

A task **worker** consome o JSON da fila e persiste no banco:

```python
@shared_task
def store_weather_log(payload: dict):
    WeatherLog.objects.create(
        temperature=payload.get("temperature"),
        humidity=payload.get("humidity"),
        wind_speed=payload.get("wind_speed"),
        rain_probability=payload.get("rain_probability"),
        condition=str(payload.get("condition_code")),
        source=payload.get("source", "open-meteo"),
        raw_payload=payload.get("raw"),
    )
```

Assim, toda vez que o produtor rodar, um novo registro será salvo no histórico de clima.

---

## 4. API REST (DRF)

O app `weather` expõe um **ViewSet** que disponibiliza endpoints para:

- Listar registros de clima;
- Exportar CSV / XLSX;
- Gerar insights de IA sobre o histórico.

### 4.1. Serializer

```python
class WeatherLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = WeatherLog
        fields = [
            'id',
            'collected_at',
            'temperature',
            'humidity',
            'wind_speed',
            'condition',
            'rain_probability',
            'source',
        ]
```

### 4.2. ViewSet e endpoints

```python
class WeatherLogViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = WeatherLog.objects.all()
    serializer_class = WeatherLogSerializer

    # GET /api/weather/logs/export.csv
    @action(detail=False, methods=['get'], url_path='export.csv')
    def export_csv(self, request):
        ...

    # GET /api/weather/logs/export.xlsx
    @action(detail=False, methods=['get'], url_path='export.xlsx')
    def export_xlsx(self, request):
        ...

    # GET/POST /api/weather/logs/insights
    @action(detail=False, methods=['get', 'post'], url_path='insights')
    def insights(self, request):
        ...
```

Rotas típicas (via `DefaultRouter`):

- `GET /api/weather/logs/` → Lista paginada de logs
- `GET /api/weather/logs/{id}/` → Detalhe de um log
- `GET /api/weather/logs/export.csv/` → Exporta todos os registros em CSV
- `GET /api/weather/logs/export.xlsx/` → Exporta todos os registros em XLSX
- `GET /api/weather/logs/insights/?days=7` → Gera insights dos últimos N dias
- `POST /api/weather/logs/insights/` com corpo JSON (ex.: `{ "days": 3 }`) → Gera insights sob demanda

---

## 5. Camada de IA (Insights Climáticos)

Os insights de IA são gerados a partir dos dados históricos.  
Neste projeto, há uma função `generate_insights_text` que:

1. Recebe uma lista de registros serializados (temperatura, umidade, probabilidade de chuva, etc.);
2. Calcula estatísticas simples (média, máxima, mínima);
3. Produz um texto em linguagem natural com recomendações/observações.

Exemplo (simplificado):

```python
def generate_insights_text(data: list[dict]) -> str:
    if not data:
        return "Ainda não há dados suficientes para gerar insights climáticos."

    temps = [d['temperature'] for d in data if d['temperature'] is not None]
    hums = [d['humidity'] for d in data if d['humidity'] is not None]
    rains = [d['rain_probability'] for d in data if d['rain_probability'] is not None]

    # cálculo de médias, mín/máx e construção de texto...
```

Essa camada pode ser evoluída para:

- Integrar um modelo de **IA generativa** (OpenAI, etc.), enviando o resumo dos dados e recebendo um texto mais elaborado;
- Gerar alertas específicos (ondas de calor, baixa umidade, alta probabilidade de chuva, etc.);
- Agendar a geração de insights automaticamente sempre que novos dados forem inseridos.

---

## 6. Exportação CSV e XLSX

Para facilitar análise em ferramentas externas (Excel, Power BI, etc.), foram adicionados dois endpoints:

- `GET /api/weather/logs/export.csv/`
- `GET /api/weather/logs/export.xlsx/`

A geração de XLSX utiliza a biblioteca **openpyxl** (ver `weather/utils.py`).

Certifique-se de ter a dependência no `requirements.txt`:

```txt
openpyxl>=3.1.0
```

---

## 7. Execução com Docker Compose

### Pré-requisitos

- **Docker** e **Docker Compose** instalados.

### Passos

1. Ajuste variáveis de ambiente no arquivo `.env` (se houver), incluindo:
   - Configuração de banco de dados;
   - URL do broker Celery (ex.: `amqp://user:pass@rabbitmq:5672//`).

2. Suba os serviços:

```bash
docker-compose up --build
```

Serviços esperados:

- `backend` – aplicação Django/DRF;
- `rabbitmq` – broker de mensagens;
- `celery_worker` – worker que processa tasks;
- `celery_beat` – scheduler para tasks periódicas.

3. Acesse a API em:

```text
http://localhost:8000/api/weather/logs/
```

> A porta pode variar de acordo com o `docker-compose.yml`.

---

## 8. Execução local (sem Docker)

1. Crie e ative o ambiente virtual:

```bash
python -m venv .venv
source .venv/bin/activate  # Linux/macOS
# ou
.\.venv\Scriptsctivate   # Windows
```

2. Instale dependências:

```bash
pip install -r requirements.txt
```

3. Execute migrações:

```bash
python manage.py migrate
```

4. Inicie o servidor Django:

```bash
python manage.py runserver
```

5. Inicie o Celery Worker e o Beat (ajuste `<nome_projeto>` para o módulo principal do Django):

```bash
celery -A <nome_projeto> worker -l info
celery -A <nome_projeto> beat -l info
```

---

## 9. Usuários e autenticação

O desafio pede um **CRUD de usuários com autenticação e usuário padrão**.  
O projeto base pode trazer um módulo de usuários (ex.: `users`, `accounts`), com autenticação via DRF (Token, Session ou JWT).

Sugestão de uso:

- Criar um superusuário para acesso ao admin:

```bash
python manage.py createsuperuser
```

- Autenticar via DRF (Token/JWT) nos endpoints de clima, caso necessário.

> A proteção dos endpoints (`IsAuthenticated`, `DjangoModelPermissions`, etc.) pode ser configurada via `DEFAULT_PERMISSION_CLASSES` no `settings.py`.

---

## 10. Testando rapidamente

1. Suba o projeto (Docker ou local);
2. Aguarde alguns minutos até o primeiro ciclo do Celery Beat (ou force a execução da task `fetch_weather_data` manualmente);
3. Acesse:

   - `GET /api/weather/logs/` → deve retornar uma lista com registros climáticos;
   - `GET /api/weather/logs/insights/?days=7` → retorna um texto com insights dos últimos 7 dias;
   - `GET /api/weather/logs/export.csv/` → baixa um CSV com o histórico;
   - `GET /api/weather/logs/export.xlsx/` → baixa um XLSX com o histórico.

---

## 11. Rodando scripts para popular banco de dados

```bash
python manage.py seed_weather_logs
```

```bash
python manage.py seed_weather_logs --days 10 --step 1
```

---

## 12. Próximos passos / extensões

- Integrar uma **camada de IA generativa** (LLM) para enriquecer os insights;
- Adicionar filtros avançados (por intervalo de datas, horário, fonte de dados);
- Configurar alertas (ex.: enviar notificação quando temperatura média de 24h ultrapassar X graus);
- Persistir insights em uma coleção própria (ex.: `weather_insights`) e exibi-los no dashboard.

---

Este README descreve a visão geral e os componentes necessários para que o projeto atenda ao desafio de integração entre **dados reais de clima**, **fila (RabbitMQ)**, **API em DRF** e **camada de IA**.
