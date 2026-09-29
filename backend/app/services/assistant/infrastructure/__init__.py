"""Assistant infrastructure layer: the only place with raw SQL and LLM calls.

Hosts the usage persistence adapter, the read adapter (context + factual SQL),
and the LLM provider adapter (Groq -> Gemini fallback).
"""
