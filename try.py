from google import genai

client = genai.Client(api_key="AIzaSyBfyeioijtuTAO1Vig2r-b-82NmYIZQOHg")
response = client.models.generate_content(
    model="gemini-2.0-flash", contents="Explain how AI works"
)
print(response.text)