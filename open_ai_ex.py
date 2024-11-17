import os
from dotenv import load_dotenv
from openai import OpenAI
import asyncio
import random
import tiktoken

load_dotenv()  

client = OpenAI(
    api_key='YOUR_API_KEY_HERE', # Replace with your actual API Key
    base_url="https://api.gilas.io/v1/"
)

context = 16385
max_tokens = 1000
messages_formating_tokens = 20 

def get_completion(instruction, prompt, model="gpt-4o-mini"):
    messages = [{"role": "system", "content": instruction},
                {"role": "user", "content": prompt}]
    response = client.chat.completions.create(
        model=model,
        messages=messages,
        temperature=0.0,
        max_tokens=max_tokens
    )
    
    return response.choices[0].message.content

encoding = tiktoken.get_encoding("cl100k_base")

def num_tokens_from_string(string: str) -> int:
    return len(encoding.encode(string))

def generate_few_shots_instruction(basic_instruction, prompt):
    prompt_tokens = num_tokens_from_string(prompt)
    instruction = f"{basic_instruction}\n"

    file_path = "few-shots.txt"
    with open(file_path, "r", encoding='utf-8') as file:
        lines = file.readlines()
    
    lines = [line.strip() for line in lines if line.strip()]
    samples = []
    
    for i in range(0, len(lines), 2):
        if i + 1 < len(lines):
            samples.append(f"{lines[i].strip()}\n{lines[i + 1].strip()}\n")

    random.shuffle(samples)
    for sample in samples:
        new_instruction = instruction + f"{sample}\n"
        if num_tokens_from_string(new_instruction) > (context - (max_tokens + prompt_tokens + messages_formating_tokens)):
            break
        instruction = new_instruction
    
    return instruction

basic_instruction = f"""
You are an intelligent translator specializing in translating technical texts from English to Farsi. Please follow these steps to translate the provided English texts to Farsi:
1. Thoroughly understand the given text.
2. Translate the content into fluent Farsi, preserving the original structure and flow.
3. Tailor the translation for software engineers by keeping the technical and programming terms in English, enclosed in backticks (e.g., `GPT-3`).
4. You can include additional explanations in Farsi for clarity, if needed.
5. If you encounter a block of text enclosed in triple backticks, do not translate it; keep it as it is in your translation.
6. Review your translation to ensure you followed the steps. If the translated text is not fluent Farsi, revise it. 
7. Your output should only include the very final version and formatted translation. 
"""

def get_next_test_data():
    file_path = "test-data.txt"
    with open(file_path, "r", encoding='utf-8') as file:
        lines = file.readlines()
    
    if not hasattr(get_next_test_data, "current_index"):
        get_next_test_data.current_index = 0

    while get_next_test_data.current_index < len(lines):
        next_line = lines[get_next_test_data.current_index].strip()
        get_next_test_data.current_index += 1
        if next_line:
            return f"""English: {next_line} \n
            Farsi: ?
            """

    return None

async def gen_prompt_response(sample):
    few_shots_response = await asyncio.to_thread(few_shots_prompt, sample)
    single_shot_response = await asyncio.to_thread(zero_shot_prompt, sample)

    print(f"English Text: {sample.strip()}")
    print(f"Zero Shot Translation: {single_shots_response.strip()}")
    print(f"Few Shots Translation: {few_shots_response.strip()}\n")

def few_shots_prompt(question):
    _instruction = generate_few_shots_instruction(basic_instruction, question)   
    return get_completion(_instruction, question)

def zero_shot_prompt(question):
    return get_completion(basic_instruction, question)

async def main():
    sample = get_next_test_data()
    while sample:
        await gen_prompt_response(sample)
        sample = get_next_test_data()

asyncio.run(main())