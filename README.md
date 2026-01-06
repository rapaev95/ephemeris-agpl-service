# ephemeris-agpl-service

HTTP сервис для астрономических расчётов на основе Swiss Ephemeris (AGPL-3.0).

## Описание

Сервис предоставляет REST API для расчёта позиций планет, домов и времени Design (Human Design) с использованием Swiss Ephemeris через Python binding (pyswisseph).

## Локальный запуск

### Требования

- Python 3.11 или 3.12
- Swiss Ephemeris data files (SE_* файлы)

### Установка

```bash
# Клонировать репозиторий
git clone https://github.com/rapaev95/ephemeris-agpl-service.git
cd ephemeris-agpl-service

# Установить зависимости
pip install -e .

# Скачать Swiss Ephemeris data files в ./sweph/
# (см. инструкции на https://www.astro.com/swisseph/swephinfo_e.htm)
```

### Настройка переменных окружения

Создайте `.env` файл:

```bash
AGPL_SERVICE_API_KEYS=your-secret-key-1,your-secret-key-2
SWEPH_PATH=./sweph
PORT=8000
```

### Запуск

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

Сервис будет доступен на `http://localhost:8000`

## Docker

### Сборка образа

```bash
docker build -t ephemeris-agpl-service:latest .
```

### Запуск контейнера

```bash
docker run -p 8000:8000 \
  -e AGPL_SERVICE_API_KEYS=your-secret-key \
  -e SWEPH_PATH=/app/sweph \
  ephemeris-agpl-service:latest
```

## API Endpoints

### Meta (без авторизации)

- `GET /health` - Health check
- `GET /v1/version` - Информация о версии и сборке
- `GET /v1/source` - Информация об исходном коде (repo, tag, commit)

### Вычислительные (требуют авторизации)

Все вычислительные endpoints требуют заголовок:
```
Authorization: Bearer <your-api-key>
```

- `POST /v1/positions` - Расчёт позиций планет
- `POST /v1/houses` - Расчёт домов и углов
- `POST /v1/design-time` - Поиск времени Design для Human Design

Подробная документация API доступна в `/docs` (Swagger UI) после запуска сервиса.

## Как получить исходники

Исходный код доступен в публичном репозитории:

- **Репозиторий:** https://github.com/rapaev95/ephemeris-agpl-service
- **Releases:** https://github.com/rapaev95/ephemeris-agpl-service/releases

Каждый ответ от вычислительных endpoints содержит заголовок `X-AGPL-Source` с информацией о версии исходного кода.

## Лицензия

Этот проект распространяется под лицензией **AGPL-3.0**.

См. файл [LICENSE](LICENSE) для полного текста лицензии.

## Third-party notices

См. файл [NOTICE.md](NOTICE.md) для информации о сторонних библиотеках и их лицензиях.

## Разработка

### Установка зависимостей для разработки

```bash
pip install -e ".[dev]"
```

### Запуск тестов

```bash
pytest tests/
```

### Линтинг

```bash
ruff check .
black --check .
```

## Changelog

См. [CHANGELOG.md](CHANGELOG.md) для истории изменений.
