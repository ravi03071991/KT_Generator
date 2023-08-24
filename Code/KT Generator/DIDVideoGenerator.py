import json
import requests
import time
import os
from loguru import logger
from dotenv import load_dotenv

load_dotenv() 

class DIDVideoGeneration:
    BASE_URL = "https://api.d-id.com/talks"
    HEADERS = {
        "accept": "application/json",
        "content-type": "application/json",
        # NOTE: Avoid hardcoding sensitive information. Ideally, this should be loaded securely
        "authorization": os.environ["DID_API_KEY"]
    }

    def __init__(self, source_url):
        self.source_url = source_url

    def create_talk(self, text):
        payload = {
            "script": {
                "type": "text",
                "subtitles": "false",
                "provider": {
                    "type": "microsoft",
                    "voice_id": "en-US-JasonNeural"
                },
                "ssml": "false",
                "input": text
            },
            "config": {
                "fluent": "false",
                "pad_audio": "0.0"
            },
            "source_url": self.source_url
        }
        response = requests.post(self.BASE_URL, json=payload, headers=self.HEADERS)
        return json.loads(response.text)["id"]

    def get_talk(self, talk_id):
        retries = 3
        logger.info("Waiting for video to be generated...")
        logger.info(f"Talk ID: {talk_id}")
        while retries > 0:
            logger.info(f"Retries left: {retries}")
            for i in range(4):
                time.sleep(30)
                logger.info(f"Time elapsed: {(i+1)*30} seconds")
            response = requests.get(f"{self.BASE_URL}/{talk_id}", headers=self.HEADERS)
            if "result_url" in json.loads(response.text):
               return json.loads(response.text)["result_url"]
            else:
                retries-=1

    def download_video(self, result_url, folder_name, output_file_name):
        response = requests.get(result_url)
        response.raise_for_status()
        with open(f"{folder_name}/{output_file_name}", "wb") as file:
            file.write(response.content)

    def process_chunk(self, chunk, i, folder_name):
        talk_id = self.create_talk(chunk)
        result_url = self.get_talk(talk_id)
        self.download_video(result_url, folder_name, f"chunk_{i}.mp4")