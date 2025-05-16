from fastapi import FastAPI, Query
import requests

app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "Ezan Vakti API'ye hoş geldiniz"}

@app.get("/vakitler")
def get_prayer_times(
    city: str = Query(default="Istanbul", description="Şehir adı"),
    country: str = Query(default="Turkey", description="Ülke adı"),
    method: int = Query(default=13, description="Hesaplama metodu (varsayılan: Diyanet Türkiye - 13)")
):
    url = f"https://api.aladhan.com/v1/timingsByCity?city={city}&country={country}&method={method}&school=1"
    response = requests.get(url)

    if response.status_code != 200:
        return {"error": "API yanıt vermedi."}

    data = response.json()
    return {
        "konum": f"{city}, {country}",
        "tarih": data["data"]["date"]["readable"],
        "vakitler": data["data"]["timings"]
    }
