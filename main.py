from fastapi import FastAPI, Query
from fastapi.responses import JSONResponse
import requests
from bs4 import BeautifulSoup
import unicodedata

app = FastAPI()

# Şehir ID veritabanı
CITIES = {
    9146: "ADANA", 9158: "ADIYAMAN", 9167: "AFYONKARAHISAR", 9185: "AĞRI",
    9193: "AKSARAY", 9198: "AMASYA", 9206: "ANKARA", 9225: "ANTALYA",
    9238: "ARDAHAN", 9246: "ARTVIN", 9252: "AYDIN", 9270: "BALIKESIR",
    9285: "BARTIN", 9288: "BATMAN", 9295: "BAYBURT", 9297: "BILECIK",
    9303: "BINGOL", 9311: "BITLIS", 9315: "BOLU", 9327: "BURDUR",
    9335: "BURSA", 9352: "CANAKKALE", 9359: "CANKIRI", 9370: "CORUM",
    9392: "DENIZLI", 9402: "DIYARBAKIR", 9414: "DUZCE", 9419: "EDIRNE",
    9432: "ELAZIG", 9440: "ERZINCAN", 9451: "ERZURUM", 9470: "ESKISEHIR",
    9479: "GAZIANTEP", 9494: "GIRESUN", 9501: "GUMUSHANE", 9507: "HAKKARI",
    20089: "HATAY", 9522: "IĞDIR", 9528: "ISPARTA", 9541: "ISTANBUL",
    9560: "IZMIR", 9577: "KAHRAMANMARAS", 9581: "KARABUK", 9587: "KARAMAN",
    9594: "KARS", 9609: "KASTAMONU", 9620: "KAYSERI", 9629: "KILIS",
    9635: "KIRIKKALE", 9638: "KIRKLARELI", 9646: "KIRSEHIR", 9654: "KOCAELI",
    9676: "KONYA", 9689: "KUTAHYA", 9703: "MALATYA", 9716: "MANISA",
    9726: "MARDIN", 9737: "MERSIN", 9747: "MUGLA", 9755: "MUS",
    9760: "NEVSEHIR", 9766: "NIGDE", 9782: "ORDU", 9788: "OSMANIYE",
    9799: "RIZE", 9807: "SAKARYA", 9819: "SAMSUN", 9831: "SANLIURFA",
    9839: "SIIRT", 9847: "SINOP", 9854: "SIRNAK", 9868: "SIVAS",
    9879: "TEKIRDAG", 9887: "TOKAT", 9905: "TRABZON", 9914: "TUNCELI",
    9919: "USAK", 9930: "VAN", 9935: "YALOVA", 9949: "YOZGAT", 9955: "ZONGULDAK"
}

def normalize_string(string):
    """Şehir adını normalize et (İ/ı sorunlarını ve Türkçe karakterleri kaldır)"""
    string = unicodedata.normalize("NFKD", string).encode("ASCII", "ignore").decode("utf-8")
    return string.upper().replace("İ", "I")

def get_city_id(city_name: str):
    """Kullanıcının girdiği şehir adına göre city_id bul"""
    normalized = normalize_string(city_name)
    for k, v in CITIES.items():
        if normalize_string(v) == normalized:
            return k
    return None

def fetch_prayer_times(city_id: int):
    """Diyanet sitesinden vakitleri çek"""
    url = f"https://namazvakitleri.diyanet.gov.tr/tr-TR/{city_id}"
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")

    table = soup.select_one('#tab-1 > div > table')
    if not table:
        return None

    result = []
    for row in table.select("tr"):
        cols = row.find_all("td")
        if len(cols) >= 8:
            result.append({
                "miladi_tarih": cols[0].text.strip(),
                "hicri_tarih": cols[1].text.strip(),
                "imsak": cols[2].text.strip(),
                "gunes": cols[3].text.strip(),
                "ogle": cols[4].text.strip(),
                "ikindi": cols[5].text.strip(),
                "aksam": cols[6].text.strip(),
                "yatsi": cols[7].text.strip()
            })
    return result

@app.get("/")
def root():
    return {"message": "📿 Ezan Vakitleri API çalışıyor"}

@app.get("/vakitler")
def get_vakitler(city: str = Query(..., description="Şehir adı")):
    try:
        city_id = get_city_id(city)
        if not city_id:
            return JSONResponse(status_code=404, content={"status": False, "error": "❌ Şehir bulunamadı"})

        data = fetch_prayer_times(city_id)
        if not data:
            return JSONResponse(status_code=500, content={"status": False, "error": "❌ Veri alınamadı"})

        return {"status": True, "city": CITIES[city_id], "data": data}
    except Exception as e:
        return JSONResponse(status_code=500, content={"status": False, "error": str(e)})
