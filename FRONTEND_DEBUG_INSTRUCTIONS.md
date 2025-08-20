# Frontend Authentication Debug Instructions

## Issue Summary
The backend risk endpoints are working correctly when tested directly, but the frontend is still getting 403 Forbidden errors. This suggests the frontend is using a cached or old token that was generated before the permission fix.

## Root Cause
The frontend is likely using a cached JWT token that was generated before we fixed the permission checking logic. The old token might have been created when the permission system was broken.

## Solution Steps

### Step 1: Clear Browser Storage
1. Open your browser's Developer Tools (F12)
2. Go to the **Application** tab (Chrome) or **Storage** tab (Firefox)
3. In the left sidebar, find **Local Storage**
4. Click on `http://localhost:3000`
5. Delete all items, especially:
   - `access_token`
   - `refresh_token`
   - Any other authentication-related items

### Step 2: Clear Browser Cache
1. In Developer Tools, go to the **Network** tab
2. Right-click and select "Clear browser cache"
3. Or use Ctrl+Shift+R (Cmd+Shift+R on Mac) to hard refresh

### Step 3: Log Out and Log Back In
1. If you're currently logged in, click the logout button
2. Navigate to the login page
3. Log in with:
   - **Username**: `string`
   - **Password**: `Test123*`

### Step 4: Verify the Fix
1. After logging in, navigate to the Risk & Opportunity Register page
2. Check the browser console for any errors
3. The risk endpoints should now work correctly

## Alternative Solution: Force Token Refresh

If clearing storage doesn't work, you can force a token refresh by:

1. Open the browser console
2. Run this JavaScript code:
```javascript
// Clear all authentication data
localStorage.removeItem('access_token');
localStorage.removeItem('refresh_token');
localStorage.removeItem('user');

// Reload the page
window.location.reload();
```

## Verification

After following these steps, you should see:
- ✅ Successful login
- ✅ Risk endpoints returning 200 OK
- ✅ Risk data displaying in the frontend
- ✅ No 403 errors in the console

## Technical Details

### Why This Happens
- JWT tokens are stateless and contain user information
- Old tokens were created when the permission system was broken
- The frontend caches these tokens in localStorage
- Even after fixing the backend, old tokens still have the old permission data

### Backend Status
- ✅ Permission fix implemented and working
- ✅ All risk endpoints tested and functional
- ✅ Authentication system working correctly
- ✅ User `string` with password `Test123*` has correct permissions

### Frontend Status
- ✅ Authentication flow working
- ✅ Token storage working
- ✅ API calls configured correctly
- ⚠️ Using cached old tokens (needs clearing)

## Expected Results

After clearing the browser storage and logging in again:
- The frontend will get a fresh token with correct permissions
- All risk endpoints will work correctly
- The Risk & Opportunity Register page will display data properly
- No more 403 Forbidden errors

## If Issues Persist

If the problem continues after following these steps:

1. Check the browser console for any JavaScript errors
2. Verify the backend is running on port 8000
3. Verify the frontend is running on port 3000
4. Check that the proxy configuration is working
5. Try using a different browser or incognito mode

## Test Credentials

Use these credentials for testing:
- **Username**: `string`
- **Password**: `Test123*`
- **Role**: System Administrator (has all permissions)


