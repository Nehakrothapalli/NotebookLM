import re
from gtts import gTTS
from src.backend.llm import llm_generate
from src.backend.rag import format_sources, context_block

def generate_report(topic: str, hits, extra_prompt: str):
    prompt = f"""
Write a markdown study report grounded ONLY in the sources.
Every non-trivial claim must include citations like [S1].

Topic: {topic}
Extra instructions: {extra_prompt or "(none)"}

Sources list:
{format_sources(hits)}

Excerpts:
{context_block(hits)}

Output:
# Report
## Key Concepts
## Detailed Notes
## Key Takeaways
"""
    return llm_generate(prompt, max_new_tokens=900, temperature=0.25)

def generate_quiz(topic: str, hits, extra_prompt: str):
    prompt = f"""
Write a markdown quiz grounded ONLY in the sources.
Create 8 questions:
- 5 multiple choice
- 3 short answer
Then include an Answer Key with explanations.
Explanations must include citations like [S1].

Topic: {topic}
Extra instructions: {extra_prompt or "(none)"}

Sources list:
{format_sources(hits)}

Excerpts:
{context_block(hits)}

Output:
# Quiz
## Questions
## Answer Key
"""
    return llm_generate(prompt, max_new_tokens=900, temperature=0.25)

def generate_podcast_transcript(topic: str, hits, extra_prompt: str):
    prompt = f"""
Write a markdown podcast transcript grounded ONLY in the sources.
Two speakers: Speaker 1 and Speaker 2.
Every non-trivial claim must include citations like [S1].

Topic: {topic}
Extra instructions: {extra_prompt or "(none)"}

Sources list:
{format_sources(hits)}

Excerpts:
{context_block(hits)}

Output:
# Podcast Transcript
**Speaker 1:** ...
**Speaker 2:** ...
End with Sources section.
"""
    return llm_generate(prompt, max_new_tokens=900, temperature=0.3)

def transcript_to_mp3(transcript_md: str, out_path: str):
    text = re.sub(r"\[(S\d+)\]", "", transcript_md)
    text = re.sub(r"#+", "", text)
    text = re.sub(r"\*\*", "", text)
    text = re.sub(r"\s+", " ", text).strip()
    text = text[:4500]
    gTTS(text=text, lang="en").save(out_path)