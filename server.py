from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import httpx

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

SUPPORTED_CURRENCIES = ["USD", "EUR", "RUB", "GBP", "JPY", "CNY"]
API_URL = "https://open.er-api.com/v6/latest/USD"

@app.get("/convert")
async def convert_currency(amount: float, from_currency: str, to_currency: str):
    from_curr = from_currency.upper()
    to_curr = to_currency.upper()
    
    if amount < 0:
        raise HTTPException(status_code=400, detail="Сумм отрицательный хал йиш яц")
    
    if from_curr not in SUPPORTED_CURRENCIES:
        raise HTTPException(status_code=400, detail=f"Неподдерживаемая валюта: {from_curr}")
    
    if to_curr not in SUPPORTED_CURRENCIES:
        raise HTTPException(status_code=400, detail=f"Неподдерживаемая валюта: {to_curr}")

    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(API_URL, timeout=10.0)
            if response.status_code != 200:
                raise HTTPException(status_code=503, detail="Ошибка API курсов валют")
            
            data = response.json()
            rates = data.get("rates")
            
            if from_curr not in rates or to_curr not in rates:
                raise HTTPException(status_code=503, detail="Валют яц в ответе API")

    except httpx.RequestError:
        raise HTTPException(status_code=503, detail="Соединени яц")

    rate_from = rates[from_curr]
    rate_to = rates[to_curr]
    
    converted_amount = (amount / rate_from) * rate_to
    exchange_rate = rate_to / rate_from
    
    return {
        "amount": amount,
        "from_currency": from_curr,
        "to_currency": to_curr,
        "converted_amount": round(converted_amount, 2),
        "rate": round(exchange_rate, 4),
        "source": "live_api"
    }
