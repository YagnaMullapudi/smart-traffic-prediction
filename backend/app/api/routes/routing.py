"""Route recommendation endpoint (Module 6). Uses an in-memory demo network;
swap build_sample_network() for a real graph built from your road dataset."""
from fastapi import APIRouter, Depends, HTTPException

from app.api.deps import get_current_user
from app.ml.route_recommendation import build_sample_network
from app.models.models import User
from app.schemas.schemas import RouteRequest, RouteResponse

router = APIRouter(prefix="/api/routes", tags=["route-recommendation"])

# In a real deployment this would be built once at startup from the roads dataset
# and refreshed periodically with live/predicted congestion factors.
_network = build_sample_network()


@router.post("/recommend", response_model=RouteResponse)
def recommend_route(payload: RouteRequest, current_user: User = Depends(get_current_user)):
    try:
        result = _network.recommend_route(payload.origin_node, payload.destination_node, payload.algorithm)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return result
