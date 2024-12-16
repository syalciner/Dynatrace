import requests
from openpyxl import Workbook
import urllib3
from requests.packages.urllib3.exceptions import InsecureRequestWarning
from datetime import datetime, timedelta

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

Base_Url="https://--/e/"
Env ="--"
Token ="--"

url = Base_Url + Env + '/api/v2/events?pageSize=1000&from=now-30d&eventSelector=frequentEvent%28true%29'
Next_Page_Url = Base_Url + Env + '/api/v2/events?'
headers = {
    'accept': 'application/json; charset=utf-8',
    'Authorization': 'Api-Token ' + Token
}

all_events = []

response = requests.get(url, headers=headers, verify=False)
data = response.json()

if 'events' in data:
    all_events.extend(data['events'])

while 'nextPageKey' in data:
    next_page_key = data['nextPageKey']
    next_url = f'{Next_Page_Url}&nextPageKey={next_page_key}'
    response = requests.get(next_url, headers=headers, verify=False)
    data = response.json()
    if 'events' in data:
        all_events.extend(data['events'])
    else:
        break

event_list = []
for event in all_events:
    event_id = event.get('eventId', '')
    event_type = event.get('eventType', '')
    title = event.get('title', '')
    entity_id = event.get('entityId', {}).get('entityId', {}).get('id', '')
    entity_type = event.get('entityId', {}).get('entityId', {}).get('type', '')
    entity_name = event.get('entityId', {}).get('name', '')
    status = event.get('status', '')
    start_time = event.get('startTime', '')
    entity_tag = event.get('entityTags', [])
    if entity_tag and 'key' in entity_tag[0]:
        entity_tag_name = entity_tag[0]['key']
    else:
        entity_tag_name = "Tag Yok"
    management_zone = event.get('managementZones', [])
    if management_zone and 'name' in management_zone[0]:
        management_zone_name = management_zone[0]['name']
    else:
        management_zone_name = "MZ YOK"

    # Timestamp'ı Türkiye saatine çeviriyoruz
    if start_time:
        timestamp_utc = datetime.utcfromtimestamp(start_time / 1000)
        timestamp_tr = timestamp_utc + timedelta(hours=3)
    else:
        timestamp_tr = ""

    # Dynatrace Entity URL'si
    entity_url = f"{Base_Url}{Env}/#entity;id={entity_id}" if entity_id else "URL Yok"

    event_list.append([event_id, event_type, title, entity_id, entity_name, entity_type,
                       management_zone_name, entity_tag_name, timestamp_tr, entity_url])

entity_id_counts = {}
for event in event_list:
    entity_id = event[3]
    if entity_id in entity_id_counts:
        entity_id_counts[entity_id] += 1
    else:
        entity_id_counts[entity_id] = 1

wb = Workbook()
ws = wb.active
ws.title = "Dynatrace Events Report"

headers = ['Event ID', 'Event Type', 'Title', 'Entity ID', 'Entity Name', 'Entity Type',
           'Management Zone', 'Tag', 'TimeStamp (TR)', 'Entity URL', 'Entity ID Count']
ws.append(headers)

for event in event_list:
    entity_id_count = entity_id_counts[event[3]]
    ws.append(event + [entity_id_count])

# Excel dosyasını kaydediyoruz
wb.save("dynatrace_events_report.xlsx")

print('Veriler başarıyla Excel dosyasına kaydedildi.')