import os
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed
from dotenv import load_dotenv

# 환경 변수 로드
load_dotenv()

# DeepSeek API 설정
DEEPSEEK_API_KEY = os.getenv('DEEPSEEK_API_KEY')
DEEPSEEK_API_URL = "https://api.deepseek.com/v1/chat/completions"
MODEL_NAME = "deepseek-chat"  # 사용할 DeepSeek 모델 이름

def read_topics_from_input():
    # input.md 파일에서 주제 목록 읽기
    with open('input.md', 'r', encoding='utf-8') as f:
        lines = f.readlines()
        # 주제는 # 주제 목록 이후의 줄부터 시작
        topics = [line.strip() for line in lines if line.strip() and not line.startswith("#")]
    
    return [topic for topic in topics if topic]

def call_deepseek_api(topic, reference):
    headers = {
        "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
        "Content-Type": "application/json"
    }
    data = {
        "model": MODEL_NAME,
        "messages": [
            {"role": "system", "content": reference},
            {"role": "user", "content": f"'{topic}'에 대해 글을 작성해주세요."}
        ],
        "max_tokens": 2000
    }
    response = requests.post(DEEPSEEK_API_URL, headers=headers, json=data)
    if response.status_code == 200:
        return response.json()["choices"][0]["message"]["content"].strip()
    else:
        raise Exception(f"API 호출 실패: {response.status_code}, {response.text}")

def save_to_file(topic, content):
    filename = f"outputs/{topic.replace(' ', '_').lower()}.md"
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(content)

def process_topic(topic, reference):
    content = call_deepseek_api(topic, reference)
    save_to_file(topic, content)
    return topic

def main():
    # input.md 파일에서 주제 목록 읽기
    topics = read_topics_from_input()
    
    # reference.md 파일 읽기
    with open('reference.md', 'r', encoding='utf-8') as f:
        reference = f.read()

    # outputs 폴더 생성
    if not os.path.exists('outputs'):
        os.makedirs('outputs')

    # 병렬 처리
    with ThreadPoolExecutor(max_workers=20) as executor:
        futures = [executor.submit(process_topic, topic, reference) for topic in topics]
        for future in as_completed(futures):
            print(f"Completed: {future.result()}")

if __name__ == "__main__":
    main()
