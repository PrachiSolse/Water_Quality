import requests
import time
import random
import urllib3

# This line hides the "Insecure Request" warning from your terminal
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

URL = "https://script.google.com/macros/s/AKfycbz5qGHDLA0Rv3r9vwjZ1LoeQ5vDNi6IdsR0u2AX3inXbZW7IKn0JZ9vTuc1XGZcx8sAqg/exec"


def run_simulator():
    print("--- AI Water Monitor Simulator Started ---")
    while True:
        data = {
            "ph": round(random.uniform(6, 7.5), 2),
            "turb": round(random.uniform(1.2, 3.8), 2),
            "tds": random.randint(180, 1000),
            "temp": round(random.uniform(24.5, 25.5), 1)
        }
        
        try:
            # ADD verify=False HERE
            response = requests.post(URL, json=data, verify=False)
            if response.status_code == 200:
                print(f"Success! Sent: {data}")
            else:
                # If it says 302, that's actually fine—it's a Google redirect
                print(f"Server Response: {response.status_code}")
        except Exception as e:
            print(f"Connection Failed: {e}")
            
        time.sleep(10)

if __name__ == "__main__":
    run_simulator()            
             






