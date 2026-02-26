from google import genai

client = genai.Client(api_key="AIzaSyBqpVmkAu5R5hC2-RwUYse0Umyby87UFuE")

# Quick test with more details
models = client.models.list()
for m in models:
    print(f"Model: {m.name}")
    print(f"  Display Name: {m.display_name}")
    print(f"  Description: {m.description}")
    print(f"  Supported Actions: {m.supported_actions}")
    
    # If you want to see all attributes of the model object
    # print(f"  All attributes: {dir(m)}")
    print("-" * 50)