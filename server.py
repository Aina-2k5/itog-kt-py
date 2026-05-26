from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List
import httpx

app = FastAPI(title="Конвертер валют", version="1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

class ConversionResponse(BaseModel):
    amount: float
    from_currency: str
    to_currency: str
    converted_amount: float
    rate: float
    source: str

class ErrorResponse(BaseModel):
    detail: str

class CurrenciesResponse(BaseModel):
    currencies: List[str]

SUPPORTED_CURRENCIES = ["USD", "EUR", "RUB", "GBP", "JPY", "CNY"]

FIXED_RATES = {
    "USD": 1.0,
    "EUR": 0.92,
    "RUB": 92.5,
    "GBP": 0.79,
    "JPY": 157.3,
    "CNY": 7.24
}

API_URL = "https://api.exchangerate-api.com/v4/latest/USD"


@app.get("/convert", 
         response_model=ConversionResponse,
         responses={400: {"model": ErrorResponse}},
         summary="Конвертация валют",
         description="Конвертирует сумму из одной валюты в другую")
async def convert_currency(
    amount: float,
    from_currency: str,
    to_currency: str
):
    from_currency = from_currency.upper()
    to_currency = to_currency.upper()
    
    if amount < 0:
        raise HTTPException(status_code=400, detail="Сумма не может быть отрицательной")
    
    if from_currency not in SUPPORTED_CURRENCIES:
        raise HTTPException(status_code=400, detail=f"Неподдерживаемая валюта: {from_currency}")
    
    if to_currency not in SUPPORTED_CURRENCIES:
        raise HTTPException(status_code=400, detail=f"Неподдерживаемая валюта: {to_currency}")
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(API_URL, timeout=10.0)
            if response.status_code == 200:
                data = response.json()
                rates = data.get("rates", FIXED_RATES)
            else:
                rates = FIXED_RATES
    except Exception:
        rates = FIXED_RATES
    
    amount_in_usd = amount / rates[from_currency]
    converted_amount = amount_in_usd * rates[to_currency]
    exchange_rate = rates[to_currency] / rates[from_currency]
    
    return {
        "amount": amount,
        "from_currency": from_currency,
        "to_currency": to_currency,
        "converted_amount": round(converted_amount, 2),
        "rate": round(exchange_rate, 4),
        "source": "live" if rates != FIXED_RATES else "fixed"
    }


@app.get("/currencies", 
         response_model=CurrenciesResponse,
         summary="Список валют",
         description="Возвращает список поддерживаемых валют")
async def get_supported_currencies():
    return {"currencies": SUPPORTED_CURRENCIES}