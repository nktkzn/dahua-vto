# Dahua DHI-VTO3211D-P2-S2 — Python Examples

English below • Русская версия — сразу здесь

## RU

Этот репозиторий — сборник **примеров на Python** для работы с домофонами **Dahua VILLA STATION** и линейкой **DHI‑VTO**.
На практике всё проверено на **DHI‑VTO3211D‑P2‑S2** (прошивка `DH_VTOXXXXD-G / V4.700.0000000.3.R.250331`).

**Что уже есть:**
- `examples/python/get_id.py` — двухшаговый логин (challenge → hash → session), сохранение `session.txt`.
- `examples/python/_session_util.py` — общий хелпер, который ищет/создаёт `session.txt` (спросит ввести вручную или предложит запустить `get_id.py`).
- `examples/python/add_user.py` — добавление пользователя и привязка карты (`AccessUser.insertMulti` и `AccessCard.insertMulti`).
- `examples/python/open_door.py` — удалённое открытие двери (`accessControl.openDoor`).

**Файлы данных (не коммитятся, добавлены в `.gitignore`):**
- `examples/python/credentials.txt` — IP, логин и пароль (в открытом виде).
- `examples/python/session.txt` — актуальный идентификатор сессии для повторного использования.

> ⚠️ В разных прошивках Dahua параметры и методы RPC могут отличаться. Примеры ориентированы на указанную выше прошивку;
> при другой версии возможны отличия в полях/поведении.

---

## Требования

- Python **3.10+** (работает и на 3.12).
- Пакеты: см. `examples/python/requirements.txt` (сейчас: `requests`).

Дополнительно (опционально):
- Docker (если хотите запускать примеры в контейнере).
- VS Code / любой редактор.



### Быстрый старт
```bash
cd examples/python
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python add_user.py --help  # или другой скрипт
```

---

## EN
Python examples for **Dahua VILLA STATION** and **DHI‑VTO** devices. Verified on **DHI‑VTO3211D‑P2‑S2**, firmware `DH_VTOXXXXD-G_MultiLang / V4.700.0000000.3.R.250331`.

Included:
- `get_id.py` — challenge‑based login, stores `session.txt`.
- `_session_util.py` — helper to load or create a session id (prompts to run `get_id.py` or enter manually).
- `add_user.py` — create user and assign a card.
- `open_door.py` — remote door open.

### Quick start:
```bash
cd examples/python
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python get_id.py
python add_user.py
python open_door.py
```
