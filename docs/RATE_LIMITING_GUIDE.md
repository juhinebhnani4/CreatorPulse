# Rate Limiting Guide

This guide explains how to configure and use rate limiting in the CreatorPulse backend.

## Installation

Rate limiting uses the `slowapi` library (FastAPI-compatible):

```bash
pip install slowapi
```

## Configuration

Rate limits are configured via environment variables in `.env`:

```bash
# Default rate limit for all endpoints (if not specified)
DEFAULT_RATE_LIMIT=100/minute

# Resource-intensive operations
NEWSLETTER_GENERATION_LIMIT=5/minute
TREND_DETECTION_LIMIT=10/minute
STYLE_TRAINING_LIMIT=10/minute

# High-volume operations
ANALYTICS_EVENT_LIMIT=1000/minute

# Rate limit storage (optional - defaults to memory)
# For production, use Redis:
# RATE_LIMIT_STORAGE_URI=redis://localhost:6379
```

## Usage in Endpoints

### Basic Usage

```python
from fastapi import APIRouter, Request
from backend.middleware.rate_limiter import limiter, RateLimits

router = APIRouter()

@router.post("/generate")
@limiter.limit(RateLimits.NEWSLETTER_GENERATION)
async def generate_newsletter(request: Request):
    # This endpoint is limited to 5 requests per minute per IP
    ...
```

### Custom Rate Limits

```python
@router.post("/custom-endpoint")
@limiter.limit("10/minute")  # Custom limit
async def custom_endpoint(request: Request):
    ...
```

### Multiple Rate Limits

```python
@router.post("/tiered-limit")
@limiter.limit("100/hour")  # Long-term limit
@limiter.limit("10/minute")  # Short-term burst limit
async def tiered_endpoint(request: Request):
    ...
```

## Integration with FastAPI App

In `backend/main.py`:

```python
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from backend.middleware.rate_limiter import limiter, rate_limit_exceeded_handler

app = FastAPI()

# Add rate limiter to app state
app.state.limiter = limiter

# Register custom error handler
app.add_exception_handler(RateLimitExceeded, rate_limit_exceeded_handler)
```

## Predefined Rate Limits

The `RateLimits` class provides predefined limits for common use cases:

```python
from backend.middleware.rate_limiter import RateLimits

# Resource-intensive operations
RateLimits.NEWSLETTER_GENERATION  # 5/minute
RateLimits.TREND_DETECTION        # 10/minute
RateLimits.STYLE_TRAINING         # 10/minute

# High-volume operations
RateLimits.ANALYTICS_EVENT        # 1000/minute

# Standard CRUD operations
RateLimits.CREATE                 # 20/minute
RateLimits.READ                   # 100/minute
RateLimits.UPDATE                 # 30/minute
RateLimits.DELETE                 # 10/minute

# Authentication
RateLimits.LOGIN                  # 5/minute
RateLimits.SIGNUP                 # 3/minute
```

## Error Response

When rate limit is exceeded, the API returns:

```json
HTTP 429 Too Many Requests
{
  "success": false,
  "error": "RateLimitExceeded",
  "message": "Too many requests. Please try again later.",
  "detail": "5 per 1 minute",
  "retry_after": 60
}
```

Headers:
```
Retry-After: 60
```

## Production Setup with Redis

For production, use Redis for distributed rate limiting:

1. Install Redis client:
```bash
pip install redis
```

2. Update `.env`:
```bash
RATE_LIMIT_STORAGE_URI=redis://localhost:6379
```

3. Start Redis:
```bash
docker run -d -p 6379:6379 redis:alpine
```

## Testing Rate Limits

```bash
# Test with curl
for i in {1..10}; do
  curl -X POST http://localhost:8000/api/v1/newsletters/generate
  sleep 1
done
```

After 5 requests within a minute, you'll receive a 429 error.

## Monitoring

Check rate limit headers in responses:

```
X-RateLimit-Limit: 5
X-RateLimit-Remaining: 3
X-RateLimit-Reset: 1234567890
```

## Best Practices

1. **Use appropriate limits** - Match limits to endpoint resource requirements
2. **Consider burst limits** - Allow short bursts but limit sustained load
3. **Use Redis in production** - Memory storage is reset on app restart
4. **Monitor 429 errors** - Track rate limit hits in analytics
5. **Communicate limits** - Document API rate limits for users
6. **Implement exponential backoff** - In client code, retry with increasing delays

## Examples

### Newsletter Generation Endpoint

```python
@router.post("/api/v1/newsletters/generate")
@limiter.limit(RateLimits.NEWSLETTER_GENERATION)
async def generate_newsletter(
    request: Request,
    data: NewsletterGenerateRequest
):
    # Limited to 5 requests per minute
    ...
```

### Trend Detection Endpoint

```python
@router.post("/api/v1/trends/detect")
@limiter.limit(RateLimits.TREND_DETECTION)
async def detect_trends(
    request: Request,
    workspace_id: UUID
):
    # Limited to 10 requests per minute
    ...
```

### Analytics Event Endpoint

```python
@router.post("/api/v1/analytics/events")
@limiter.limit(RateLimits.ANALYTICS_EVENT)
async def record_event(
    request: Request,
    event: AnalyticsEvent
):
    # Limited to 1000 requests per minute (high-volume)
    ...
```

## Troubleshooting

### Rate limits not working

1. Check that `limiter` is added to `app.state`
2. Ensure `Request` parameter is in endpoint signature
3. Verify storage URI is accessible

### All requests getting rate limited

1. Check if behind a proxy - may need to configure `key_func`
2. Use `X-Forwarded-For` header for real client IP:

```python
def get_real_ip(request: Request) -> str:
    return request.headers.get("X-Forwarded-For", request.client.host)

limiter = Limiter(key_func=get_real_ip, ...)
```

### Redis connection errors

1. Verify Redis is running
2. Check connection string format
3. Ensure firewall allows connection

## References

- [slowapi Documentation](https://github.com/laurents/slowapi)
- [FastAPI Rate Limiting](https://fastapi.tiangolo.com/)
- [Redis Setup Guide](https://redis.io/docs/getting-started/)
