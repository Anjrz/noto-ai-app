from openai import OpenAI

class AISummarizer:
    def __init__(self):
        # Point to your local Ollama server
        self.client = OpenAI(
            base_url='http://localhost:11434/v1',
            api_key='ollama'  # Required by the library, but ignored by Ollama
        )

    def summarize(self, text):
        completion = self.client.chat.completions.create(
            model="llama3",  # Use the exact model name you pulled with Ollama
            messages=[
                {"role": "system", "content": "You are a helpful assistant that summarizes text for students."},
                {"role": "user", "content": f"Summarize these notes for a student:\n{text}"}
            ]
        )
        return completion.choices[0].message.content
