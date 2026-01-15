import os
from openai import OpenAI
from dotenv import load_dotenv


# Załaduj .env z folderu backend
load_dotenv('.env')

token = os.getenv("GITHUB_TOKEN")
endpoint = "https://models.inference.ai.azure.com"

print(f"Testowanie tokena: {token[:4]}...{token[-4:]}")

client = OpenAI(
    base_url=endpoint,
    api_key=token,
)

try:
    # Testujemy na modelu gpt-4o-mini (Twój backup)
    response = client.chat.completions.create(
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "Are you working? Reply with 'Yes, RecruitMate is online'."}
        ],
        model="gpt-4o-mini",
    )
    print("\n✅ SUKCES! Odpowiedź modelu:")
    print(response.choices[0].message.content)
except Exception as e:
    print(f"\n❌ BŁĄD: {e}")
    print("Sprawdź czy token jest poprawnie wklejony do .env i nie ma spacji na końcu.")
