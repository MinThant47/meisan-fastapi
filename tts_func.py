# import requests

# url = "https://client.camb.ai/apis/tts"
# API_KEY = "9c280bc6-49b2-4047-bc60-64767634255c"

# payload = {
#     "text": text,
#     "voice_id": 20305,
#     "language": 104,
#     "gender": 2,
#     "age": 2
# }
# headers = {
#     "x-api-key": API_KEY,
#     "Content-Type": "application/json"
# }

# response = requests.request("POST", url, json=payload, headers=headers)

# data = response.json()
# print(data)

# # Access run_id
# task_id = data.get("task_id")
# print(task_id)

# url = f"https://client.camb.ai/apis/tts/{task_id}"

# headers = {"x-api-key": API_KEY}

# response = requests.request("GET", url, headers=headers)

# data = response.json()

# # Access run_id
# status = data.get("status")
# while (status != "SUCCESS"):
#     response = requests.request("GET", url, headers=headers)
#     data = response.json()
#     status = data.get("status")

# if (status == "SUCCESS"):
#     run_id = data.get("run_id")
#     print(run_id)

# if run_id:
#     tts_result = requests.get(
#         f"https://client.camb.ai/apis/tts-result/{run_id}", # Replace with a `run_id` for a run you created.
#         headers={"x-api-key": API_KEY}, stream=True
#     )

#     with open("output.wav", "wb") as f:
#         for chunk in tts_result.iter_content(chunk_size=1024):
#             f.write(chunk)


import time
import requests

API_KEY = "9c280bc6-49b2-4047-bc60-64767634255c"
BASE_URL = "https://client.camb.ai/apis/tts"

HEADERS = {
    "x-api-key": API_KEY,
    "Content-Type": "application/json"
}


def initiate_tts(text, voice_id=20305, language=104, gender=2, age=2):
    payload = {
        "text": text,
        "voice_id": voice_id,
        "language": language,
        "gender": gender,
        "age": age
    }
    response = requests.post(BASE_URL, json=payload, headers=HEADERS)
    response.raise_for_status()
    data = response.json()
    return data.get("task_id")


def wait_for_completion(task_id, poll_interval=2):
    status = ""
    run_id = None
    url = f"{BASE_URL}/{task_id}"
    headers = {"x-api-key": API_KEY}

    while status != "SUCCESS":
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        data = response.json()
        status = data.get("status")
        run_id = data.get("run_id")
        if status != "SUCCESS":
            time.sleep(poll_interval)
    return run_id


def download_tts_result(run_id, filename="response_output.wav"):
    url = f"https://client.camb.ai/apis/tts-result/{run_id}"
    response = requests.get(url, headers={"x-api-key": API_KEY}, stream=True)
    response.raise_for_status()
    with open(filename, "wb") as f:
        for chunk in response.iter_content(chunk_size=1024):
            f.write(chunk)
    print(f"TTS audio saved as {filename}")


def run_tts_pipeline(text):
    task_id = initiate_tts(text)
    print("Task ID:", task_id)
    run_id = wait_for_completion(task_id)
    print("Run ID:", run_id)
    if run_id:
        download_tts_result(run_id)

