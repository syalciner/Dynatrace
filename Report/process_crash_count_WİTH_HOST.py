import requests
import pandas as pd
from datetime import datetime, timedelta, timezone
import json
# Dynatrace API bilgileri
API_URL = "--/api/v2/events"
PROCESS_DETAILS_URL = "--/api/v2/entities"
API_TOKEN = "--"  # Buraya API Token'ınızı ekleyin
BASE_DYNATRACE_URL = "--/#processdetails;gtf=-30m;gf=all;id="

# İstek başlıkları
HEADERS = {
    "Authorization": f"Api-Token {API_TOKEN}"
}

# Tarih aralığını oluştur (Son 7 gün, UTC)
def get_date_range():
    end_time = datetime.utcnow()
    start_time = end_time - timedelta(days=7)
    return start_time.strftime('%Y-%m-%dT%H:%M:%SZ'), end_time.strftime('%Y-%m-%dT%H:%M:%SZ')

# API'den eventleri çek ve ham yanıtı kaydet
def fetch_events(start_time, end_time):
    all_events = []
    next_page_key = None

    while True:
        params = {"from": start_time, "to": end_time, "pageSize": 100}
        if next_page_key:
            params = {"nextPageKey": next_page_key}

        response = requests.get(API_URL, headers=HEADERS, params=params)
        if response.status_code != 200:
            print(f"API isteği başarısız oldu. Durum kodu: {response.status_code}, Hata: {response.text}")
            break

        data = response.json()

        # İlk ham yanıtı kaydet (kontrol amaçlı)
        with open("api_response.json", "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)

        events = data.get("events", [])
        filtered_events = [event for event in events if event.get("eventType") == "PGI_CRASHED_INFO"]
        all_events.extend(filtered_events)

        next_page_key = data.get("nextPageKey")
        if not next_page_key:
            break

    return all_events

# Olayları işleyip DataFrame'e dönüştür
def process_events(events):
    crash_data = []
    for event in events:
        try:
            # UTC zaman damgalarını Türkiye saatine (GMT+3) çevir
            start_time_utc = datetime.fromtimestamp(event.get("startTime", 0) / 1000, tz=timezone.utc)
            end_time_utc = datetime.fromtimestamp(event.get("endTime", 0) / 1000, tz=timezone.utc)
            start_time_tr = start_time_utc.astimezone(timezone(timedelta(hours=3)))
            end_time_tr = end_time_utc.astimezone(timezone(timedelta(hours=3)))

            # Process Name ve Process ID bilgisi
            entity_info = event.get("entityId", {})
            name = entity_info.get("name", "N/A")
            process_id = entity_info.get("entityId", {}).get("id", "N/A")

            # Dynatrace URL'sini oluştur
            dynatrace_url = f"{BASE_DYNATRACE_URL}{process_id}" if process_id != "N/A" else "N/A"

            # Management Zone bilgisi
            management_zones = event.get("managementZones", [])
            management_zone_names = ", ".join(zone.get("name", "N/A") for zone in management_zones)

            # Host bilgisi: properties içinde "host.name" anahtarını bul
            properties = event.get("properties", [])
            host_name = next((prop.get("value", "N/A") for prop in properties if prop.get("key") == "host.name"), "N/A")

            # Event bilgilerini ekle
            crash_data.append({
                "Event ID": event.get("eventId"),
                "Process ID": process_id,
                "Name": name,
                "Dynatrace URL": dynatrace_url,
                "Start Time (TR)": start_time_tr.strftime('%Y-%m-%d %H:%M:%S'),
                "End Time (TR)": end_time_tr.strftime('%Y-%m-%d %H:%M:%S'),
                "Management Zone": management_zone_names,
                "Host": host_name,  # Güncellenmiş host bilgisi
                "Description": event.get("eventDescription", "N/A")
            })
        except Exception as e:
            print(f"Event işlenirken hata oluştu: {e}")
    return pd.DataFrame(crash_data)

# Crash sayısını ekle
def add_crash_counts(df):
    if df.empty:
        return df
    df["Crash Count"] = df.groupby("Process ID")["Process ID"].transform("count")
    return df

# En çok crash olan 10 prosesi bul
def top_10_processes(df):
    if df.empty:
        return pd.DataFrame()
    top_processes = (
        df.groupby(["Process ID", "Name", "Dynatrace URL", "Host"])  # Host bilgisi dahil
        .size()
        .reset_index(name="Crash Count")
        .sort_values(by="Crash Count", ascending=False)
        .head(10)
    )
    return top_processes

# DataFrame'i Excel dosyasına yaz (Çoklu Sayfa)
def save_to_excel_with_sheets(df, top_10_df, filename):
    try:
        with pd.ExcelWriter(filename, engine="openpyxl") as writer:
            df.to_excel(writer, sheet_name="All Events", index=False)
            top_10_df.to_excel(writer, sheet_name="Top 10 Processes", index=False)
        print(f"Veriler başarıyla '{filename}' dosyasına yazdırıldı.")
    except Exception as e:
        print(f"Excel dosyasına yazma sırasında hata oluştu: {e}")

# Ana program
def main():
    print("Tarih aralığı oluşturuluyor (Son 7 gün)...")
    start_time, end_time = get_date_range()

    print("Olaylar API'den çekiliyor...")
    events = fetch_events(start_time, end_time)

    if not events:
        print("Hiç 'PGI_CRASHED_INFO' event bulunamadı.")
        return

    print(f"Toplam {len(events)} olay işleniyor...")
    df = process_events(events)

    print("Crash sayıları ekleniyor...")
    df = add_crash_counts(df)

    print("En çok crash olan 10 proses belirleniyor...")
    top_10_df = top_10_processes(df)

    print("Excel dosyasına kaydediliyor...")
    save_to_excel_with_sheets(df, top_10_df, "pgi_crashed_report_last_7_days.xlsx")

if __name__ == "__main__":
    main()