# Docker и CI для API-тестов

REST-тесты из предыдущей работы обращаются к публичному Playground API:
`https://playground.nileslabs.com/api/v1`.
Проверяют создание поста, изменение через PATCH и чтение через GET,
а также ответ 404 для отсутствующего поста. Каждый прогон использует
свой `X-Playground-Identity`. Токены не нужны.

Нужен запущенный Docker с Linux-контейнерами и доступ к интернету.
Из корня репозитория:

```bash
docker build -t api-test .
docker run --rm api-test
```

Контейнер автоматически запускает pytest и выводит результаты и HTTP-логи.
При успешных проверках возвращает код 0, при падении теста код 1.

Для запуска без Docker нужен Python 3.10+:

```bash
python -m pip install -r requirements.txt
python -m pytest
```

Конфигурация CI: `.github/workflows/ci.yml`.
При push, pull request или ручном запуске GitHub Actions получает исходники,
собирает образ и запускает его. Ошибка сборки или теста приводит к падению job.

[Запуски GitHub Actions](https://github.com/django228/MTS/actions/workflows/ci.yml).
После первого успешного запуска нужно добавить сюда ссылку на конкретный run.
