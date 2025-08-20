# Database Setup Guide - ISO 22000 FSMS Platform

## 🎯 Overview

This guide explains how to set up a new database for the ISO 22000 FSMS platform with all enum values correctly set to lowercase from the start, preventing the need for migrations.

## 🚀 Quick Setup (Recommended)

For a new database setup, use the simple setup script:

```bash
cd backend
python setup_new_database.py
```

This script will:
- ✅ Validate all enum values are lowercase
- ✅ Create database tables with correct enum definitions
- ✅ Set up permissions and roles
- ✅ Create admin user
- ✅ Verify database integrity

## 📋 Available Scripts

### 1. `setup_new_database.py` (Recommended for new setups)
- **Purpose**: Complete database setup with validation
- **Use when**: Setting up a new database from scratch
- **Features**: 
  - Validates enum values before creating tables
  - Comprehensive error checking
  - User-friendly prompts
  - Automatic verification

### 2. `init_database_improved.py` (Advanced users)
- **Purpose**: Detailed database initialization with enum validation
- **Use when**: You need more control over the setup process
- **Features**:
  - Step-by-step validation
  - Detailed logging
  - Comprehensive enum checking
  - Database integrity verification

### 3. `init_database.py` (Legacy)
- **Purpose**: Basic table creation
- **Use when**: You only need to create tables (not recommended)
- **Features**: Simple table creation only

## 🔧 Manual Setup Steps

If you prefer to set up the database manually:

### Step 1: Validate Enum Values
```bash
cd backend
python -c "
from init_database_improved import validate_enum_values
validate_enum_values()
"
```

### Step 2: Create Tables
```bash
python -c "
from init_database_improved import create_database_tables
create_database_tables()
"
```

### Step 3: Set Up Permissions and Roles
```bash
python -c "
from init_database_improved import create_permissions, create_default_roles
create_permissions()
create_default_roles()
"
```

### Step 4: Create Admin User
```bash
python -c "
from init_database_improved import create_admin_user
create_admin_user()
"
```

## 🔍 Verification

After setup, verify that everything is working:

```bash
python -c "
from init_database_improved import verify_database_integrity
verify_database_integrity()
"
```

## 📊 What Gets Created

### Database Tables
- All application tables with proper enum definitions
- Enum columns use lowercase values from the start

### Permissions
- All module permissions (VIEW, CREATE, UPDATE, DELETE)
- Organized by module (HACCP, PRP, SUPPLIERS, etc.)

### Roles
- **System Administrator**: Full access to all modules
- **QA Manager**: Quality Assurance management access
- **QA Specialist**: Limited management access
- **Production Manager**: Production and HACCP access
- **Production Operator**: Basic operational access
- **Viewer**: Read-only access

### Admin User
- **Username**: admin
- **Password**: admin123
- **Role**: System Administrator
- **Status**: active (lowercase)

## 🎉 Benefits

### ✅ No Migration Needed
- All enum values are lowercase from the start
- No need to run enum migration scripts
- Consistent data format across frontend and backend

### ✅ Production Ready
- Proper validation and error handling
- Comprehensive verification
- Ready for immediate use

### ✅ Consistent Data
- Frontend and backend use identical enum values
- No data format inconsistencies
- Proper ISO 22000 compliance

## 🚨 Troubleshooting

### Common Issues

#### 1. "Enum validation failed"
**Cause**: Some enum values are still uppercase in the model files
**Solution**: 
```bash
# Check which enums are incorrect
python -c "
from init_database_improved import validate_enum_values
validate_enum_values()
"
```

#### 2. "Database file already exists"
**Cause**: Previous database setup
**Solution**: 
```bash
# Delete existing database
rm iso22000_fsms.db
# Run setup again
python setup_new_database.py
```

#### 3. "Import error"
**Cause**: Missing dependencies or wrong directory
**Solution**:
```bash
# Ensure you're in the backend directory
cd backend
# Install dependencies
pip install -r requirements.txt
# Run setup
python setup_new_database.py
```

### Getting Help

If you encounter issues:

1. **Check the error messages** - They provide specific guidance
2. **Verify prerequisites** - Ensure you're in the backend directory
3. **Check enum values** - Run the validation function
4. **Review logs** - Look for specific error details

## 🔄 Migration from Existing Database

If you have an existing database with uppercase enum values:

1. **Backup your data**:
   ```bash
   cp iso22000_fsms.db iso22000_fsms_backup.db
   ```

2. **Run the migration script**:
   ```bash
   python migrations/enum_value_migration.py
   ```

3. **Verify migration**:
   ```bash
   python -c "
   from init_database_improved import verify_database_integrity
   verify_database_integrity()
   "
   ```

## 📝 Next Steps

After successful database setup:

1. **Start the backend server**:
   ```bash
   python -m uvicorn app.main:app --reload
   ```

2. **Start the frontend**:
   ```bash
   cd ../frontend
   npm start
   ```

3. **Login with admin credentials**:
   - Username: admin
   - Password: admin123

4. **Begin using the system**:
   - Create additional users
   - Set up HACCP plans
   - Configure PRP programs
   - Add suppliers and documents

## 🎯 Summary

The improved database setup ensures that:
- ✅ All enum values are lowercase from the start
- ✅ No migration scripts are needed for new databases
- ✅ Frontend and backend are perfectly synchronized
- ✅ The system is ready for production use
- ✅ ISO 22000 compliance is maintained

Use `python setup_new_database.py` for the easiest and most reliable setup experience.
