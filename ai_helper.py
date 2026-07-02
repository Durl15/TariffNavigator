import anthropic

# ── SETTINGS ──────────────────────────────────────────
API_KEY = "REDACTED_API_KEY"
FAST_MODEL  = "claude-haiku-4-5-20251001"   # cheap + fast
SMART_MODEL = "claude-sonnet-4-6"           # more powerful
# ──────────────────────────────────────────────────────

client = anthropic.Anthropic(api_key=API_KEY)

def ask_claude(prompt, smart=False, max_tokens=1024):
    """
    Send a prompt to Claude and get a response.
    smart=False uses Haiku (cheap)
    smart=True  uses Sonnet (powerful)
    """
    model = SMART_MODEL if smart else FAST_MODEL

    response = client.messages.create(
        model=model,
        max_tokens=max_tokens,
        messages=[
            {"role": "user", "content": prompt}
        ]
    )
    return response.content[0].text


# ── TEST IT ───────────────────────────────────────────
if __name__ == "__main__":

    # Test 1 — Haiku (fast and cheap)
    print("=== HAIKU RESPONSE ===")
    result = ask_claude("List 3 ways AI can help small businesses. Be brief.")
    print(result)

    # Test 2 — Sonnet (smarter)
    print("\n=== SONNET RESPONSE ===")
    result = ask_claude("List 3 ways AI can help small businesses. Be brief.", smart=True)
    print(result)
