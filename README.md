# Практическая работа №1 — вариант 1

Дисциплина: «Прикладная разработка серверных частей веб-приложений на языке Питон».

## Задание

Реализован прототип веб-приложения с удалённым вызовом процедур по TCP. Данные хранятся только в оперативной памяти и представлены кортежами. Реализованы сущности Actor, Instruction и Response, операции CRUD, реляционная выборка последних инструкций, TCP RPC, клиент RPC и Model-Based Testing на `hypothesis`.

## Структура

```text
src/model.py       # модель слоя доступа к данным
src/rpc.py         # TCP RPC сервер и клиент
src/server.py      # запуск сервера
src/repl.py        # REPL модели
src/demo.py        # демонстрация RPC

tests/test_mbt.py  # MBT-тесты
requirements.txt
run.bat
Makefile
```

## Сущности

- Actor: `(key, time, ip, user_agent)`
- Instruction: `(key, time, content, actor, status)`
- Response: `(key, time, output, status, failure, instruction)`

Все записи в памяти представлены кортежами.

## 13 функций модели

1. `create_actor`
2. `delete_actor`
3. `get_all_actors`
4. `update_actor`
5. `create_instruction`
6. `delete_instruction`
7. `get_all_instructions`
8. `update_instruction`
9. `create_response`
10. `delete_response`
11. `get_all_responses`
12. `update_response`
13. `select_recent_instructions`

## RPC

Заголовок запроса и ответа: версия протокола — 1 байт, код операции — 1 байт, размер JSON-тела — 5 байт. Все целочисленные поля заголовка передаются в порядке от старшего байта к младшему. JSON-кодировка — UTF-8.

## Запуск

### Установка

```bash
python -m venv .venv
.venv\\Scripts\\activate
python -m pip install -r requirements.txt
```

### Демонстрация

```bash
python -m src.demo
```

### REPL

```bash
python -c "from src.repl import repl; repl()"
```

### Сервер

```bash
python -m src.server
```

## Тестирование MBT

```bash
python -m coverage run --branch -m pytest tests
python -m coverage report -m
```

Тесты используют `RuleBasedStateMachine` из `hypothesis` и сравнивают состояние удалённого RPC с эталонной моделью.

## Git-коммиты

Рекомендуемые сообщения:

```text
feat(model): implement variant 1 data model
feat(rpc): implement tcp rpc server and client
feat(test): add hypothesis model based tests
```
