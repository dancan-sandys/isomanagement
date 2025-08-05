# User Management System Integration

## Overview

This document outlines the complete integration of the user management system between the FastAPI backend and React TypeScript frontend for the ISO 22000 FSMS application.

## System Architecture

### Backend (FastAPI)
- **Authentication**: JWT-based authentication with access and refresh tokens
- **Role-Based Access Control (RBAC)**: Comprehensive permission system
- **User Management**: Full CRUD operations with role assignment
- **Security**: Password hashing, session management, and permission validation

### Frontend (React TypeScript)
- **State Management**: Redux Toolkit for authentication and user state
- **Role-Based Navigation**: Dynamic menu filtering based on user roles
- **Protected Routes**: Component-level access control
- **Real-time Updates**: Automatic token refresh and session management

## User Roles and Permissions

### Role Hierarchy
1. **System Administrator** (ID: 1)
   - Full system access
   - User management capabilities
   - System settings access
   - Can create all other user types

2. **QA Manager** (ID: 2)
   - User management (limited)
   - HACCP system access
   - Document control
   - Supplier management
   - Traceability access

3. **QA Specialist** (ID: 3)
   - HACCP system access
   - Document control
   - Supplier management
   - Traceability access

4. **Production Manager** (ID: 4)
   - HACCP system access
   - PRP programs
   - Supplier management
   - Traceability access

5. **Production Operator** (ID: 5)
   - HACCP system access
   - PRP programs
   - Traceability access

6. **Maintenance** (ID: 6)
   - PRP programs access

7. **Lab Technician** (ID: 7)
   - Limited access to specific modules

8. **Viewer** (ID: 8)
   - Read-only access to assigned modules

## Authentication Flow

### 1. System Setup (First Time)
```
1. System Administrator signs up via /signup
2. Account is created with System Administrator role
3. Redirected to login page
4. Login with credentials
5. Access to full system with user management capabilities
```

### 2. User Login
```
1. User enters credentials on /login
2. Backend validates credentials
3. JWT tokens generated (access + refresh)
4. User data and tokens stored in Redux state
5. Tokens stored in localStorage
6. Redirected to role-specific dashboard
```

### 3. Session Management
```
1. Access token expires after 30 minutes
2. Automatic refresh using refresh token
3. Failed refresh redirects to login
4. Logout invalidates both tokens
```

## Role-Based Dashboard Access

### System Administrator Dashboard
- **User Management Overview**: Total users, active users, pending approvals
- **System Health**: Database status, storage usage, performance metrics
- **Recent Activities**: System events and user actions
- **Quick Actions**: Manage users, system settings, roles & permissions

### QA Manager Dashboard
- **Non-Conformance Trends**: Open NCs, CAPA completion rates
- **Document Updates**: Pending reviews and version alerts
- **Audit Schedule**: Upcoming audits and compliance status
- **CAPA Deadlines**: Corrective action tracking

### Production Operator Dashboard
- **Daily Tasks**: Checklist items and scheduled activities
- **Recent Activities**: Completed actions and reported issues
- **Quick Actions**: Report issues, view procedures, request training

### Auditor Dashboard
- **Compliance Score**: Overall compliance percentage
- **Audit Findings**: Recent findings and severity levels
- **Evidence Review**: Documents pending review

### Default Dashboard
- **Welcome Message**: Personalized greeting
- **Quick Actions**: Basic navigation to accessible modules
- **Role Information**: Current role and department

## Navigation and Access Control

### Dynamic Menu Filtering
The navigation menu is dynamically filtered based on user roles:

```typescript
// Example: User Management access
const hasAccess = canManageUsers(user); // System Admin or QA Manager

// Example: HACCP access
const hasAccess = hasRole(user, 'QA Manager') || 
                 hasRole(user, 'QA Specialist') || 
                 hasRole(user, 'Production Manager') || 
                 hasRole(user, 'Production Operator') ||
                 isSystemAdministrator(user);
```

### Protected Routes
Routes are protected using the `RoleBasedRoute` component:

```typescript
<Route path="/users" element={
  <RoleBasedRoute 
    allowedRoles={['System Administrator', 'QA Manager']}
    component={Users}
  />
} />
```

### Access Denied Handling
- Clear error messages explaining required roles
- Navigation options to go back or return to dashboard
- User-friendly interface with security icons

## User Management Features

### User Creation (System Administrators Only)
- **Form Validation**: Username, email, password requirements
- **Role Assignment**: Dropdown with all available roles
- **Department Assignment**: Optional department and position
- **Contact Information**: Phone and employee ID
- **Profile Information**: Bio and additional details

### User Management Operations
- **View User Details**: Complete user profile with role and status
- **Edit User Information**: Update all user fields except username
- **Activate/Deactivate**: Toggle user account status
- **Delete User**: Soft delete with confirmation
- **Password Management**: Reset passwords (admin only)

### User Dashboard
- **User Statistics**: Total, active, inactive, pending approval counts
- **Role Distribution**: Users by role and department
- **Recent Activity**: Login tracking and system usage
- **Training Alerts**: Overdue training and expiring competencies

## API Integration

### Authentication Endpoints
```typescript
// Login
POST /api/v1/auth/login
// Signup (System Administrator only)
POST /api/v1/auth/signup
// Logout
POST /api/v1/auth/logout
// Refresh token
POST /api/v1/auth/refresh
// Get current user
GET /api/v1/auth/me
```

### User Management Endpoints
```typescript
// Get users (paginated with filters)
GET /api/v1/users?page=1&size=10&search=&role=&status=&department=
// Get user by ID
GET /api/v1/users/{user_id}
// Create user
POST /api/v1/users
// Update user
PUT /api/v1/users/{user_id}
// Delete user
DELETE /api/v1/users/{user_id}
// Activate user
POST /api/v1/users/{user_id}/activate
// Deactivate user
POST /api/v1/users/{user_id}/deactivate
// User dashboard data
GET /api/v1/users/dashboard
```

### Error Handling
- **Network Errors**: Automatic retry with exponential backoff
- **Authentication Errors**: Redirect to login with clear messages
- **Permission Errors**: Access denied with role requirements
- **Validation Errors**: Form-specific error messages

## Security Features

### Frontend Security
- **Token Storage**: Secure localStorage with automatic cleanup
- **Route Protection**: Component-level access control
- **Input Validation**: Client-side form validation
- **XSS Prevention**: Sanitized user input and output

### Backend Security
- **Password Hashing**: bcrypt with salt rounds
- **JWT Tokens**: Secure token generation and validation
- **Session Management**: User session tracking
- **Permission Validation**: Server-side permission checks
- **SQL Injection Prevention**: Parameterized queries

## State Management

### Redux Store Structure
```typescript
interface AuthState {
  user: User | null;
  token: string | null;
  refreshToken: string | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  error: string | null;
}
```

### User Interface
```typescript
interface User {
  id: number;
  username: string;
  email: string;
  full_name: string;
  role_id: number;
  role_name?: string;
  status: string;
  department?: string;
  position?: string;
  phone?: string;
  employee_id?: string;
  profile_picture?: string;
  bio?: string;
  is_active: boolean;
  is_verified: boolean;
  last_login?: string;
  created_at?: string;
  updated_at?: string;
}
```

## Testing and Validation

### Manual Testing Checklist
- [ ] System Administrator signup works correctly
- [ ] Login with valid credentials
- [ ] Role-based dashboard displays correctly
- [ ] Navigation menu filters based on role
- [ ] Protected routes deny unauthorized access
- [ ] User management operations work for authorized users
- [ ] Token refresh works automatically
- [ ] Logout clears all session data
- [ ] Error handling displays appropriate messages

### API Testing
- [ ] All endpoints return correct response formats
- [ ] Permission validation works on backend
- [ ] Error responses include proper status codes
- [ ] Pagination works correctly
- [ ] Search and filtering functions properly

## Deployment Considerations

### Environment Variables
```bash
# Frontend
REACT_APP_API_URL=http://localhost:8000/api/v1

# Backend
DATABASE_URL=postgresql://user:password@localhost/dbname
SECRET_KEY=your-secret-key
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

### Database Setup
- Ensure all roles are created in the database
- System Administrator role must exist (ID: 1)
- Proper indexes on user tables for performance
- Foreign key constraints for data integrity

### Security Checklist
- [ ] HTTPS enabled in production
- [ ] Secure cookie settings
- [ ] CORS properly configured
- [ ] Rate limiting implemented
- [ ] Input validation on all endpoints
- [ ] Error messages don't leak sensitive information

## Future Enhancements

### Planned Features
1. **Two-Factor Authentication**: SMS or email verification
2. **Password Policies**: Complexity requirements and expiration
3. **Audit Logging**: Complete user action tracking
4. **Bulk Operations**: Import/export user data
5. **Advanced Permissions**: Granular permission system
6. **User Groups**: Department-based access control
7. **SSO Integration**: Active Directory or LDAP support

### Performance Optimizations
1. **Caching**: Redis for session and user data
2. **Pagination**: Efficient large dataset handling
3. **Lazy Loading**: Component-level code splitting
4. **API Optimization**: GraphQL for complex queries

## Troubleshooting

### Common Issues

#### Login Problems
- Check if user account is active
- Verify username/password combination
- Ensure backend is running and accessible
- Check browser console for network errors

#### Permission Issues
- Verify user role in database
- Check role permissions configuration
- Ensure user has required role for feature
- Clear browser cache and localStorage

#### API Errors
- Check backend logs for detailed error messages
- Verify API endpoint URLs
- Ensure proper authentication headers
- Check CORS configuration

### Debug Mode
Enable debug logging in development:
```typescript
// Frontend
localStorage.setItem('debug', 'true');

// Backend
logging.basicConfig(level=logging.DEBUG)
```

## Conclusion

The user management system provides a robust, secure, and scalable solution for the ISO 22000 FSMS application. The integration between FastAPI backend and React TypeScript frontend ensures proper role-based access control, secure authentication, and comprehensive user management capabilities.

The system is designed to be easily extensible for future requirements while maintaining security best practices and providing an excellent user experience. 