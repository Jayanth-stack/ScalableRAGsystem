"""API middleware components."""

import time
from typing import Callable
from fastapi import Request, Response, HTTPException
from fastapi.responses import JSONResponse
from collections import defaultdict
import asyncio

class RateLimitMiddleware:
    """Simple rate limiting middleware."""
    
    def __init__(self, calls: int = 100, period: int = 60):
        self.calls = calls
        self.period = period
        self.clients = defaultdict(list)
        
    async def __call__(self, request: Request, call_next: Callable) -> Response:
        client_id = request.client.host
        now = time.time()
        
        # Clean old entries
        self.clients[client_id] = [
            timestamp for timestamp in self.clients[client_id]
            if timestamp > now - self.period
        ]
        
        # Check rate limit
        if len(self.clients[client_id]) >= self.calls:
            return JSONResponse(
                status_code=429,
                content={"detail": "Rate limit exceeded"}
            )
        
        # Record request
        self.clients[client_id].append(now)
        
        # Process request
        response = await call_next(request)
        return response

class APIKeyMiddleware:
    """API key authentication middleware."""
    
    def __init__(self):
        self.api_keys = set()  # In production, load from database
        
    async def __call__(self, request: Request, call_next: Callable) -> Response:
        # Skip auth for docs and health
        if request.url.path in ["/docs", "/openapi.json", "/health", "/"]:
            return await call_next(request)
            
        api_key = request.headers.get("X-API-Key")
        if not api_key or api_key not in self.api_keys:
            return JSONResponse(
                status_code=401,
                content={"detail": "Invalid or missing API key"}
            )
            
        return await call_next(request) 