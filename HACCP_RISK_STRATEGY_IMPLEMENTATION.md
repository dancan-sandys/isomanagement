# HACCP Risk Strategy Implementation Summary

## Overview
This document summarizes the implementation of an enhanced risk assessment approach for HACCP hazards, aligning with ISO 22000 standards. The system now supports multiple risk control strategies: CCP, OPPRP, ACCEPT, and FURTHER_ANALYSIS.

---

## ✅ Changes Implemented

### 1. Database Schema Updates

#### Hazards Table
- **Replaced**: `rationale` → `consequences` (describes potential consequences if hazard occurs)
- **Added**: `risk_strategy` enum column with values:
  - `ccp` - Critical Control Point
  - `opprp` - Operational Prerequisite Program  
  - `accept` - Risk accepted (typically for low risks)
  - `further_analysis` - Requires decision tree analysis
  - `not_determined` - Not yet determined (default)
- **Added**: `opprp_justification` TEXT column for OPPRP rationale

#### Decision Trees Table
- **Added Question 5** for OPPRP vs CCP determination:
  - `q5_answer` - Boolean (Yes = OPPRP, No = CCP)
  - `q5_justification` - TEXT
  - `q5_answered_by` - User ID
  - `q5_answered_at` - Timestamp
- **Added**: `is_opprp` Boolean column for OPPRP determination result

### 2. Backend Models

**Files Modified:**
- `backend/app/models/haccp.py`
  - Added `RiskStrategy` enum
  - Updated `Hazard` model with new fields
  - Updated `DecisionTree` model with Question 5
  - Added `determine_risk_strategy()` method that returns strategy (ACCEPT/OPPRP/CCP)

**Decision Tree Logic:**
```
Q1: Is control at this step necessary for safety?
  └─ NO → ACCEPT

Q2: Is control necessary to eliminate/reduce hazard?
  └─ NO → ACCEPT

Q3: Could contamination occur or increase to unacceptable levels?
  └─ NO → ACCEPT

Q4: Will a subsequent step eliminate or reduce the hazard?
  └─ YES → OPPRP

Q5: Is this control measure preventive or does it significantly reduce the hazard?
  └─ YES → OPPRP
  └─ NO → CCP
```

### 3. Backend Schemas

**Files Modified:**
- `backend/app/schemas/haccp.py`
  - Added `RiskStrategy` enum
  - Updated `HazardCreate` schema
  - Updated `HazardUpdate` schema
  - Updated `HazardResponse` schema

### 4. Backend Services

**Files Modified:**
- `backend/app/services/haccp_service.py`
  - Updated `create_hazard()` to use `consequences` instead of `rationale`
  - Added support for `risk_strategy` and `opprp_justification`

### 5. Frontend Updates

**Files Modified:**
- `frontend/src/pages/HACCP.tsx`
  - Updated hazard form state to include:
    - `consequences` field
    - `risk_strategy` selector
    - `opprp_justification` field
  - Added Risk Strategy dropdown with 5 options
  - Conditional fields:
    - CCP Justification shown only when strategy = "ccp"
    - OPPRP Justification shown only when strategy = "opprp"

### 6. Database Migration & Setup

**Files Updated:**
- `backend/migrations/add_risk_strategy_to_hazards.py`
  - Automated migration script for SQLite (for existing databases)
  - Adds all new columns to hazards and decision_trees tables
  - Copies existing `rationale` data to `consequences` field

- `backend/setup_database_complete.py`
  - Updated imports to include DecisionTree, RiskStrategy, and related enums
  - Added schema documentation in header about risk strategy updates
  - Added informative print statements about new schema features
  - New database setups will automatically include all new fields

---

## 🔧 How to Use

### Setting Up Database Schema

#### For Existing Databases (Migration):
```bash
cd backend
python migrations/add_risk_strategy_to_hazards.py
```

This will:
1. Add new columns to the database
2. Preserve existing data
3. Copy rationale → consequences

#### For Fresh Database Setup:
```bash
cd backend
python setup_database_complete.py
```

The setup script automatically includes all new schema changes - no migration needed!

### Creating a Hazard with Risk Strategy

1. **Navigate to HACCP page**
2. **Select a product** and click "Add Hazard"
3. **Fill in hazard details:**
   - Process Step
   - Hazard Type (Biological, Chemical, Physical, Allergen)
   - Hazard Name
   - Description
   - **Consequences** (What could happen if this hazard occurs?)
   - Likelihood (1-5)
   - Severity (1-5)
   - Control Measures

4. **Select Risk Strategy:**
   - **Not Determined**: Default, haven't decided yet
   - **CCP**: Critical Control Point - Shows CCP justification field
   - **OPPRP**: Operational PRP - Shows OPPRP justification field
   - **Accept Risk**: Low risk, acceptable
   - **Further Analysis**: Triggers decision tree (future implementation)

5. **Save the hazard**

---

## 📋 Remaining Tasks

### 1. Decision Tree Dialog Component (Priority: HIGH)

**What's Needed:**
Create a reusable Decision Tree dialog component that:
- Displays 5 questions sequentially
- Saves answers to the decision_trees table
- Automatically determines final strategy (ACCEPT/OPPRP/CCP)
- Updates the hazard with the determined strategy

**Implementation Steps:**
1. Create `frontend/src/components/HACCP/DecisionTreeDialog.tsx`
2. Add API endpoints for:
   - `POST /haccp/hazards/{hazard_id}/decision-tree` - Start decision tree
   - `PUT /haccp/decision-trees/{tree_id}/answer` - Submit answer to question
   - `POST /haccp/decision-trees/{tree_id}/complete` - Finalize decision
3. Integrate with hazard form when "Further Analysis" is selected

**Suggested UI Flow:**
```
User clicks "Run Decision Tree" button
  ↓
Dialog opens with Question 1
  ↓
User answers YES/NO + Justification
  ↓
Next question appears (if applicable)
  ↓
After all questions answered:
  - System determines: ACCEPT/OPPRP/CCP
  - Shows result with reasoning
  - Updates hazard automatically
```

### 2. Display Risk Strategy in UI

**Updates Needed:**
- Show risk strategy badge/chip in hazard list
- Color coding:
  - CCP: Red (Critical)
  - OPPRP: Orange (Important)
  - ACCEPT: Green (Low risk)
  - FURTHER_ANALYSIS: Blue (In progress)
  - NOT_DETERMINED: Grey (Pending)

### 3. Backend API Endpoints for Decision Tree

**Files to Update:**
- `backend/app/api/v1/endpoints/haccp.py`

**New Endpoints:**
```python
POST   /haccp/hazards/{hazard_id}/decision-tree/start
PUT    /haccp/decision-trees/{tree_id}/question/{question_num}
POST   /haccp/decision-trees/{tree_id}/complete
GET    /haccp/decision-trees/{tree_id}
```

### 4. Testing

**Test Scenarios:**
1. Create hazard with each risk strategy
2. Verify consequences field saves correctly
3. Test conditional fields (CCP vs OPPRP justification)
4. Migration rollback/forward compatibility
5. Decision tree complete flow (when implemented)

---

## 🎯 Benefits

1. **ISO 22000 Compliance**: Proper risk-based approach to hazard control
2. **Clear Differentiation**: Between CCPs and OPRPs
3. **Decision Support**: Structured decision tree guides users
4. **Traceability**: All decisions documented with justification
5. **Flexibility**: Multiple strategies for different risk levels

---

## 📝 Notes

### Backward Compatibility
- Existing hazards with `is_ccp=true` will work normally
- Migration preserves all existing data
- `rationale` field data copied to `consequences`

### Data Validation
- Risk strategy required field (defaults to `not_determined`)
- Consequences optional but recommended
- Justifications required when strategy is CCP or OPPRP

### Future Enhancements
1. Automated risk strategy suggestion based on likelihood × severity
2. Decision tree templates for different product types
3. Bulk risk strategy assignment
4. Risk strategy change history/audit trail
5. Integration with PRP module for OPPRP documentation

---

## 🚀 Quick Start Guide

1. **Run migration**:
   ```bash
   python backend/migrations/add_risk_strategy_to_hazards.py
   ```

2. **Restart backend server** (if running)

3. **Test in UI**:
   - Create new hazard
   - Select "OPPRP" strategy
   - Fill OPPRP justification
   - Save and verify

4. **Next**: Implement Decision Tree dialog for "Further Analysis" option

---

## ✅ Completion Checklist

- [x] Database schema updated
- [x] Backend models updated
- [x] Backend schemas updated  
- [x] Backend services updated
- [x] Frontend form updated
- [x] Migration script created
- [ ] Decision Tree dialog component
- [ ] Decision Tree API endpoints
- [ ] UI badges/chips for strategies
- [ ] Full end-to-end testing
- [ ] Documentation for users

---

**Last Updated**: 2025-10-14  
**Status**: Core Implementation Complete - Decision Tree Pending

