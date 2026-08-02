from fastapi import APIRouter

router = APIRouter(tags=["Health"])


@router.get("/healthz")
def healthz() -> dict[str, str]:
    return {"status": "ok", "service": "neurocorp-backend"}
