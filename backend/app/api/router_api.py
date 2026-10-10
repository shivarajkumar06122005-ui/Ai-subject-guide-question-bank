from fastapi import APIRouter

from app.models.router_model import RouterRequest, RouterResult
from app.services.intent_detection_service import route_intent

router = APIRouter(prefix="/api/v1/router", tags=["Router / Intent Agent"])


@router.post("/intent", response_model=RouterResult)
def classify_intent(request: RouterRequest) -> RouterResult:
    return route_intent(
        request.message,
        document_related=request.document_related,
        image_related=request.image_related,
        voice_related=request.voice_related,
    )
