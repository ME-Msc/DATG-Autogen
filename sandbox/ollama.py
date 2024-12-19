from litellm import completion

response = completion(
    model="ollama/mistral",
    api_base="http://localhost:11434",
    stream=False,
    messages=[{"content": "respond in 20 words. who are you?", "role": "user"}],
)
print(response.choices[0].message.content)
