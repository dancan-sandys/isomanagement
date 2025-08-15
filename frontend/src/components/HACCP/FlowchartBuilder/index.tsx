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

interface HACCPFlowchartBuilderProps {
  open: boolean;
  onClose: () => void;
  productId?: string;
  productName?: string;
  initialFlowchartId?: string;
  readOnly?: boolean;
}

const HACCPFlowchartBuilderContainer: React.FC<HACCPFlowchartBuilderProps> = ({
  open,
  onClose,
  productId,
  productName = '',
  initialFlowchartId,
  readOnly = false,
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
      if (initialFlowchartId) {
        // Load existing flowchart
        loadFlowchart(initialFlowchartId);
      } else {
        // Show template selection for new flowchart
        setIsNewFlowchart(true);
        setTemplateDialogOpen(true);
      }
    }
  }, [open, initialFlowchartId]);

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
