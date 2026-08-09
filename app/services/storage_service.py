from pathlib import Path
from uuid import uuid4

import httpx
from fastapi import HTTPException, UploadFile

from app.core.config import settings

UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)


def _safe_extension(filename: str | None) -> str:
    ext = Path(filename or "").suffix.lower()
    if ext in {".jpg", ".jpeg", ".png", ".webp", ".gif"}:
        return ext
    return ".jpg"


def _clean_env(value: str) -> str:
    return value.strip().strip('"').strip("'")


def _supabase_base_url() -> str:
    """
    Aceita a Project URL limpa e também valores colados por engano
    (ex.: .../rest/v1 ou .../storage/v1).
    """
    base = _clean_env(settings.SUPABASE_URL).rstrip("/")
    for suffix in ("/storage/v1", "/rest/v1", "/auth/v1"):
        if base.endswith(suffix):
            base = base[: -len(suffix)].rstrip("/")
    return base


def _upload_local(filename: str, content: bytes) -> str:
    file_path = UPLOAD_DIR / filename
    file_path.write_bytes(content)
    base_url = settings.public_api_base_url.rstrip("/")
    return f"{base_url}/media/{filename}"


def _upload_supabase(filename: str, content: bytes, content_type: str) -> str:
    bucket = _clean_env(settings.SUPABASE_STORAGE_BUCKET).strip("/") or "bellora-uploads"
    base = _supabase_base_url()
    service_key = _clean_env(settings.SUPABASE_SERVICE_ROLE_KEY)

    if not base.startswith("https://") or "supabase.co" not in base:
        raise HTTPException(
            status_code=503,
            detail=(
                "SUPABASE_URL inválida. Use a Project URL do painel "
                "(ex.: https://xxxx.supabase.co), não a connection string do banco."
            ),
        )

    if not service_key.startswith("eyJ"):
        raise HTTPException(
            status_code=503,
            detail="SUPABASE_SERVICE_ROLE_KEY inválida. Use a chave service_role (secret) de Settings → API.",
        )

    # POST /storage/v1/object/{bucket}/{path}
    upload_url = f"{base}/storage/v1/object/{bucket}/{filename}"

    headers = {
        "Authorization": f"Bearer {service_key}",
        "apikey": service_key,
        "Content-Type": content_type or "application/octet-stream",
        "x-upsert": "true",
    }

    try:
        response = httpx.post(upload_url, content=content, headers=headers, timeout=60.0)
    except httpx.HTTPError as exc:
        raise HTTPException(
            status_code=502,
            detail=f"Falha de rede ao falar com o Supabase Storage: {exc}",
        ) from exc

    if response.status_code not in (200, 201):
        body = (response.text or "").strip()[:300]
        raise HTTPException(
            status_code=502,
            detail=(
                f"Storage rejeitou o upload ({response.status_code}) no bucket '{bucket}'. "
                f"URL: {upload_url}. "
                f"Resposta Supabase: {body or 'sem detalhe'}. "
                "Confira no Render se SUPABASE_URL é só https://SEU_REF.supabase.co "
                "(sem /rest/v1 e sem connection string do banco)."
            ),
        )

    return f"{base}/storage/v1/object/public/{bucket}/{filename}"


def _ensure_durable_storage() -> None:
    if settings.supabase_storage_configured:
        return

    base = settings.public_api_base_url.lower()
    if "localhost" in base or "127.0.0.1" in base:
        return

    raise HTTPException(
        status_code=503,
        detail=(
            "Upload indisponível em produção. Configure SUPABASE_URL, "
            "SUPABASE_SERVICE_ROLE_KEY e SUPABASE_STORAGE_BUCKET no Render "
            "(bucket público bellora-uploads)."
        ),
    )


def store_uploaded_image(file: UploadFile) -> dict[str, str]:
    content = file.file.read()
    if not content:
        raise HTTPException(status_code=400, detail="Arquivo vazio.")

    if len(content) > 5 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="Imagem muito grande (máx. 5 MB).")

    filename = f"{uuid4()}{_safe_extension(file.filename)}"
    content_type = file.content_type or "application/octet-stream"
    if content_type == "application/octet-stream":
        ext = _safe_extension(file.filename)
        content_type = {
            ".jpg": "image/jpeg",
            ".jpeg": "image/jpeg",
            ".png": "image/png",
            ".webp": "image/webp",
            ".gif": "image/gif",
        }.get(ext, "application/octet-stream")

    if settings.supabase_storage_configured:
        url = _upload_supabase(filename, content, content_type)
    else:
        _ensure_durable_storage()
        url = _upload_local(filename, content)

    return {"filename": filename, "url": url}
