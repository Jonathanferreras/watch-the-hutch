import os
import httpx
from fastapi import APIRouter, Request, Response, HTTPException

router = APIRouter()
MEDIAMTX_WEBRTC_URL = os.getenv("MEDIAMTX_WEBRTC_URL")

def normalize_upstream_url(raw_url: str | None) -> str:
    if not raw_url:
        raise HTTPException(
            status_code=500,
            detail="MEDIAMTX_WEBRTC_URL is not set",
        )
    if raw_url.startswith("http://") or raw_url.startswith("https://"):
        return raw_url
    return f"http://{raw_url}"


@router.post("/camera/whep")
async def proxy_webrtc_whep(request: Request):
    upstream_base = normalize_upstream_url(MEDIAMTX_WEBRTC_URL).rstrip("/")
    upstream_url = f"{upstream_base}/camera/whep"
    body = await request.body()
    headers = {}
    content_type = request.headers.get("content-type")
    if content_type:
        headers["content-type"] = content_type

    async with httpx.AsyncClient() as client:
        upstream_resp = await client.post(upstream_url, content=body, headers=headers)

    response_headers = {}
    if "content-type" in upstream_resp.headers:
        response_headers["content-type"] = upstream_resp.headers["content-type"]
    if "location" in upstream_resp.headers:
        response_headers["location"] = "/camera/whep"

    return Response(
        content=upstream_resp.content,
        status_code=upstream_resp.status_code,
        headers=response_headers,
    )
