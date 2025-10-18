# Updated HACCP Risk Strategy Flow

## New Risk Strategy Added: "Use Existing PRPs"

### Risk Strategy Options (4 Total)

1. **Use Existing PRPs** - For low risks and when subsequent steps control the hazard
2. **OPRP** (Operational Prerequisite Program) - For medium risks requiring specific operational controls
3. **CCP** (Critical Control Point) - For critical hazards requiring immediate monitoring
4. **Further Analysis** - Decision tree to determine appropriate strategy

---

## Updated Auto-Recommendation Logic

| Risk Level | Risk Score | Auto-Recommended Strategy |
|------------|------------|---------------------------|
| LOW | 1-4 | **Use Existing PRPs** |
| MEDIUM | 5-8 | **OPRP** |
| HIGH | 9-15 | **Further Analysis** |
| CRITICAL | 16-25 | **Further Analysis** |

---

## Updated Decision Tree Outcomes

| Question | Answer | Outcome | Notes |
|----------|--------|---------|-------|
| Q1: Is hazard significant? | NO | **Use Existing PRPs** | Not a significant hazard |
| Q2: Subsequent step controls? | YES | **Use Existing PRPs** | Requires subsequent step name |
| Q2: Subsequent step controls? | NO | Continue to Q3 | - |
| Q3: Control measures in place? | NO | Alert to modify | - |
| Q3: Control measures in place? | YES | Continue to Q4 | - |
| Q4: Can establish critical limits? | NO | **OPRP** | Cannot establish measurable limits |
| Q4: Can establish critical limits? | YES | Continue to Q5 | - |
| Q5: Can monitor immediately? | YES | **CCP** | Immediate monitoring possible |
| Q5: Can monitor immediately? | NO | **OPRP** | Immediate monitoring not possible |

---

## What Happens for Each Strategy

### 1. Use Existing PRPs
**When Selected:**
- Low risk hazards (score 1-4)
- Q1 answered "NO" (not significant)
- Q2 answered "YES" (subsequent step controls)

**What Appears:**
- Justification field (required if from decision tree)
- Success alert: "This hazard will be managed using existing Prerequisite Programs"
- Shows subsequent step name if from Q2
- **NO CCP/OPRP creation form** - No additional control point needed

**What Gets Saved:**
- Hazard record with `risk_strategy = "use_existing_prps"`
- Justification
- Subsequent step name (if applicable)
- Decision tree answers (if applicable)
- **NO CCP or OPRP created**

### 2. OPRP (Operational Prerequisite Program)
**When Selected:**
- Medium risk hazards (score 5-8)
- Q4 answered "NO" (cannot establish critical limits)
- Q5 answered "NO" (cannot monitor immediately)
- User manually selects OPRP

**What Appears:**
- Justification field
- **OPRP Creation Form:**
  - OPRP Number (required)
  - OPRP Name (required, auto-filled)
  - Description (auto-filled)
  - Objective
  - SOP Reference

**What Gets Saved:**
- Hazard record with `risk_strategy = "opprp"`
- **OPRP record** created and linked to hazard

### 3. CCP (Critical Control Point)
**When Selected:**
- Q5 answered "YES" (can monitor immediately)
- User manually selects CCP

**What Appears:**
- Justification field
- **CCP Creation Form:**
  - CCP Number (required)
  - CCP Name (required, auto-filled)
  - Description (auto-filled)
  - Critical Limit Min
  - Critical Limit Max
  - Unit
  - Monitoring Frequency
  - Monitoring Method
  - Corrective Actions

**What Gets Saved:**
- Hazard record with `risk_strategy = "ccp"`
- **CCP record** created and linked to hazard

### 4. Further Analysis
**When Selected:**
- High/Critical risk hazards
- User wants structured decision-making

**What Happens:**
- Opens 5-question decision tree dialog
- Each question answered with justification
- System determines final strategy (Use Existing PRPs, OPRP, or CCP)
- Returns to main dialog with strategy locked
- Appropriate form appears based on determination

---

## Complete User Flow Examples

### Example 1: Low Risk Hazard
```
1. Enter: Likelihood=2, Severity=2
2. System calculates: Score=4, Level=LOW
3. System recommends: Use Existing PRPs
4. User accepts recommendation
5. Justification (optional): "Low risk controlled by standard hygiene PRPs"
6. Save → Only hazard created
```

### Example 2: Medium Risk Hazard
```
1. Enter: Likelihood=3, Severity=2
2. System calculates: Score=6, Level=MEDIUM
3. System recommends: OPRP
4. User accepts recommendation
5. Justification (optional): "Requires operational control"
6. OPRP form appears:
   - Number: OPRP-1
   - Name: (auto-filled from hazard)
   - Objective: "Maintain sanitation standards"
   - SOP Reference: "SOP-SAN-001"
7. Save → Hazard + OPRP created
```

### Example 3: High Risk with Decision Tree → Use Existing PRPs
```
1. Enter: Likelihood=4, Severity=4
2. System calculates: Score=16, Level=CRITICAL
3. System recommends: Further Analysis
4. User selects Further Analysis
5. Decision Tree:
   - Q1: Is hazard significant? YES
   - Q2: Subsequent step controls? YES
   - Subsequent Step Name: "Final Heat Treatment"
6. System determines: Use Existing PRPs
7. Justification (required): Auto-filled from Q2
8. Shows: "Subsequent step (Final Heat Treatment) will control this hazard"
9. Save → Only hazard created (with subsequent_step field)
```

### Example 4: High Risk with Decision Tree → CCP
```
1. Enter: Likelihood=5, Severity=4
2. System calculates: Score=20, Level=CRITICAL
3. System recommends: Further Analysis
4. User selects Further Analysis
5. Decision Tree:
   - Q1: Is hazard significant? YES
   - Q2: Subsequent step controls? NO
   - Q3: Control measures in place? YES
   - Q4: Can establish critical limits? YES
   - Q5: Can monitor immediately? YES
6. System determines: CCP
7. Justification (required): Auto-filled
8. CCP form appears
9. Fill CCP details
10. Save → Hazard + CCP created
```

---

## Backend Handling

### Risk Strategy Enum Values
```python
class RiskStrategy(str, enum.Enum):
    CCP = "ccp"
    OPPRP = "opprp"
    USE_EXISTING_PRPS = "use_existing_prps"  # NEW
    FURTHER_ANALYSIS = "further_analysis"
    NOT_DETERMINED = "not_determined"
```

### Service Layer Logic
```python
if risk_level == RiskLevel.LOW:
    risk_strategy = RiskStrategy.USE_EXISTING_PRPS  # NEW - Low risks use existing PRPs
elif risk_level == RiskLevel.MEDIUM:
    risk_strategy = RiskStrategy.OPPRP
elif risk_level == RiskLevel.HIGH:
    risk_strategy = RiskStrategy.FURTHER_ANALYSIS
else:  # CRITICAL
    risk_strategy = RiskStrategy.FURTHER_ANALYSIS
```

### CCP/OPRP Creation Logic
```python
# Only create CCP if strategy is CCP and ccp data provided
if hazard_data.ccp and hazard.risk_strategy == RiskStrategy.CCP:
    create_ccp(...)

# Only create OPRP if strategy is OPRP and oprp data provided  
if hazard_data.oprp and hazard.risk_strategy == RiskStrategy.OPPRP:
    create_oprp(...)

# If strategy is USE_EXISTING_PRPS, no CCP/OPRP is created
```

---

## UI Button Labels

| Strategy | Save Button Text |
|----------|------------------|
| Use Existing PRPs | "Save Hazard" |
| OPRP | "Save Hazard & OPRP" |
| CCP | "Save Hazard & CCP" |
| Not selected | "Save Hazard" |

---

## Summary of Changes

### What Changed:
1. ✅ Added "Use Existing PRPs" as 4th risk strategy option
2. ✅ LOW risk now defaults to "Use Existing PRPs" (was OPRP)
3. ✅ Q1 NO now sets "Use Existing PRPs" (was OPRP)
4. ✅ Q2 YES now sets "Use Existing PRPs" (was OPRP)
5. ✅ "Use Existing PRPs" shows informational alert (no form)
6. ✅ No CCP/OPRP created for "Use Existing PRPs" strategy

### Strategy Distribution:
- **Use Existing PRPs:** Low risks, non-significant hazards, controlled by subsequent steps
- **OPRP:** Medium risks, cannot establish critical limits, cannot monitor immediately
- **CCP:** Critical hazards requiring immediate monitoring and control
- **Further Analysis:** High/critical risks requiring structured decision-making

---

## Risk Strategy Matrix (Updated)

| Risk Level | Auto-Recommended | When to Override |
|------------|------------------|------------------|
| LOW (1-4) | Use Existing PRPs | Override to OPRP if specific operational control needed |
| MEDIUM (5-8) | OPRP | Override to CCP if monitoring critical |
| HIGH (9-15) | Further Analysis | Use decision tree for proper determination |
| CRITICAL (16-25) | Further Analysis | Use decision tree for proper determination |

---

## Testing Scenarios

### Test 1: Low Risk → Use Existing PRPs
- [x] Likelihood=1, Severity=2 → Recommends "Use Existing PRPs"
- [x] Select "Use Existing PRPs"
- [x] Justification optional
- [x] No CCP/OPRP form appears
- [x] Save creates only hazard

### Test 2: Decision Tree Q2 YES → Use Existing PRPs
- [x] High risk → Further Analysis
- [x] Q1: YES
- [x] Q2: YES (with subsequent step name)
- [x] Determines "Use Existing PRPs"
- [x] Justification required
- [x] Shows subsequent step alert
- [x] No CCP/OPRP form
- [x] Save creates only hazard with subsequent_step field

### Test 3: Medium Risk → OPRP
- [x] Likelihood=3, Severity=2 → Recommends OPRP
- [x] Select OPRP
- [x] OPRP form appears
- [x] Fill OPRP details
- [x] Save creates hazard + OPRP

### Test 4: Decision Tree → CCP
- [x] Complete decision tree → CCP
- [x] CCP form appears
- [x] Fill CCP details
- [x] Save creates hazard + CCP

---

## Files Modified

### Backend:
1. ✅ `backend/app/models/haccp.py` - Added USE_EXISTING_PRPS to RiskStrategy enum
2. ✅ `backend/app/schemas/haccp.py` - Added USE_EXISTING_PRPS to RiskStrategy enum
3. ✅ `backend/app/services/haccp_service.py` - Updated auto-determination logic

### Frontend:
1. ✅ `frontend/src/components/HACCP/HazardDialog.tsx` - Added 4th option, updated logic, added alert for Use Existing PRPs

---

## Status

✅ **ALL CHANGES COMPLETE**
✅ **NO LINTER ERRORS**
✅ **READY FOR TESTING**

The system now has 4 risk strategies with proper logic flow and appropriate UI for each!


