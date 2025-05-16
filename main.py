from fastapi import FastAPI
import requests

app = FastAPI()

@app.get("/prayer-times")
def get_prayer_times(city: str = "Hatay", district: str = "Yayladağı"):
    url = f"https://ezanvakti.herokuapp.com/vakitler?il={city}&ilce={district}"
    response = requests.get(url)
    return response.json()
