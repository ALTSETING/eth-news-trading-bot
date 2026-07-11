# ETH News Trading Bot — starter

Бот:
- читає Ethereum-новини через Google News RSS;
- перевіряє нові записи кожні 60 секунд;
- аналізує лише нові новини через OpenAI;
- класифікує їх за 12 категоріями;
- ставить оцінку впливу від -100 до 100;
- формує PAPER-рішення LONG / SHORT / NO_TRADE;
- щосекунди оновлює інформацію в терміналі;
- зберігає результати в SQLite.

## Запуск Windows

```powershell
cd eth_news_trading_bot
py -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
```

Відкрий `.env` і встав свій `OPENAI_API_KEY`, потім:

```powershell
python main.py
```

## Увага

Це стартова PAPER-версія. Вона не відкриває реальні угоди.
Перед підключенням біржі потрібні backtest, контроль ризику, стоп-лоси,
ліміти втрат і захист API-ключів.
