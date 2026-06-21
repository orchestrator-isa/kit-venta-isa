"""
Seguridad para ISA ChatCommerce
Rate limiting, headers, validación
"""
from fastapi import Request, HTTPException
import time
from collections import defaultdict

# Rate limiting simple (en memoria)
request_counts = defaultdict(list)

async def rate_limit(request: Request, max_requests: int = 30, window: int = 60):
    """Limita requests por IP"""
    client_ip = request.client.host
    now = time.time()

    # Limpiar requests antiguos
    request_counts[client_ip] = [t for t in request_counts[client_ip] if now - t < window]

    if len(request_counts[client_ip]) >= max_requests:
        raise HTTPException(status_code=429, detail="Too many requests")

    request_counts[client_ip].append(now)

# Headers de seguridad
security_headers = {
    "X-Content-Type-Options": "nosniff",
    "X-Frame-Options": "DENY",
    "X-XSS-Protection": "1; mode=block",
    "Strict-Transport-Security": "max-age=31536000; includeSubDomains",
    "Referrer-Policy": "strict-origin-when-cross-origin",
}
