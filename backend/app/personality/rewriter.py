"""Google Gemini API integration for personality-flavored review rewriting.

Takes structured findings + a personality config, calls the Gemini API with
streaming, and yields text chunks to the frontend.
"""

import json
from typing import Any, AsyncGenerator

import google.generativeai as genai

from app.config import settings
from app.personality import PERSONALITIES, PersonalityConfig
from app.schemas.findings import AnalysisResult


async def rewrite_findings_stream(
    analysis: AnalysisResult,
    personality_id: str,
    code: str,
) -> AsyncGenerator[str, None]:
    """Stream a personality-flavored review from Gemini.

    Yields text chunks. The caller wraps them in SSE framing.
    """
    if personality_id not in PERSONALITIES:
        raise ValueError(f"Unknown personality: {personality_id}")

    config: PersonalityConfig = PERSONALITIES[personality_id]

    api_key = settings.GEMINI_API_KEY
    if api_key and not api_key.startswith("sk-ant-") and api_key != "mock":
        try:
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel(
                model_name="gemini-3.5-flash",
                system_instruction=config.system_prompt
            )

            findings_data = [
                {
                    "id": f.id,
                    "category": f.category,
                    "rule": f.rule,
                    "severity": f.severity,
                    "message": f.message,
                    "line_start": f.line_start,
                    "line_end": f.line_end,
                    "code_snippet": f.code_snippet,
                    "suggestion": f.suggestion,
                }
                for f in analysis.findings
            ]

            prompt = json.dumps({
                "code": code,
                "input_stats": analysis.input_stats,
                "findings": findings_data,
            }, indent=2)

            import asyncio
            def _generate():
                response = model.generate_content(prompt, stream=True)
                chunks = []
                for chunk in response:
                    if chunk.text:
                        chunks.append(chunk.text)
                return chunks

            chunks = await asyncio.to_thread(_generate)
            for chunk in chunks:
                yield chunk
            return
        except Exception as e:
            yield json.dumps({
                "opening": f"Gemini API Error: {str(e)}",
                "findings": [],
                "closing": "Please check your API key.",
                "overall_grade": "F"
            })
            return

    # Fallback mock generator if no valid Gemini key provided
    yield json.dumps({
        "opening": f"[{config.name} Roast]: This code has some serious issues.",
        "findings": [
            {
                "id": f.id,
                "comment": f"Rule {f.rule}: {f.message}",
                "severity_reaction": f"[{f.severity.upper()}]"
            }
            for f in analysis.findings
        ],
        "closing": "Clean this up before shipping!",
        "overall_grade": "C"
    })


def parse_claude_output(text: str) -> dict[str, Any]:
    """Parse Gemini's streamed JSON output into a structured dict."""
    import re
    cleaned = re.sub(r"^```(?:json)?\n?|\n?```$", "", text.strip(), flags=re.MULTILINE)
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        return {
            "opening": text[:300] if len(text) > 300 else text,
            "findings": [],
            "closing": "Review complete.",
            "overall_grade": "C"
        }
