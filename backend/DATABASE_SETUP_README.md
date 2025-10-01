# Database Setup Guide

This guide explains how to set up the ISO 22000 FSMS database with professional demo data.

## Quick Setup

### Option 1: Complete Setup (Recommended)
Run the complete database setup script that creates all tables and populates them with professional data:

```bash
cd backend
python setup_database_complete.py
```

This script will:
- Create all database tables
- Create default roles and permissions
- Populate the database with professional food safety demo data
- Set up 12 professional users with realistic roles
- Create 8 food products (dairy, meat, bakery)
- Add 15 food industry suppliers
- Generate 24 professional documents (SOPs, manuals, etc.)
- Create production batches and HACCP plans
- Set up equipment records and training programs

### Option 2: Tables Only
If you only want to create the database tables without demo data:

```bash
cd backend
python init_database.py
```

### Option 3: Data Population Only
If tables already exist and you only want to populate with demo data:

```bash
cd backend
python populate_professional_data.py
```

## Default Login Credentials

After running the complete setup, you can log in with:

- **Username:** `admin`
- **Password:** `admin123`

All demo users use the password: `admin123`

## Demo Users Created

The system creates 12 professional users with realistic food safety roles:

### Management
- **Food Safety Manager** (fs_manager) - Sarah Johnson
- **QA Director** (qa_director) - Michael Chen  
- **Plant Manager** (plant_manager) - Robert Williams

### Quality Assurance
- **QA Supervisor** (qa_supervisor) - Lisa Rodriguez
- **HACCP Coordinator** (haccp_coordinator) - David Kim
- **Microbiologist** (microbiologist) - Jennifer Lee

### Production
- **Production Supervisor** (production_supervisor) - James Brown
- **Sanitation Lead** (sanitation_lead) - Maria Garcia
- **Line Operator** (line_operator) - Thomas Wilson

### Maintenance
- **Maintenance Manager** (maintenance_manager) - Kevin Davis
- **Calibration Technician** (calibration_tech) - Amanda Taylor

### System
- **System Administrator** (admin) - System Administrator

## Demo Data Overview

### Products (8)
- Fresh Whole Milk (DAI-001)
- Greek Yogurt (DAI-002)
- Cheddar Cheese (DAI-003)
- Butter (DAI-004)
- Ground Beef (MEA-001)
- Chicken Breast (MEA-002)
- Whole Wheat Bread (BAK-001)
- Chocolate Chip Cookies (BAK-002)

### Suppliers (15)
- Raw Materials: Green Valley Dairy Farm, Premium Beef Ranch, Golden Grain Mills
- Packaging: EcoPack Solutions, FreshSeal Packaging
- Ingredients: Pure Cultures Inc, Sweet Sugar Co
- Services: CleanTech Sanitation, CalibPro Services
- Equipment: FoodTech Equipment, ColdChain Solutions
- Testing: FoodLab Testing, MicroTest Labs
- Transportation: FreshLogistics, SafeHaul Transport

### Documents (24)
- Food Safety Manuals (3)
- Standard Operating Procedures (5)
- Work Instructions (3)
- Forms and Records (4)
- Training Materials (3)
- Policies (3)
- Specifications (3)

### Production Data
- 20+ Production Batches
- Complete HACCP Plans
- 8 Critical Control Points (CCPs)
- 30+ CCP Monitoring Logs
- Equipment Records
- Training Programs

## Troubleshooting

### Tables Don't Exist Error
If you get "no such table" errors, run the complete setup first:
```bash
python setup_database_complete.py
```

### Permission Errors
Make sure you have write permissions to the backend directory and that the database file can be created.

### Port Conflicts
If you get port conflicts when starting the server, make sure no other instance is running on the same port.

## Database File Location

The SQLite database file is created as `iso22000_fsms.db` in the backend directory.

## Next Steps

After setting up the database:

1. Start the backend server: `python main.py`
2. Start the frontend development server: `npm start` (in frontend directory)
3. Access the application at `http://localhost:3000`
4. Log in with the admin credentials above

## Support

If you encounter any issues with the database setup, check the console output for specific error messages and ensure all dependencies are installed correctly.