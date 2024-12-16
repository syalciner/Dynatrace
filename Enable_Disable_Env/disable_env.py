import requests
import urllib3

# SSL uyarılarını bastır
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Dynatrace API bilgileri
CLUSTER_TOKEN = "Api-Token xxxxxx"
BASE_URL = "https://xxxxxxx/api/cluster/v2/environments"
ENV_IDS = [
    "xxxENV_TOKENxxxxx",  # Test Env 1
    "dxxxENV_TOKENxxxxx"   # Test Env 2
]

def update_environment_state(env_ids, cluster_token, base_url, state):
    headers = {
        'Authorization': cluster_token,
        'Content-Type': 'application/json',
    }

    payload = {
        "state": state
    }

    for env_id in env_ids:
        try:
            url = f"{base_url}/{env_id}"
            response = requests.put(url, headers=headers, json=payload, verify=False)
            if response.status_code in [200, 204]:
                print(f"Environment '{env_id}' başarıyla {state} durumuna getirildi.")
            else:
                print(f"Hata: Environment '{env_id}' durumuna getirilemedi. Status Code: {response.status_code}")
                print(f"Yanıt: {response.text}")
        except Exception as e:
            print(f"Bir hata oluştu: {e}")

def main():
    # DISABLE etmek için:
    update_environment_state(ENV_IDS, CLUSTER_TOKEN, BASE_URL, "DISABLED")

    # ENABLE etmek için (eğer gerekirse):
    # update_environment_state(ENV_IDS, CLUSTER_TOKEN, BASE_URL, "ENABLED")

if __name__ == "__main__":
    main()
