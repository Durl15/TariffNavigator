import anthropic
client = anthropic.Anthropic(api_key="REDACTED_API_KEY")
response = client.messages.create(
     model="claude-haiku-4-5-20251001",  # ← Haiku model
     max_tokens=1024,
     messages=[
         {"role": "user", "content": "List 3 ways AI can help small businesses save money. Be brief."}
     ]
)
print(response.content[0].text)


