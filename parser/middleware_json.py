from transformers import pipeline, AutoTokenizer
from langdetect import detect
import warnings
warnings.filterwarnings("ignore")

model_en = pipeline(
    "summarization",
    model="google/pegasus-xsum",
    max_length=4,      
    min_length=2,      
    do_sample=False
)

tokenizer_ru = AutoTokenizer.from_pretrained("sberbank-ai/ruT5-base", use_fast=False)
model_ru = pipeline(
    "summarization",
    model="sberbank-ai/ruT5-base",
    tokenizer=tokenizer_ru,
    max_length=4,
    min_length=2,
    do_sample=False
)

model_uk = pipeline(
    "text-generation",
    model="ai-forever/mGPT-1.3B-ukranian",
    tokenizer="ai-forever/mGPT-1.3B-ukranian",
    max_new_tokens=4,
    do_sample=True,
    top_k=50,
    top_p=0.95
)

def middleware(article_text: str) -> str:
    lang = detect(article_text)
    if lang not in ("en", "ru", "uk"):
        return article_text

    text = article_text[:5000]

    if lang == "en":
        out = model_en(text)[0]
        return out.get("summary_text", str(out))

    if lang == "ru":
        out = model_ru(text)[0]
        return out.get("summary_text", str(out))

    out = model_uk(text)[0]
    return out.get("generated_text", str(out))
