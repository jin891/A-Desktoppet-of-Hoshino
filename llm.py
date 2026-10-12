import os
from openai import OpenAI
import json
import jsontool as jt
import pyautogui
import base64
import io
from PIL import Image
from datetime import datetime



def get_llm_stream(prompt):
    Settings = jt.get_value("settings.json", "LLMSystem")
    client = OpenAI(
        api_key=jt.get_value("settings.json", "LLM_API"),
        base_url=jt.get_value("settings.json", "LLM_URL")
    )
    respon = client.chat.completions.create(
        model=jt.get_value("settings.json", "LLM_NAME"),
        messages=[
            {"role": "system", "content": Settings},
            {"role": "user", "content": prompt}

        ],
        stream=True
    )
    for chunk in respon:
        content = chunk.choices[0].delta.content
        if content is not None:
            yield content

def get_llm_respon(prompt):
    Settings = jt.get_value("settings.json", "LLMSystem")
    client = OpenAI(
        api_key=jt.get_value("settings.json", "LLM_API"),
        base_url=jt.get_value("settings.json", "LLM_URL")
    )
    respon = client.chat.completions.create(
        model=jt.get_value("settings.json", "LLM_NAME"),
        messages=[
            {"role": "system", "content": Settings},
            {"role": "user", "content": prompt}

        ],
        stream=False
    )
    return respon.choices[0].message.content

def recognize_screen_respon(prompt, picture):
    Settings = jt.get_value("settings.json", "LLMSystem")
    client = OpenAI(
        api_key=jt.get_value("settings.json", "RecscreenLLMAPI"),
        base_url=jt.get_value("settings.json", "RecscreenLLMURL")
    )
    respon = client.chat.completions.create(
        model = jt.get_value("settings.json", "RecscreenLLMName"),
        messages = [
            {"role": "system", "content": Settings},
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/png;base64,{picture}"
                        }
                    }
                ]
            }
        ],
        stream = False
    )
    return respon.choices[0].message.content

def recognize_screen_stream(prompt, picture):
    Settings = jt.get_value("settings.json", "LLMSystem")
    client = OpenAI(
        api_key=jt.get_value("settings.json", "RecscreenLLMAPI"),
        base_url=jt.get_value("settings.json", "RecscreenLLMURL")
    )
    respon = client.chat.completions.create(
        model = jt.get_value("settings.json", "RecscreenLLMName"),
        messages = [
            {"role": "system", "content": Settings},
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/png;base64,{picture}"
                        }
                    }
                ]
            }
        ],
        stream = True
    )
    for chunk in respon:
        content = chunk.choices[0].delta.content
        if content is not None:
            yield content