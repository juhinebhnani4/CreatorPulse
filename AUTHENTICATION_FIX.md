# Authentication Token Fix

## Issue
The Content Library and Newsletter Generator tabs were showing "API Error: Not authenticated" because the API client functions were looking for the wrong session state variable.

## Root Cause
- **Expected:** `st.session_state.auth_token`
- **Actual:** `st.session_state.token`

The authentication flow in [frontend/utils/auth.py](frontend/utils/auth.py) stores the JWT token as `st.session_state.token` (line 48), but the API client functions in Sprint 2 and Sprint 3 were looking for `st.session_state.auth_token`.

## Fix Applied

### Files Modified:

1. **[frontend/utils/content_api.py](frontend/utils/content_api.py:16-24)**
   - Changed `st.session_state.auth_token` → `st.session_state.token`

2. **[frontend/utils/newsletter_api.py](frontend/utils/newsletter_api.py:17-25)**
   - Changed `st.session_state.auth_token` → `st.session_state.token`

### Code Change:

```python
# BEFORE (❌ Wrong)
def _get_headers() -> Dict[str, str]:
    headers = {"Content-Type": "application/json"}
    if 'auth_token' in st.session_state and st.session_state.auth_token:
        headers["Authorization"] = f"Bearer {st.session_state.auth_token}"
    return headers

# AFTER (✅ Correct)
def _get_headers() -> Dict[str, str]:
    headers = {"Content-Type": "application/json"}
    # Get token from session state (note: it's 'token' not 'auth_token')
    if 'token' in st.session_state and st.session_state.token:
        headers["Authorization"] = f"Bearer {st.session_state.token}"
    return headers
```

## Status
✅ **Fixed** - Both Content Library and Newsletter Generator tabs should now authenticate correctly.

## Testing
1. Login to the application
2. Select a workspace
3. Navigate to "📚 Content Library" tab - should load without "Not authenticated" error
4. Navigate to "📝 Newsletter Generator" tab - should show content stats without error

## Related Files
- [frontend/utils/auth.py](frontend/utils/auth.py) - Authentication flow (stores `st.session_state.token`)
- [frontend/utils/content_api.py](frontend/utils/content_api.py) - Content API client
- [frontend/utils/newsletter_api.py](frontend/utils/newsletter_api.py) - Newsletter API client
