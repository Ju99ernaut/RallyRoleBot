import data
import rally_api

from typing import List, Optional
from fastapi import APIRouter, Query
from .models import CoinPrice


router = APIRouter(prefix="/coins", tags=["coins"])


@router.get("/{coin}/price", response_model=CoinPrice)
async def read_price(coin: str, include_24hr_change: Optional[bool] = False):
    price = rally_api.get_current_price(coin)
    if not include_24hr_change:
        return {"coinKind": coin, "priceInUsd": price["priceInUsd"]}
    last_24hr = data.get_coin_prices(coin, limit=24)
    percentage_24h_change = (
        (float(price["priceInUsd"]) - float(last_24hr[-1]["price"])) / float(last_24hr[-1]["price"])
    ) * 100
    return {
        "coinKind": coin,
        "priceInUsd": str(price["priceInUsd"]),
        "usd_24h_change": str(percentage_24h_change),
    }


@router.get("/{coin}/historical_price", response_model=List[CoinPrice])
async def read_prices(
    coin: str,
    limit: Optional[int] = Query(
        None,
        title="Query string",
        description="Maximum number of data points to return",
    ),
):
    return [prices for prices in data.get_coin_prices(coin, limit)]
