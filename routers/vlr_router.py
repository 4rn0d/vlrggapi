from fastapi import APIRouter, Request
from api.scrape import Vlr, Sheep
from slowapi import Limiter
from slowapi.util import get_remote_address

router = APIRouter()
limiter = Limiter(key_func=get_remote_address)
vlr = Vlr()
sheep = Sheep()


# region VLR API
@router.get("/vlrNews", tags=["vlr"])
@limiter.limit("250/minute")
async def VLR_news(request: Request):
    return vlr.vlr_news()


@router.get("/vlrNews/content/", tags=["vlr"])
@limiter.limit("250/minute")
async def VLR_news(request: Request, article_url: str):
    return vlr.vlr_articles(article_url)


@router.get("/stats/{region}/{timespan}", tags=["vlr"])
@limiter.limit("250/minute")
async def VLR_stats(region, timespan, request: Request):
    """
    region shortnames:\n
        "na": "north-america",\n
        "eu": "europe",\n
        "ap": "asia-pacific",\n
        "sa": "latin-america",\n
        "jp": "japan",\n
        "oce": "oceania",\n
        "mn": "mena",\n

    timespan:\n
        "30": 30 days,\n
        "60": 60 days,\n
        "90": 90 days,\n
    """
    return vlr.vlr_stats(region, timespan)


@router.get("/rankings/{region}", tags=["vlr"])
@limiter.limit("250/minute")
async def VLR_ranks(region, request: Request):
    """
    region shortnames:\n
        "na": "north-america",\n
        "eu": "europe",\n
        "ap": "asia-pacific",\n
        "la": "latin-america",\n
        "la-s": "la-s",\n
        "la-n": "la-n",\n
        "oce": "oceania",\n
        "kr": "korea",\n
        "mn": "mena",\n
        "gc": "game-changers",\n
        "br": "Brazil",\n
        "cn": "china",\n
    """
    return vlr.vlr_rankings(region)


@router.get("/match", tags=["vlr"])
@limiter.limit("250/minute")
async def VLR_match(request: Request, q: str):
    """
    query parameters:\n
        "upcoming": upcoming matches,\n
        "live_score": live match scores,\n
        "results": match results,\n
    """
    if q == "upcoming":
        return vlr.vlr_upcoming_matches()
    elif q == "live_score":
        return vlr.vlr_live_score()
    elif q == "results":
        return vlr.vlr_match_results()
    else:
        return {"error": "Invalid query parameter"}


# endregion

# region SHEEP API
@router.get("/news/thumbnail", tags=["sheep"])
@limiter.limit("250/minute")
async def get_thumbnail(request: Request, tag: str = ""):
    return sheep.sheep_news(tag)


@router.get("/news/content/", tags=["sheep"])
@limiter.limit("250/minute")
async def get_content(request: Request, article_url: str):
    return sheep.sheep_get_content(article_url)


# endregion

# region Miscellaneous
@router.get("/health", tags=["miscellaneous"])
def health():
    return "Healthy: OK"
# endregion
