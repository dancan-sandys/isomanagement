# HACCP Hazard Creation Flow - User Guide

## Overview

This document provides a detailed walkthrough of the new HACCP hazard creation process with risk strategy determination and automatic CCP/OPRP creation.

## Flow Diagram

```
┌─────────────────────────────────────────────────────────────┐
│  1. Click "Add Hazard" Button                               │
└─────────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────┐
│  2. Fill Basic Information:                                 │
│     • Process Step (required)                               │
│     • Hazard Type (required)                                │
│     • Hazard Name (required)                                │
│     • Description                                           │
│     • Consequences                                          │
│     • References (optional, can add multiple)               │
└─────────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────┐
│  3. Enter Risk Assessment:                                  │
│     • Likelihood (1-5)                                      │
│     • Severity (1-5)                                        │
│     ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━  │
│     SYSTEM AUTO-CALCULATES:                                 │
│     • Risk Score = Likelihood × Severity                    │
│     • Risk Level (LOW/MEDIUM/HIGH/CRITICAL)                 │
│     • Recommended Risk Strategy                             │
└─────────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────┐
│  4. Select Risk Strategy (3 Options):                       │
│                                                             │
│  ○ OPRP (Operational Prerequisite Program)                 │
│     → Control measure for significant hazards              │
│     → Goes to Step 5                                        │
│                                                             │
│  ○ CCP (Critical Control Point)                            │
│     → Critical control for food safety hazards             │
│     → Goes to Step 5                                        │
│                                                             │
│  ○ Further Analysis (Decision Tree)                        │
│     → Opens 5-question decision tree                        │
│     → Goes to Step 4A                                       │
└─────────────────────────────────────────────────────────────┘
         │                                    │
         │ (OPRP or CCP selected)            │ (Further Analysis)
         ↓                                    ↓
┌────────────────────────┐     ┌─────────────────────────────────────┐
│  5. Strategy Selected  │     │  4A. Decision Tree Process          │
│     and Locked         │     │                                     │
│                        │     │  Q1: Is hazard significant?         │
│  • Shows selected      │     │  → NO: OPRP (End)                   │
│    strategy            │     │  → YES: Go to Q2                    │
│  • "Change" button     │     │                                     │
│    available           │     │  Q2: Subsequent step controls?      │
│  • Justification field │     │  → YES: Enter step name → OPRP      │
│    (optional)          │     │  → NO: Go to Q3                     │
│                        │     │                                     │
│  → Goes to Step 6      │     │  Q3: Control measures in place?     │
└────────────────────────┘     │  → NO: Modify process (Alert)       │
                               │  → YES: Go to Q4                    │
                               │                                     │
                               │  Q4: Can establish critical limits? │
                               │  → NO: OPRP (End)                   │
                               │  → YES: Go to Q5                    │
                               │                                     │
                               │  Q5: Can monitor immediately?       │
                               │  → YES: CCP (End)                   │
                               │  → NO: OPRP (End)                   │
                               │                                     │
                               │  → Each answer requires justification│
                               │  → Auto-locks strategy when done    │
                               │  → Goes to Step 5                   │
                               └─────────────────────────────────────┘
                                              ↓
                               ┌─────────────────────────────────────┐
                               │  5. Strategy Locked & Justification │
                               │                                     │
                               │  • Shows determined strategy        │
                               │  • "Change" button available        │
                               │  • Justification field (REQUIRED)   │
                               │  → Goes to Step 6                   │
                               └─────────────────────────────────────┘
                                              ↓
                               ┌─────────────────────────────────────┐
                               │  6. Click "Save"                    │
                               └─────────────────────────────────────┘
                                              ↓
                               ┌─────────────────────────────────────┐
                               │  7. Backend Processing:             │
                               │                                     │
                               │  • Create Hazard record             │
                               │  • Store decision tree answers      │
                               │  • Auto-create CCP or OPRP:         │
                               │    - If strategy = CCP → Create CCP │
                               │    - If strategy = OPRP → Create OPRP│
                               │  • Return success message           │
                               └─────────────────────────────────────┘
                                              ↓
                               ┌─────────────────────────────────────┐
                               │  8. Success!                        │
                               │                                     │
                               │  Message:                           │
                               │  "Hazard created successfully       │
                               │   and CCP/OPRP auto-created"        │
                               └─────────────────────────────────────┘
```

## Detailed Step-by-Step Guide

### Step 1: Open Hazard Dialog
- Click "Add Hazard" button in HACCP Product Detail page
- Dialog opens with empty form

### Step 2: Fill Basic Information

**Required Fields:**
- **Process Step:** Select from dropdown (existing process flow steps)
- **Hazard Type:** Biological, Chemical, Physical, or Allergen
- **Hazard Name:** Descriptive name of the hazard

**Optional Fields:**
- **Description:** Detailed description of the hazard
- **Consequences:** What happens if this hazard is not controlled
- **References:** Add scientific references, standards, regulations, etc.
  - Each reference includes: Title, URL, Type, Description
  - Can add multiple references
  - Can edit/delete references inline

### Step 3: Risk Assessment

**User Input:**
- **Likelihood (1-5):** How likely is this hazard to occur?
  - 1 = Very unlikely
  - 5 = Very likely

- **Severity (1-5):** How severe would the consequences be?
  - 1 = Minimal impact
  - 5 = Life-threatening

**System Auto-Calculates:**
- **Risk Score:** Likelihood × Severity (1-25)
- **Risk Level:**
  - LOW: Score 1-4
  - MEDIUM: Score 5-8
  - HIGH: Score 9-15
  - CRITICAL: Score 16-25

**Visual Feedback:**
- Risk score displayed in large, color-coded box
- Risk level shown as colored chip
- Recommendation alert appears

**Existing Control Measures:**
- Describe any current controls in place

### Step 4: Risk Strategy Selection

**System Recommendation:**
- Alert shows: "Based on the risk level (HIGH), the recommended strategy is: **Further Analysis Required**"

**Three Options:**

#### Option A: OPRP (Direct Selection)
- Click OPRP radio button
- Strategy locks immediately
- Goes to Step 5 (Justification)

#### Option B: CCP (Direct Selection)
- Click CCP radio button
- Strategy locks immediately
- Goes to Step 5 (Justification)

#### Option C: Further Analysis (Decision Tree)
- Click Further Analysis radio button
- Decision Tree Dialog opens
- Goes to Step 4A

### Step 4A: Decision Tree Process

**Interface:**
- Vertical stepper showing 5 questions
- Current question highlighted
- Previous questions show as completed
- Each question has:
  - Question text
  - Help text (explanatory guidance)
  - Justification text field (required)
  - Yes/No buttons

**Question Flow:**

#### Q1: Is this hazard significant?
- **NO:** 
  - Strategy set to OPRP
  - Justification auto-filled: "Not a significant hazard based on risk assessment."
  - Dialog closes
  - Goes to Step 5
- **YES:** Continue to Q2

#### Q2: Will a subsequent step control this hazard?
- **Special Field:** "Subsequent Step Name" input appears
- **YES:** 
  - MUST enter subsequent step name
  - Strategy set to OPRP
  - Justification auto-filled: "Subsequent step ({name}) will control this hazard."
  - Dialog closes
  - Goes to Step 5
- **NO:** Continue to Q3

#### Q3: Are control measures in place?
- **NO:** 
  - Alert shown: "Control measures are not adequate. Please modify the process or product and reassess."
  - Dialog closes
  - User must modify and restart
- **YES:** Continue to Q4

#### Q4: Can establish critical limits?
- **NO:** 
  - Strategy set to OPRP
  - Justification auto-filled: "Critical limits cannot be established for this control measure."
  - Dialog closes
  - Goes to Step 5
- **YES:** Continue to Q5

#### Q5: Can monitor immediately for corrective action?
- **YES:** 
  - Strategy set to CCP
  - Justification auto-filled: "Monitoring allows immediate corrective action - managed by HACCP plan (CCP)."
  - Dialog closes
  - Goes to Step 5
- **NO:** 
  - Strategy set to OPRP
  - Justification auto-filled: "Immediate monitoring not possible - managed by OPRP."
  - Dialog closes
  - Goes to Step 5

### Step 5: Strategy Locked & Justification

**Display:**
- Green alert box showing: "Risk strategy determined: **[CCP/OPRP]**"
- "Change" button in alert (allows user to reset and reselect)

**Justification Field:**
- Large text area for justification
- **For Further Analysis:** REQUIRED (auto-populated but can be edited)
- **For Manual Selection:** Optional but recommended
- Helper text indicates requirement

**If Subsequent Step:**
- Info alert shows: "Subsequent Step: {name}"

### Step 6: Save Hazard

**Validation:**
- All required fields filled
- Risk strategy selected
- If decision tree was used, justification must be provided

**Click "Save" Button**

### Step 7: Backend Processing

**Backend automatically:**

1. **Creates Hazard Record:**
   - Stores all basic information
   - Stores risk assessment (likelihood, severity, score, level)
   - Stores risk strategy
   - Stores justification
   - Stores subsequent step name (if applicable)
   - Stores decision tree answers as JSON (if applicable)

2. **Auto-Creates CCP (if strategy = CCP):**
   - CCP Number: `CCP-{product_id}-{hazard_id}`
   - CCP Name: Same as hazard name
   - Description: "CCP for {hazard_name}"
   - Status: ACTIVE
   - Linked to hazard

3. **Auto-Creates OPRP (if strategy = OPRP):**
   - OPRP Number: `OPRP-{product_id}-{hazard_id}`
   - OPRP Name: Same as hazard name
   - Description: "OPRP for {hazard_name}"
   - Justification: From risk strategy justification
   - Status: ACTIVE
   - Linked to hazard

### Step 8: Success Message

**User sees:**
- Success message: "Hazard created successfully and CCP auto-created" (or OPRP)
- Dialog closes
- Hazard appears in table
- CCP/OPRP appears in respective tables
- User can view and edit the auto-created CCP/OPRP

## Key Benefits

### 1. Streamlined Workflow
- No need to manually create CCP/OPRP after hazard
- Automatic linkage ensures consistency
- Reduced data entry errors

### 2. Guided Decision-Making
- Clear decision tree with help text
- Auto-recommendations based on risk level
- Required justifications ensure documentation

### 3. ISO 22000 Compliance
- Follows ISO 22000:2018 requirements
- Proper CCP vs OPRP determination
- Complete audit trail with justifications

### 4. Flexibility
- Can override auto-recommendations
- Can change strategy before saving
- Can manually select CCP or OPRP directly

### 5. Data Quality
- Consistent CCP/OPRP numbering
- Complete decision documentation
- Traceable risk strategy rationale

## Example Scenarios

### Scenario 1: Low Risk Hazard (Direct OPRP)

1. Enter: Likelihood = 2, Severity = 2
2. System shows: Risk Score = 4, Level = LOW
3. Recommendation: OPRP
4. User selects: OPRP
5. Justification (optional): "Low risk, managed through standard procedures"
6. Save → Hazard + OPRP auto-created

### Scenario 2: High Risk with Decision Tree

1. Enter: Likelihood = 4, Severity = 4
2. System shows: Risk Score = 16, Level = CRITICAL
3. Recommendation: Further Analysis
4. User selects: Further Analysis
5. Decision Tree:
   - Q1: Is hazard significant? **YES** (Justification: "High bacterial contamination risk")
   - Q2: Subsequent step controls? **NO** (Justification: "No subsequent thermal processing")
   - Q3: Control measures in place? **YES** (Justification: "Temperature control during storage")
   - Q4: Can establish critical limits? **YES** (Justification: "Temperature range 2-4°C")
   - Q5: Can monitor immediately? **YES** (Justification: "Continuous temperature monitoring with alarms")
6. Result: **CCP** determined
7. Justification auto-filled: "Monitoring allows immediate corrective action - managed by HACCP plan (CCP)."
8. Save → Hazard + CCP auto-created (CCP-1-42)

### Scenario 3: Medium Risk with Subsequent Control

1. Enter: Likelihood = 3, Severity = 2
2. System shows: Risk Score = 6, Level = MEDIUM
3. Recommendation: OPRP
4. User selects: Further Analysis (wants to document subsequent control)
5. Decision Tree:
   - Q1: Is hazard significant? **YES** (Justification: "Potential chemical contamination")
   - Q2: Subsequent step controls? **YES**
     - Subsequent Step Name: "Final Heat Treatment Step"
     - Justification: "Heat treatment at 85°C for 15min will eliminate chemical residues"
6. Result: **OPRP** determined
7. Justification auto-filled: "Subsequent step (Final Heat Treatment Step) will control this hazard."
8. Save → Hazard + OPRP auto-created (OPRP-1-43)

## Data Storage

### Hazard Record Includes:
```json
{
  "id": 42,
  "product_id": 1,
  "process_step_id": 5,
  "hazard_type": "biological",
  "hazard_name": "Salmonella contamination",
  "description": "...",
  "consequences": "Foodborne illness outbreak",
  "likelihood": 4,
  "severity": 4,
  "risk_score": 16,
  "risk_level": "critical",
  "control_measures": "Temperature control",
  "risk_strategy": "ccp",
  "risk_strategy_justification": "Monitoring allows immediate corrective action...",
  "subsequent_step": null,
  "decision_tree_steps": "{\"q1_answer\": true, \"q1_justification\": \"...\", ...}",
  "created_at": "2025-10-17T10:30:00Z"
}
```

### Auto-Created CCP Record:
```json
{
  "id": 15,
  "product_id": 1,
  "hazard_id": 42,
  "ccp_number": "CCP-1-42",
  "ccp_name": "Salmonella contamination",
  "description": "CCP for Salmonella contamination",
  "status": "active",
  "created_at": "2025-10-17T10:30:00Z"
}
```

### Auto-Created OPRP Record:
```json
{
  "id": 23,
  "product_id": 1,
  "hazard_id": 43,
  "oprp_number": "OPRP-1-43",
  "oprp_name": "Chemical residue contamination",
  "description": "OPRP for Chemical residue contamination",
  "justification": "Subsequent step (Final Heat Treatment Step) will control this hazard.",
  "status": "active",
  "created_at": "2025-10-17T10:30:00Z"
}
```

## Field Mapping

### Removed Fields
These fields are NO LONGER part of the hazard creation form:
- ❌ Is Controlled (switch)
- ❌ Control Effectiveness (1-5 rating)
- ❌ Is CCP (switch)

### New Fields
These fields are NOW part of the hazard creation:
- ✅ Risk Strategy (auto-determined, user-selectable)
- ✅ Risk Strategy Justification (required for decision tree)
- ✅ Subsequent Step (from decision tree Q2)
- ✅ Decision Tree Answers (stored as JSON)

### Auto-Determined Fields
These fields are automatically set by the system:
- ✅ Risk Score
- ✅ Risk Level
- ✅ Is CCP (based on risk_strategy)
- ✅ CCP Justification (from risk_strategy_justification if CCP)
- ✅ OPRP Justification (from risk_strategy_justification if OPRP)

## API Response

### Success Response
```json
{
  "success": true,
  "message": "Hazard created successfully and CCP auto-created",
  "data": {
    "id": 42,
    "risk_strategy": "ccp",
    "control_point": {
      "type": "ccp",
      "id": 15,
      "number": "CCP-1-42"
    }
  }
}
```

## Next Steps After Hazard Creation

### If CCP was auto-created:
1. Navigate to CCPs tab
2. Find the auto-created CCP (CCP-1-42)
3. Edit CCP to add:
   - Critical limits (min/max values, units)
   - Monitoring frequency and method
   - Monitoring responsible person
   - Corrective actions
   - Verification frequency and method
   - Verification responsible person

### If OPRP was auto-created:
1. Navigate to OPRPs tab (or management section)
2. Find the auto-created OPRP (OPRP-1-43)
3. Edit OPRP to add:
   - Operational limits
   - Monitoring frequency and method
   - Monitoring responsible person
   - Corrective actions
   - Verification requirements

## Tips for Users

1. **Start with accurate risk assessment:**
   - Be realistic with likelihood and severity scores
   - Consider historical data and scientific evidence

2. **Use decision tree for high/critical risks:**
   - Provides documented decision-making process
   - Ensures ISO 22000 compliance
   - Creates audit trail

3. **Provide detailed justifications:**
   - Required for decision tree
   - Recommended for manual selections
   - Helps during audits and reviews

4. **Review auto-created CCP/OPRP:**
   - Auto-creation saves time but requires completion
   - Add critical/operational limits immediately
   - Assign responsible personnel
   - Set monitoring schedules

5. **Use references:**
   - Link to scientific studies
   - Reference regulatory requirements
   - Cite industry standards
   - Improves credibility of hazard analysis

## Validation Rules

### Before Save:
- ✓ Process Step selected
- ✓ Hazard Name provided
- ✓ Risk Strategy selected
- ✓ If decision tree used: Justification provided
- ✓ If Q2 answered "Yes": Subsequent step name provided

### Backend Validation:
- ✓ Product exists
- ✓ Process step belongs to product
- ✓ Likelihood 1-5
- ✓ Severity 1-5
- ✓ Risk strategy is valid enum value

## Error Handling

### Common Errors:
1. **"Please select a risk strategy"**
   - Solution: Choose OPRP, CCP, or Further Analysis

2. **"Justification is required when using Further Analysis"**
   - Solution: Fill in the justification field after decision tree

3. **"Please enter the subsequent step name before answering 'Yes'"**
   - Solution: Fill in the subsequent step name field in Q2

4. **"Control measures are not adequate"**
   - Solution: Modify your process/product or choose different answer

## Conclusion

The new HACCP hazard creation flow provides:
- ✅ ISO 22000:2018 compliance
- ✅ Clear, guided workflow
- ✅ Automatic CCP/OPRP creation
- ✅ Complete documentation trail
- ✅ Reduced manual effort
- ✅ Improved data quality
- ✅ Better audit readiness


