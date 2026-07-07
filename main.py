from fastapi import FastAPI, Header, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional

app = FastAPI()

# --- CORS Configuration ---
# Allows cross-origin requests from the grader/any browser page
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Your assigned API Key
ASSIGNED_API_KEY = "ak_weo8qrc061jq9zhw9hkyj2pe"
# Replace with your actual logged-in email address used in the grader
USER_EMAIL = "24f3001385@ds.study.iitm.ac.in" 

# --- Pydantic Models for Input Validation ---
class Event(BaseModel):
    user: str
    amount: float
    ts: int

class AnalyticsRequest(BaseModel):
    events: List[Event]

@app.post("/analytics")
async def get_analytics(
    request: AnalyticsRequest, 
    x_api_key: Optional[str] = Header(None, alias="X-API-Key")
):
    # 1. Authentication Check
    if x_api_key is None or x_api_key != ASSIGNED_API_KEY:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing or invalid API Key"
        )
    
    events = request.events
    total_events = len(events)
    
    # Track unique users and compute revenues
    unique_users_set = set()
    user_revenue_map = {}
    total_revenue = 0.0
    
    for event in events:
        unique_users_set.add(event.user)
        
        # Aggregation Rule: Only aggregate amounts strictly greater than 0
        if event.amount > 0:
            total_revenue += event.amount
            user_revenue_map[event.user] = user_revenue_map.get(event.user, 0.0) + event.amount

    # Find top_user (user with highest positive-amount total)
    # Handle edge case where no positive amounts exist
    if user_revenue_map:
        top_user = max(user_revenue_map, key=user_revenue_map.get)
    else:
        top_user = ""

    # 2. Return the aggregated payload matching the requested schema
    return {
        "email": USER_EMAIL,
        "total_events": total_events,
        "unique_users": len(unique_users_set),
        "revenue": total_revenue,
        "top_user": top_user
    }