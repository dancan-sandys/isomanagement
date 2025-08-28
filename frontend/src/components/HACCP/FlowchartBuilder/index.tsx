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
        if (!isNaN(hid)) ccpByHazardId.set(hid, c);
      });

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
        }));

        // Map CCP if tied to a hazard at this step
        let ccpData: any = undefined;
        if (stepHazards.length > 0) {
          const matched = stepHazards.find((h) => ccpByHazardId.has(h.id));
          if (matched) {
            const c = ccpByHazardId.get(matched.id)!;
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
      // TODO: Replace with actual API call
      if (isNewFlowchart) {
        // Create new flowchart
        // const response = await haccpAPI.createFlowchart(flowchart);
        console.log('Creating new flowchart:', flowchart);
      } else {
        // Update existing flowchart
        // const response = await haccpAPI.updateFlowchart(flowchart.id!, flowchart);
        console.log('Updating flowchart:', flowchart);
      }
      
      // Update local state
      setCurrentFlowchart(flowchart);
      setIsNewFlowchart(false);
      
      // Show success message or close dialog
      // For now, just log success
      console.log('Flowchart saved successfully');
      
    } catch (err) {
      setError('Failed to save flowchart');
      console.error('Error saving flowchart:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleClose = () => {
    setCurrentFlowchart(null);
    setTemplateDialogOpen(false);
    setError(null);
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
