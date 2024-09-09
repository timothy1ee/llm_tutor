import os
from dotenv import load_dotenv
import chainlit as cl
import openai
import asyncio
import json
from datetime import datetime
from prompts import ASSESSMENT_PROMPT, SYSTEM_PROMPT, CLASS_CONTEXT
from student_record import read_student_record, write_student_record, format_student_record, parse_student_record

# Load environment variables
load_dotenv()

configurations = {
    "mistral_7B_instruct": {
        "endpoint_url": os.getenv("MISTRAL_7B_INSTRUCT_ENDPOINT"),
        "api_key": os.getenv("RUNPOD_API_KEY"),
        "model": "mistralai/Mistral-7B-Instruct-v0.2"
    },
    "mistral_7B": {
        "endpoint_url": os.getenv("MISTRAL_7B_ENDPOINT"),
        "api_key": os.getenv("RUNPOD_API_KEY"),
        "model": "mistralai/Mistral-7B-v0.1"
    },
    "openai_gpt-4": {
        "endpoint_url": os.getenv("OPENAI_ENDPOINT"),
        "api_key": os.getenv("OPENAI_API_KEY"),
        "model": "gpt-4"
    }
}

# Choose configuration
config_key = "openai_gpt-4"
# config_key = "mistral_7B_instruct"
#config_key = "mistral_7B"

# Get selected configuration
config = configurations[config_key]

# Initialize the OpenAI async client
client = openai.AsyncClient(api_key=config["api_key"], base_url=config["endpoint_url"])

gen_kwargs = {
    "model": config["model"],
    "temperature": 0.3,
    "max_tokens": 500
}

# Configuration setting to enable or disable the system prompt
ENABLE_SYSTEM_PROMPT = True
ENABLE_CLASS_CONTEXT = True

def get_latest_user_message(message_history):
    # Iterate through the message history in reverse to find the last user message
    for message in reversed(message_history):
        if message['role'] == 'user':
            return message['content']
    return None

async def assess_message(message_history):
    file_path = "student_record.md"
    markdown_content = read_student_record(file_path)
    parsed_record = parse_student_record(markdown_content)

    latest_message = get_latest_user_message(message_history)

    # Remove the original prompt from the message history for assessment
    filtered_history = [msg for msg in message_history if msg['role'] != 'system']

    # Convert message history, alerts, and knowledge to strings
    history_str = json.dumps(filtered_history, indent=4)
    alerts_str = json.dumps(parsed_record.get("Alerts", []), indent=4)
    knowledge_str = json.dumps(parsed_record.get("Knowledge", {}), indent=4)
    
    current_date = datetime.now().strftime('%Y-%m-%d')

    # Generate the assessment prompt
    filled_prompt = ASSESSMENT_PROMPT.format(
        latest_message=latest_message,
        history=history_str,
        existing_alerts=alerts_str,
        existing_knowledge=knowledge_str,
        current_date=current_date
    )
    if ENABLE_CLASS_CONTEXT:
        filled_prompt += "\n" + CLASS_CONTEXT
    print("Filled prompt: \n\n", filled_prompt)

    response = await client.chat.completions.create(messages=[{"role": "system", "content": filled_prompt}], **gen_kwargs)

    assessment_output = response.choices[0].message.content.strip()
    print("Assessment Output: \n\n", assessment_output)

    # Parse the assessment output
    new_alerts, knowledge_updates = parse_assessment_output(assessment_output)

    # Update the student record with the new alerts and knowledge updates
    parsed_record["Alerts"].extend(new_alerts)
    for update in knowledge_updates:
        topic = update["topic"]
        note = update["note"]
        parsed_record["Knowledge"][topic] = note

    # Format the updated record and write it back to the file
    updated_content = format_student_record(
        parsed_record["Student Information"],
        parsed_record["Alerts"],
        parsed_record["Knowledge"]
    )
    write_student_record(file_path, updated_content)

def parse_assessment_output(output):
    try:
        parsed_output = json.loads(output)
        new_alerts = parsed_output.get("new_alerts", [])
        knowledge_updates = parsed_output.get("knowledge_updates", [])
        return new_alerts, knowledge_updates
    except json.JSONDecodeError as e:
        print("Failed to parse assessment output:", e)
        return [], []

@cl.on_message
async def on_message(message: cl.Message):
    message_history = cl.user_session.get("message_history", [])

    if ENABLE_SYSTEM_PROMPT and (not message_history or message_history[0].get("role") != "system"):
        system_prompt_content = SYSTEM_PROMPT
        if ENABLE_CLASS_CONTEXT:
            system_prompt_content += "\n" + CLASS_CONTEXT
        message_history.insert(0, {"role": "system", "content": system_prompt_content})

    message_history.append({"role": "user", "content": message.content})

    asyncio.create_task(assess_message(message_history))
    
    response_message = cl.Message(content="")
    await response_message.send()

    if config_key == "mistral_7B":
        stream = await client.completions.create(prompt=message.content, stream=True, **gen_kwargs)
        async for part in stream:
            if token := part.choices[0].text or "":
                await response_message.stream_token(token)
    else:
        stream = await client.chat.completions.create(messages=message_history, stream=True, **gen_kwargs)
        async for part in stream:
            if token := part.choices[0].delta.content or "":
                await response_message.stream_token(token)

    message_history.append({"role": "assistant", "content": response_message.content})
    cl.user_session.set("message_history", message_history)
    await response_message.update()


if __name__ == "__main__":
    cl.main()
