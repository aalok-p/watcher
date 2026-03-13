import httpx
import json
import re
from typing import AsyncGenerator
from config import OPENAI_API_KEY, OPENAI_BASE_URL,OPENAI_MODEL


SYSTEM_PROMPT="""You are a GPU health assistant embedded in a real-time GPU monitoring tool called Watcher.

STRICT RULES:
- ONLY answer questions about GPUs, graphics cards, VRAM, GPU drivers, CUDA, cuDNN, GPU temperature, GPU utilization, GPU memory, GPU benchmarks,DirectX, OpenGL, Vulkan, GPU overclocking, GPU cooling, PCIe bandwidth, nvidia-smi, GPU compute, ML training on GPU, or any directly GPU-related topic.
- If the user asks about ANYTHING unrelated to GPUs or GPU hardware/software, respond ONLY with: "I can only help with GPU-related questions. Please ask me something about your GPU."
- Keep answers concise,technical, and actionable (3-5 sentences max unless deep technical detail is needed).
- You have access to the user's live GPU metrics -always reference them when relevant.
- Never fabricate metric values. Only use the numbers provided in the context."""


def build_context(metrics: dict)->str:
    if not metrics:
        return "no GPU metrics available right now."
    return (
        f"Live GPU Metrics:\n"
        f"  GPU: {metrics.get('gpu_name', 'Unknown')}\n"
        f"  Utilization: {metrics.get('gpu_util', 0)}%\n"
        f"  VRAM: {metrics.get('mem_used_mb', 0)} MB / {metrics.get('mem_total_mb', 0)} MB "
        f"({metrics.get('mem_pct', 0)}%)\n"
        f"  Temperature: {metrics.get('temperature', 0)}°C\n"
        f"  Power: {metrics.get('power_draw', 0)}W / {metrics.get('power_limit', 0)}W "
        f"({metrics.get('power_pct', 0)}%)\n"
        f"  Throttle Reason: {metrics.get('throttle_reason', 'none')}"
    )


async def stream_chat(message: str, metrics: dict) -> AsyncGenerator[str, None]:
    context =build_context(metrics)
    user_content = f"{context}\n\nUser question: {message}"

    payload = {
        "model": OPENAI_MODEL,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_content},
        ],
        "stream": True,
    }

    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            async with client.stream(
                "POST",
                f"{OPENAI_BASE_URL}/chat/completions",
                json=payload,
                headers={"Authorization": f"Bearer {OPENAI_API_KEY}"}
            ) as resp:
                resp.raise_for_status()
                async for line in resp.aiter_lines():
                    if not line or not line.startswith("data: "):
                        continue
                    chunk =line[6:]
                    if chunk.strip()=="[DONE]":
                        break
                    try:
                        data = json.loads(chunk)
                        token = data.get("choices", [{}])[0].get("delta", {}).get("content", "")
                        if token:
                            yield token
                    except json.JSONDecodeError:
                        continue
    except httpx.ConnectError:
        yield "check your network and API key."
    except Exception as e:
        yield f"llm error: {e}"


async def llm_diagnose(metrics: dict) -> dict:
    context=build_context(metrics)
    prompt =(
        f"{context}\n\n"
        "Analyze these GPU metrics and respond with a JSON object only (no markdown, no explanation outside JSON).\n"
        "JSON format:\n"
        '{"status": "healthy|warning|critical", "headline": "one sentence max 12 words", '
        '"diagnosis": "2-3 sentences explaining what is happening", '
        '"action": "specific actionable recommendation"}\n'
        "Use the actual metric values in your response."
    )

    payload = {
        "model": OPENAI_MODEL,
        "messages": [
            {"role":"system","content": SYSTEM_PROMPT},
            {"role":"user","content": prompt},
        ],
        "stream": False,
    }

    try:
        async with httpx.AsyncClient(timeout=45.0) as client:
            resp=await client.post(
                f"{OPENAI_BASE_URL}/chat/completions",
                json=payload,
                headers={"Authorization": f"Bearer {OPENAI_API_KEY}"}
            )
            resp.raise_for_status()
            content = resp.json().get("choices", [{}])[0].get("message", {}).get("content", "")

        match=re.search(r"\{.*\}", content, re.DOTALL)
        if match:
            return json.loads(match.group())

        #fallback if no response
        return {
            "status": "healthy",
            "headline": "AI analysis complete.",
            "diagnosis": content.strip(),
            "action": "Review the analysis above.",
        }
    except httpx.ConnectError:
        return {
            "status": "error",
            "headline": "OpenAI API unreachable.",
            "diagnosis": "Cannot connect to OpenAI API. Check your network connection and API key.",
            "action": "Verify OPENAI_API_KEY is set correctly in .env",
        }
    except Exception as e:
        return {
            "status": "error",
            "headline": "AI diagnosis failed.",
            "diagnosis": str(e),
            "action": "Check OpenAI API key and base URL configuration.",
        }
