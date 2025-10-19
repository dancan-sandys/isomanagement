# CCP Display Issue - Debug and Fix Summary

## Problem Identified
CCPs were not being fetched and displayed correctly in the NodeEditDialog of the FlowchartBuilder.

## Root Cause
The `hazard_id` field was missing from the CCP data flow:
1. **Backend Schema Issue**: `CCPResponse` schema was missing the `hazard_id` field, even though it exists in the database model
2. **Frontend Type Issue**: The CCP interface in the Redux store was also missing `hazard_id`
3. This caused the CCP-to-Hazard mapping logic to fail silently

## Fixes Applied

### 1. Backend Schema Fix (`backend/app/schemas/haccp.py`)
**Line 615**: Added `hazard_id: int` to the `CCPResponse` schema

```python
class CCPResponse(BaseModel):
    id: int
    hazard_id: int  # ✅ ADDED - Links CCP to its hazard
    ccp_number: str
    ccp_name: str
    # ... rest of fields
```

### 2. Frontend Store Interface Fix (`frontend/src/store/slices/haccpSlice.ts`)
**Line 73**: Added `hazard_id: number` to the CCP interface

```typescript
export interface CCP {
  id: number;
  hazard_id: number;  // ✅ ADDED - Links CCP to its hazard
  ccp_number: string;
  ccp_name: string;
  // ... rest of fields
}
```

### 3. Debug Logging Added (`frontend/src/components/HACCP/FlowchartBuilder/index.tsx`)
Added comprehensive console logging to trace the data flow:
- **Lines 125-126**: Log total hazards and CCPs received
- **Lines 142-146**: Log CCP-to-Hazard mapping process
- **Lines 149-150**: Log the final lookup maps
- **Lines 184-208**: Log per-node CCP matching logic

### 4. NodeEditDialog Logging (`frontend/src/components/HACCP/FlowchartBuilder/NodeEditDialog.tsx`)
Added logging to see what data the dialog receives:
- **Lines 101-104**: Log node data, hazards, and CCP data when dialog opens

## Data Flow Trace

```
1. Backend Database (CCP Model)
   ├─ hazard_id (Column exists) ✅
   └─ All other CCP fields

2. Backend API Response (CCPResponse Schema)
   ├─ hazard_id (NOW INCLUDED) ✅
   └─ Returned to frontend

3. Frontend Redux Store
   ├─ CCP interface includes hazard_id ✅
   └─ Stored in state

4. FlowchartBuilder Component
   ├─ Receives hazards[] and ccps[] as props
   ├─ Creates ccpByHazardId map using hazard_id ✅
   └─ Maps CCPs to process steps via hazards

5. NodeEditDialog Component
   ├─ Receives node with node.data.ccp
   └─ Displays CCP information
```

## How to Test

### Step 1: Restart Backend Server
The schema change requires restarting the backend:
```bash
cd backend
# Stop the current server (Ctrl+C)
# Restart
uvicorn app.main:app --reload
```

### Step 2: Open Browser Console
1. Open DevTools (F12)
2. Go to Console tab
3. Clear console

### Step 3: Test in Application
1. Navigate to HACCP module
2. Select a product that has:
   - Process flows
   - Hazards with risk_strategy = 'ccp'
   - CCPs created for those hazards
3. Click "Open Flowchart Builder"
4. Click on a process step node that has hazards/CCPs
5. Check console logs for:
   ```
   [Flowchart] Total hazards: X
   [Flowchart] Total CCPs: Y
   [Flowchart] Mapped CCP <number> to hazard <id>
   [Flowchart] Node <id>: Found CCP for hazard <id>
   [NodeEditDialog] CCP data: { ... }
   ```

### Step 4: Verify Display
In the NodeEditDialog, the CCP Details accordion should show:
- ✅ CCP Number (as a red chip badge)
- ✅ Critical Limits table with Parameter/Min/Max/Unit
- ✅ Monitoring Frequency
- ✅ Monitoring Method
- ✅ Responsible Person (if set)
- ✅ Verification Method
- ✅ Corrective Actions

## Debug Console Output Examples

### Success Case:
```
[Flowchart] Total hazards: 3 [{...}, {...}, {...}]
[Flowchart] Total CCPs: 1 [{hazard_id: 5, ccp_number: "CCP-1", ...}]
[Flowchart] Mapped CCP CCP-1 to hazard 5
[Flowchart] Node step_123 (step 123): Found 2 hazards [5, 6]
[Flowchart] Node step_123: Found CCP for hazard 5: {ccp_number: "CCP-1", ...}
[Flowchart] Node step_123: Mapped CCP data: {number: "CCP-1", criticalLimits: [...], ...}
[NodeEditDialog] CCP data: {number: "CCP-1", criticalLimits: [...], ...}
```

### Failure Case (Before Fix):
```
[Flowchart] Total CCPs: 1 [{id: 1, ccp_number: "CCP-1", ...}]  ❌ No hazard_id
[Flowchart] CCP has no valid hazard_id: {id: 1, ccp_number: "CCP-1", ...}
[Flowchart] Node step_123: No CCP found for any hazard at this step
[NodeEditDialog] CCP data: {number: "", criticalLimits: [], ...}  ❌ Empty
```

## Additional Notes

### CCP Mapping Logic
The mapping works as follows:
1. CCPs are linked to Hazards via `hazard_id`
2. Hazards are linked to Process Steps via `process_step_id`
3. Therefore: CCP → Hazard → Process Step
4. When displaying a process step, we find all its hazards, then find CCPs for those hazards

### Multiple CCPs per Step
Currently, the code only shows the FIRST CCP found for a step (if multiple hazards at the same step have different CCPs). This is by design for simplicity, but could be enhanced later.

### CCP Display is Read-Only
As per requirements, all CCP data in the NodeEditDialog is display-only. CCPs are managed in their dedicated module, not in the flowchart builder.

## Cleanup
Once verified working, you can remove the debug console.log statements:
- Lines 125-126, 142-150 in `index.tsx`
- Lines 184-208 in `index.tsx`
- Lines 101-104 in `NodeEditDialog.tsx`

