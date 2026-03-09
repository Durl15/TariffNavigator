 import anthropic
>>
>> client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])
>>
>> response = client.messages.create(
>>     model="claude-haiku-4-5-20251001",  # ← Haiku model
>>     max_tokens=1024,
>>     messages=[
>>         {"role": "user", "content": "Your prompt here"}
>>     ]
>> )
>>
>> print(response.content[0].text)
>> ```