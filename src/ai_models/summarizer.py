from transformers import pipeline

class StoryProcessor:
    def __init__(self):
        self.summarizer = pipeline('summarization')
    
    def summarize(self, text, max_length=150, min_length=50):
        return self.summarizer(text, max_length=max_length, min_length=min_length)[0]['summary_text']