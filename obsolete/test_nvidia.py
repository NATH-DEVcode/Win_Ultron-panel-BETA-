import os
from openai import OpenAI

api_key = os.getenv("NVIDIA_API_KEY")

if not api_key:
    print("❌ NVIDIA_API_KEY no encontrada")
    raise SystemExit(1)

client = OpenAI(
    base_url="https://integrate.api.nvidia.com/v1",
    api_key=api_key
)

print("🧠 ULTRON está conectando con NVIDIA...")

response = client.chat.completions.create(
    model="nvidia/nemotron-3.5-lightning-30b-a3b",
    messages=[
        {
            "role": "user",
            "content": "Responde únicamente: ULTRON ONLINE"
        }
    ],
    temperature=0.2,
    max_tokens=50
)

print("\n🤖 NVIDIA:")
print(response.choices[0].message.content)
