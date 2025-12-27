
import requests
import time

def test_analytics_performance():
    url = "http://localhost:8000/api/v1/analytics/summary"
    print(f"Testing analytics endpoint: {url}")
    
    start_time = time.time()
    try:
        response = requests.post(url, json={}, timeout=35)
        duration = time.time() - start_time
        
        if response.status_code == 200:
            print(f"SUCCESS: Analytics loaded in {duration:.2f} seconds")
            data = response.json()
            print(f"Total Queries: {data.get('total_queries')}")
            print(f"Overall CTR: {data.get('overall_ctr'):.4f}")
        else:
            print(f"FAILED: Status Code {response.status_code}")
            print(f"Error: {response.text}")
            
    except requests.exceptions.Timeout:
        print(f"FAILED: Request Timed Out after {time.time() - start_time:.2f} seconds")
    except Exception as e:
        print(f"ERROR: {e}")

if __name__ == "__main__":
    test_analytics_performance()
