import React, { useState, useEffect } from 'react';
import {
  Box,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  Typography,
  Alert,
  CircularProgress,
} from '@mui/material';
import { useDispatch, useSelector } from 'react-redux';
import { AppDispatch, RootState } from '../../../store';

import FlowchartBuilder from './FlowchartBuilder';
import TemplateSelectionDialog from './TemplateSelectionDialog';
import { HACCPFlowchart, ProductTemplate } from './types';
import { productTemplates, getTemplateById } from './ProductTemplates';
import { haccpAPI } from '../../../services/haccpAPI';
import type { Hazard as StoreHazard, CCP as StoreCCP } from '../../../store/slices/haccpSlice';

interface HACCPFlowchartBuilderProps {
  open: boolean;
  onClose: () => void;
  onSuccess?: () => void;
  productId?: string;
  productName?: string;
  initialFlowchartId?: string;
  readOnly?: boolean;
  hazards?: StoreHazard[];
  ccps?: StoreCCP[];
}

const HACCPFlowchartBuilderContainer: React.FC<HACCPFlowchartBuilderProps> = ({
  open,
  onClose,
  onSuccess,
  productId,
  productName = '',
  initialFlowchartId,
  readOnly = false,
  hazards = [],
  ccps = [],
}) => {
  const dispatch = useDispatch<AppDispatch>();
  const { user: currentUser } = useSelector((state: RootState) => state.auth);
  
  const [templateDialogOpen, setTemplateDialogOpen] = useState(false);
  const [currentFlowchart, setCurrentFlowchart] = useState<HACCPFlowchart | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);
  const [isNewFlowchart, setIsNewFlowchart] = useState(true);

  useEffect(() => {
    if (open) {
      // Attempt to load existing flowchart data for the product
      if (productId) {
        loadProductFlowchart(productId);
      } else if (initialFlowchartId) {
        loadFlowchart(initialFlowchartId);
      } else {
        setIsNewFlowchart(true);
        setTemplateDialogOpen(true);
      }
    }
  }, [open, initialFlowchartId, productId]);

  // Reload mapping if hazards/ccps change while dialog open
  useEffect(() => {
    if (open && productId) {
      loadProductFlowchart(productId);
    }
  }, [hazards, ccps]);

  const loadFlowchart = async (flowchartId: string) => {
    setLoading(true);
    setError(null);
    
    try {
      // TODO: Replace with actual API call
      // const response = await haccpAPI.getFlowchart(flowchartId);
      // setCurrentFlowchart(response.data);
      
      // For now, use a basic template as placeholder
      const template = productTemplates[0];
      const flowchart: HACCPFlowchart = {
        id: flowchartId,
        productId: productId || '',
        productName: productName,
        title: `${productName} - HACCP Flowchart`,
        description: `HACCP process flowchart for ${productName}`,
        version: '1.0',
        nodes: template.defaultNodes,
        edges: template.defaultEdges,
        metadata: {
          status: 'draft',
          createdAt: new Date().toISOString(),
          createdBy: currentUser?.username,
        },
      };
      setCurrentFlowchart(flowchart);
      setIsNewFlowchart(false);
    } catch (err) {
      setError('Failed to load flowchart');
      console.error('Error loading flowchart:', err);
    } finally {
      setLoading(false);
    }
  };

  const loadProductFlowchart = async (prodId: string) => {
    setLoading(true);
    setError(null);
    try {
      const numericId = Number(prodId);
      const res: any = await haccpAPI.getFlowchartData(numericId);
      const payload = res?.data || res; // ResponseModel { success, data } or raw

      const serverNodes = payload?.nodes || [];
      const serverEdges = payload?.edges || [];

      // Build hazard and CCP lookups
      console.log('[Flowchart] Total hazards:', hazards.length, hazards);
      console.log('[Flowchart] Total CCPs:', ccps.length, ccps);
      
      // DETAILED CCP INSPECTION
      if (ccps.length > 0) {
        console.log('[Flowchart] ========== INSPECTING CCPs ==========');
        ccps.forEach((c, index) => {
          console.log(`[Flowchart] CCP ${index}:`, {
            id: c.id,
            ccp_number: c.ccp_number,
            ccp_name: (c as any).ccp_name,
            hazard_id: (c as any).hazard_id,
            has_hazard_id: 'hazard_id' in c,
            all_keys: Object.keys(c),
            full_object: c
          });
        });
        console.log('[Flowchart] ======================================');
      }
      
      const hazardsByStepId = new Map<number, StoreHazard[]>();
      hazards.forEach((h) => {
        const stepId = Number((h as any).process_step_id);
        if (!isNaN(stepId)) {
          const arr = hazardsByStepId.get(stepId) || [];
          arr.push(h);
          hazardsByStepId.set(stepId, arr);
        }
      });

      const ccpByHazardId = new Map<number, StoreCCP>();
      ccps.forEach((c) => {
        const hid = Number((c as any).hazard_id);
        console.log(`[Flowchart] Processing CCP ${c.ccp_number}:`, {
          hazard_id_raw: (c as any).hazard_id,
          hazard_id_type: typeof (c as any).hazard_id,
          hazard_id_parsed: hid,
          is_valid: !isNaN(hid)
        });
        
        if (!isNaN(hid)) {
          ccpByHazardId.set(hid, c);
          console.log('[Flowchart] ✓ Mapped CCP', c.ccp_number, 'to hazard', hid);
        } else {
          console.error('[Flowchart] ✗ CCP has no valid hazard_id:', c);
        }
      });
      
      console.log('[Flowchart] hazardsByStepId map:', Array.from(hazardsByStepId.entries()));
      console.log('[Flowchart] ccpByHazardId map:', Array.from(ccpByHazardId.entries()));

      const mappedNodes = serverNodes.map((n: any) => {
        // Map backend types to builder node types
        const typeMap: Record<string, string> = {
          start: 'start',
          end: 'end',
        };
        const mappedType = (typeMap[n.type] || 'custom') as any;

        // Derive process_step_id from id pattern step_{id}
        let processStepId: number | null = null;
        if (typeof n.id === 'string' && n.id.startsWith('step_')) {
          const raw = Number(n.id.replace('step_', ''));
          processStepId = isNaN(raw) ? null : raw;
        }

        // Map hazards attached to this step
        const stepHazards = processStepId ? (hazardsByStepId.get(processStepId) || []) : [];
        const nodeHazards = stepHazards.map((h) => ({
          id: String(h.id),
          type: h.hazard_type as any,
          description: h.description || h.hazard_name || '',
          likelihood: h.likelihood,
          severity: h.severity,
          riskLevel: h.risk_level as any,
          controlMeasures: h.control_measures || '',
          isCCP: !!h.is_ccp,
          risk_strategy: (h as any).risk_strategy,
        }));

        // Map CCP if tied to a hazard at this step
        let ccpData: any = undefined;
        if (stepHazards.length > 0) {
          console.log(`[Flowchart] Node ${n.id} (step ${processStepId}): Found ${stepHazards.length} hazards`, stepHazards.map(h => h.id));
          const matched = stepHazards.find((h) => ccpByHazardId.has(h.id));
          if (matched) {
            const c = ccpByHazardId.get(matched.id)!;
            console.log(`[Flowchart] Node ${n.id}: Found CCP for hazard ${matched.id}:`, c);
            ccpData = {
              number: c.ccp_number,
              criticalLimits: [
                {
                  parameter: c.critical_limit_description || 'Limit',
                  min: c.critical_limit_min ?? undefined,
                  max: c.critical_limit_max ?? undefined,
                  unit: c.critical_limit_unit || '',
                },
              ],
              monitoringFrequency: c.monitoring_frequency || '',
              monitoringMethod: c.monitoring_method || '',
              responsiblePerson: '',
              correctiveActions: c.corrective_actions || '',
              verificationMethod: c.verification_method || '',
            };
            console.log(`[Flowchart] Node ${n.id}: Mapped CCP data:`, ccpData);
          } else {
            console.log(`[Flowchart] Node ${n.id}: No CCP found for any hazard at this step`);
          }
        }

        // Temperature/time/ph mapping from backend flat fields
        const bd = n.data || {};
        const temperature = typeof bd.temperature === 'number' ? { target: bd.temperature, unit: 'C' as const } : undefined;
        const time = typeof bd.time_minutes === 'number' ? { duration: bd.time_minutes, unit: 'minutes' as const } : undefined;
        const ph = typeof bd.ph === 'number' ? { target: bd.ph } : undefined;
        const waterActivity = typeof bd.aw === 'number' ? { target: bd.aw } : undefined;

        return {
          id: String(n.id),
          type: mappedType,
          label: n.label || '',
          position: { x: Number(n.x) || 0, y: Number(n.y) || 0 },
          data: {
            stepNumber: bd.step_number,
            description: bd.description,
            equipment: bd.equipment,
            temperature,
            time,
            ph,
            waterActivity,
            hazards: nodeHazards.length ? nodeHazards : undefined,
            ccp: ccpData,
          },
        } as any;
      });

      const mappedEdges = serverEdges.map((e: any) => ({
        id: String(e.id),
        source: String(e.source),
        target: String(e.target),
        label: e.label,
      }));

      const flowchart: HACCPFlowchart = {
        productId: prodId || '',
        productName: productName,
        title: `${productName} - HACCP Flowchart`,
        description: `Auto-generated from process flows${hazards.length ? ', hazards' : ''}${ccps.length ? ', CCPs' : ''}`,
        version: '1.0',
        nodes: mappedNodes,
        edges: mappedEdges,
        metadata: {
          status: 'draft',
          createdAt: new Date().toISOString(),
          createdBy: currentUser?.username,
        },
      };

      setCurrentFlowchart(flowchart);
      setIsNewFlowchart(false);
      setTemplateDialogOpen(false);
    } catch (err) {
      // Fallback to template selection when no server data
      setIsNewFlowchart(true);
      setTemplateDialogOpen(true);
    } finally {
      setLoading(false);
    }
  };

  const handleTemplateSelection = (template: ProductTemplate) => {
    const newFlowchart: HACCPFlowchart = {
      productId: productId || '',
      productName: productName,
      title: `${productName} - ${template.name}`,
      description: template.description,
      version: '1.0',
      nodes: template.defaultNodes,
      edges: template.defaultEdges,
      metadata: {
        status: 'draft',
        createdAt: new Date().toISOString(),
        createdBy: currentUser?.username,
      },
    };
    
    setCurrentFlowchart(newFlowchart);
    setTemplateDialogOpen(false);
    setIsNewFlowchart(true);
  };

  const handleSaveFlowchart = async (flowchart: HACCPFlowchart) => {
    setLoading(true);
    setError(null);
    
    try {
      if (!productId) {
        throw new Error('Product ID is required to save flowchart');
      }

      const numericProductId = Number(productId);
      
      // Fetch existing process flows once before the loop
      const productData = await haccpAPI.getProduct(numericProductId);
      const existingProcessFlows = productData?.data?.process_flows || [];
      
      // Build a map of existing steps by their stored node ID (from parameters)
      const existingStepsByNodeId = new Map<string, any>();
      const existingStepsByStepNumber = new Map<number, any>();
      
      existingProcessFlows.forEach((pf: any) => {
        try {
          const params = JSON.parse(pf.parameters || '{}');
          if (params.id) {
            existingStepsByNodeId.set(params.id, pf);
          }
        } catch (e) {
          // If parameters can't be parsed, use step_number as fallback
        }
        if (pf.step_number) {
          existingStepsByStepNumber.set(pf.step_number, pf);
        }
      });
      
      // Filter out visual-only nodes and assign step numbers
      const processNodes = flowchart.nodes.filter(
        node => node.type !== 'start' && node.type !== 'end'
      );
      
      // Auto-assign step numbers if not set
      processNodes.forEach((node, index) => {
        if (!node.data?.stepNumber) {
          node.data = { ...node.data, stepNumber: index + 1 };
        }
      });
      
      console.log(`Saving ${processNodes.length} process steps...`);
      
      // Save each process step
      let createdCount = 0;
      let updatedCount = 0;
      
      for (const node of processNodes) {
        const processFlowData: any = {
          step_number: node.data?.stepNumber || 0,
          step_name: node.label || '',
          description: node.data?.description || '',
          equipment: node.data?.equipment || '',
          temperature: node.data?.temperature?.target || null,
          time_minutes: node.data?.time?.duration || null,
          ph: node.data?.ph?.target || null,
          aw: node.data?.waterActivity?.target || null,
          // Store position and node ID for future updates
          parameters: JSON.stringify({
            position: node.position,
            id: node.id,
            type: node.type
          })
        };

        // Check if this node already exists in the database
        const existingStep = existingStepsByNodeId.get(node.id) || 
                            existingStepsByStepNumber.get(processFlowData.step_number);

        try {
          if (existingStep) {
            // Update existing process flow
            await haccpAPI.updateProcessFlow(existingStep.id, processFlowData);
            updatedCount++;
            console.log(`Updated step ${processFlowData.step_number}: ${processFlowData.step_name}`);
          } else {
            // Create new process flow
            await haccpAPI.createProcessFlow(numericProductId, processFlowData);
            createdCount++;
            console.log(`Created step ${processFlowData.step_number}: ${processFlowData.step_name}`);
          }
        } catch (stepError: any) {
          console.error(`Failed to save step ${processFlowData.step_number}:`, stepError);
          throw stepError;
        }
      }
      
      console.log(`Save complete: ${createdCount} created, ${updatedCount} updated`);
      
      // Update local state
      setCurrentFlowchart(flowchart);
      setIsNewFlowchart(false);
      
      // Show success message with details
      setError(null);
      const successMsg = `Flowchart saved successfully! ${createdCount} step(s) created, ${updatedCount} step(s) updated.`;
      setSuccess(successMsg);
      console.log('Flowchart saved successfully:', successMsg);
      
      // Call onSuccess callback to refresh parent component
      if (onSuccess) {
        onSuccess();
      }
      
      // Clear success message after 5 seconds
      setTimeout(() => setSuccess(null), 5000);
      
    } catch (err: any) {
      const errorMessage = err?.response?.data?.detail || err?.message || 'Failed to save flowchart';
      setError(errorMessage);
      console.error('Error saving flowchart:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleClose = () => {
    setCurrentFlowchart(null);
    setTemplateDialogOpen(false);
    setError(null);
    setSuccess(null);
    setIsNewFlowchart(true);
    onClose();
  };

  const handleRestartWithTemplate = () => {
    setCurrentFlowchart(null);
    setTemplateDialogOpen(true);
  };

  return (
    <>
      {/* Main Flowchart Builder Dialog */}
      <Dialog
        open={open && !templateDialogOpen}
        onClose={handleClose}
        maxWidth={false}
        fullScreen
        PaperProps={{
          sx: { bgcolor: 'background.default' }
        }}
      >
        {loading && (
          <Box sx={{ 
            position: 'absolute', 
            top: 0, 
            left: 0, 
            right: 0, 
            bottom: 0, 
            bgcolor: 'rgba(255,255,255,0.8)', 
            display: 'flex', 
            alignItems: 'center', 
            justifyContent: 'center',
            zIndex: 9999 
          }}>
            <CircularProgress />
          </Box>
        )}
        
        {error && (
          <Alert 
            severity="error" 
            onClose={() => setError(null)}
            sx={{ position: 'absolute', top: 16, left: '50%', transform: 'translateX(-50%)', zIndex: 9999 }}
          >
            {error}
          </Alert>
        )}
        
        {success && (
          <Alert 
            severity="success" 
            onClose={() => setSuccess(null)}
            sx={{ position: 'absolute', top: 16, left: '50%', transform: 'translateX(-50%)', zIndex: 9999 }}
          >
            {success}
          </Alert>
        )}
        
        {currentFlowchart && (
          <FlowchartBuilder
            productId={productId}
            productName={productName}
            initialFlowchart={currentFlowchart}
            onSave={handleSaveFlowchart}
            onClose={handleClose}
            readOnly={readOnly}
          />
        )}
        
        {!currentFlowchart && !loading && !templateDialogOpen && (
          <Box sx={{ p: 4, textAlign: 'center' }}>
            <Typography variant="h6" gutterBottom>
              No flowchart loaded
            </Typography>
            <Button 
              variant="contained" 
              onClick={handleRestartWithTemplate}
            >
              Select Template
            </Button>
          </Box>
        )}
      </Dialog>

      {/* Template Selection Dialog */}
      <TemplateSelectionDialog
        open={templateDialogOpen}
        onClose={() => {
          setTemplateDialogOpen(false);
          if (!currentFlowchart) {
            handleClose();
          }
        }}
        onSelectTemplate={handleTemplateSelection}
      />
    </>
  );
};

export default HACCPFlowchartBuilderContainer;
