from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from src.db.session import get_db
from src.schemas.access_request import AccessRequestCreate, AccessRequestResponse
from src.services.access_request_service import AccessRequestService

router = APIRouter()


@router.post(
    "/access-request",
    response_model=AccessRequestResponse,
    summary="Submit access request",
    description="Public endpoint for the Alá Poker landing page form.",
)
def submit_access_request(
    request_in: AccessRequestCreate,
    db: Session = Depends(get_db),
):
    service = AccessRequestService(db)
    return service.submit_access_request(request_in)
