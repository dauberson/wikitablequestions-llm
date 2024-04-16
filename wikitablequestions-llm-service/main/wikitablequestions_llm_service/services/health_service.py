from fastapi import APIRouter
from pydantic import BaseModel

from wikitablequestions_llm_service.services.responses import responses

health_router = APIRouter(
    prefix="/health",
    tags=["health-service"],
)


class ResponseModel(BaseModel):
    status: str


@health_router.get(path="", responses=responses, response_model=ResponseModel)
async def health():
    """
    Returns a dictionary with app status

        Parameters:
        Returns:
                response (Dict): Dictionary with app status, it is used to k8s probes (livenessProbe and readinessProbe)
    """

    return ResponseModel(status="UP")
