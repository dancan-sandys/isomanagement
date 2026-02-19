import React, { useState, useCallback, useRef, useEffect } from 'react';
import {
  Box,
  AppBar,
  Toolbar,
  Typography,
  Button,
  IconButton,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  Snackbar,
  Alert,
  Chip,
  Tooltip,
  Divider,
} from '@mui/material';
import {
  Save,
  Download,
  ZoomIn,
  ZoomOut,
  FitScreen,
  Delete,
  Close,
} from '@mui/icons-material';
import ReactFlow, {
  addEdge,
  Background,
  Controls,
  MiniMap,
  useNodesState,
  useEdgesState,
  ReactFlowProvider,
  useReactFlow,
  Panel,
  BackgroundVariant,
} from 'reactflow';
import type { Node, Edge, Connection } from 'reactflow';
import 'reactflow/dist/style.css';

import NodePalette from './NodePalette';
import HACCPNode from './HACCPNode';
import NodeEditDialog from './NodeEditDialog';
import { HACCPNodeType, HACCPProcessStep, HACCPFlowConnection, HACCPFlowchart, HACCPNodeData } from './types';

// React Flow node data shape used in the canvas
type ReactFlowHACCPNodeData = HACCPNodeData & {
  label: string;
  nodeType: HACCPNodeType;
  onEdit?: (nodeId: string) => void;
  onDelete?: (nodeId: string) => void;
};

interface FlowchartBuilderProps {
  productId?: string;
  productName?: string;
  initialFlowchart?: HACCPFlowchart;
  onSave?: (flowchart: HACCPFlowchart) => void;
  onClose?: () => void;
  readOnly?: boolean;
}

const nodeTypes = {
  haccpNode: HACCPNode,
};

let nodeId = 1;
const getId = () => `node_${nodeId++}`;

const FlowchartBuilderContent: React.FC<FlowchartBuilderProps> = ({
  productId = '',
  productName = '',
  initialFlowchart,
  onSave,
  onClose,
  readOnly = false,
}) => {
  const reactFlowWrapper = useRef<HTMLDivElement>(null);
  const { project, fitView, zoomIn, zoomOut } = useReactFlow();
  
  const [nodes, setNodes, onNodesChange] = useNodesState<ReactFlowHACCPNodeData>([]);
  const [edges, setEdges, onEdgesChange] = useEdgesState<Edge>([]);
  const [reactFlowInstance, setReactFlowInstance] = useState<any>(null);
  
  // UI State
  const [selectedNodeId, setSelectedNodeId] = useState<string | null>(null);
  const [editDialogOpen, setEditDialogOpen] = useState(false);
  const [saveDialogOpen, setSaveDialogOpen] = useState(false);
  const [snackbar, setSnackbar] = useState({ open: false, message: '', severity: 'info' as 'success' | 'error' | 'info' | 'warning' });
  
  // Flowchart metadata
  const [flowchartTitle, setFlowchartTitle] = useState('');
  const [flowchartDescription, setFlowchartDescription] = useState('');
  const [flowchartVersion, setFlowchartVersion] = useState('1.0');

  // Define callbacks before effects that depend on them
  const handleNodeEdit = useCallback((nodeId: string) => {
    setSelectedNodeId(nodeId);
    setEditDialogOpen(true);
  }, []);

  const handleNodeDelete = useCallback((nodeId: string) => {
    if (readOnly) return;
    setNodes((nds) => nds.filter((node) => node.id !== nodeId));
    setEdges((eds) => eds.filter((edge) => edge.source !== nodeId && edge.target !== nodeId));
    setSnackbar({ open: true, message: 'Node deleted successfully', severity: 'info' });
  }, [setNodes, setEdges, readOnly]);

  // Load initial flowchart
  useEffect(() => {
    if (initialFlowchart) {
      setFlowchartTitle(initialFlowchart.title);
      setFlowchartDescription(initialFlowchart.description || '');
      setFlowchartVersion(initialFlowchart.version);
      
      // Convert HACCPProcessStep to ReactFlow Node
      const flowNodes = initialFlowchart.nodes.map((step) => ({
        id: step.id,
        type: 'haccpNode',
        position: step.position,
        data: {
          ...step.data,
          label: step.label,
          nodeType: step.type,
          onEdit: handleNodeEdit,
          onDelete: handleNodeDelete,
        },
      }));
      
      // Convert HACCPFlowConnection to ReactFlow Edge
      const flowEdges = initialFlowchart.edges.map((conn): Edge => ({
        id: conn.id,
        source: conn.source,
        target: conn.target,
        label: conn.label,
        type: 'smoothstep',
        animated: true,
      }));
      
      setNodes(flowNodes);
      setEdges(flowEdges);
      
      // Set higher nodeId to avoid conflicts
      const maxId = Math.max(...flowNodes.map(n => parseInt(n.id.replace('node_', '')) || 0));
      nodeId = maxId + 1;
    }
  }, [initialFlowchart, setNodes, setEdges, handleNodeEdit, handleNodeDelete]);

  const onConnect = useCallback(
    (params: Connection) => {
      if (readOnly) return;
      setEdges((eds) => addEdge({ ...params, type: 'smoothstep', animated: true }, eds));
    },
    [setEdges, readOnly]
  );

  const onDragOver = useCallback((event: React.DragEvent) => {
    event.preventDefault();
    event.dataTransfer.dropEffect = 'move';
  }, []);

  const onDrop = useCallback(
    (event: React.DragEvent) => {
      if (readOnly) return;
      
      event.preventDefault();

      const reactFlowBounds = reactFlowWrapper.current!.getBoundingClientRect();
      const type = event.dataTransfer.getData('application/reactflow-type') as HACCPNodeType;
      const nodeData = JSON.parse(event.dataTransfer.getData('application/reactflow-data'));

      if (typeof type === 'undefined' || !type) {
        return;
      }

      const position = project({
        x: event.clientX - reactFlowBounds.left,
        y: event.clientY - reactFlowBounds.top,
      });

      const newNode = {
        id: getId(),
        type: 'haccpNode',
        position,
        data: {
          ...nodeData,
          label: type.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase()),
          nodeType: type,
          onEdit: handleNodeEdit,
          onDelete: handleNodeDelete,
        },
      };

      setNodes((nds) => [...nds, newNode]);
    },
    [project, setNodes, readOnly, handleNodeEdit, handleNodeDelete]
  );

  const onDragStart = useCallback((event: React.DragEvent, nodeType: HACCPNodeType, nodeData: any) => {
    event.dataTransfer.setData('application/reactflow-type', nodeType);
    event.dataTransfer.setData('application/reactflow-data', JSON.stringify(nodeData));
    event.dataTransfer.effectAllowed = 'move';
  }, []);

  // Duplicate declarations removed; defined earlier

  const handleNodeUpdate = useCallback((nodeId: string, updatedData: Partial<HACCPNodeData>) => {
    setNodes((nds) =>
      nds.map((node) => {
        if (node.id === nodeId) {
          return {
            ...node,
            data: { ...node.data, ...updatedData },
          };
        }
        return node;
      })
    );
    setEditDialogOpen(false);
    showSnackbar('Node updated successfully', 'success');
  }, [setNodes]);

  const showSnackbar = (message: string, severity: 'success' | 'error' | 'info' | 'warning') => {
    setSnackbar({ open: true, message, severity });
  };

  const handleSave = () => {
    if (!flowchartTitle.trim()) {
      showSnackbar('Please enter a flowchart title', 'error');
      return;
    }

    // ISO/Codex validation: CCPs must have critical limits, monitoring, corrective actions, verification
    const validationErrors: string[] = [];
    nodes.forEach((node) => {
      const data = node.data as any;
      const hasCcp = !!(data?.ccp?.number) || (data?.hazards || []).some((h: any) => h.isCCP);
      if (hasCcp) {
        const limits = data?.ccp?.criticalLimits || [];
        if (!limits.length) validationErrors.push(`${node.data.label}: CCP must define at least one critical limit`);
        if (!data?.ccp?.monitoringFrequency) validationErrors.push(`${node.data.label}: CCP requires monitoring frequency`);
        if (!data?.ccp?.monitoringMethod) validationErrors.push(`${node.data.label}: CCP requires monitoring method`);
        if (!data?.ccp?.correctiveActions) validationErrors.push(`${node.data.label}: CCP requires corrective actions`);
        if (!data?.ccp?.verificationMethod) validationErrors.push(`${node.data.label}: CCP requires verification method`);
      }
    });
    if (validationErrors.length) {
      showSnackbar(`Fix ${validationErrors.length} validation issue(s) before saving`, 'error');
      console.error('HACCP Flowchart validation errors:', validationErrors);
      return;
    }

    // Convert ReactFlow nodes back to HACCPProcessStep
    const haccpNodes: HACCPProcessStep[] = nodes.map((node) => {
      const { onEdit, onDelete, label, nodeType, ...dataWithoutUi } = node.data;
      return {
        id: node.id,
        type: nodeType,
        label,
        position: node.position,
        data: dataWithoutUi,
      };
    });

    // Convert ReactFlow edges back to HACCPFlowConnection
    const haccpEdges: HACCPFlowConnection[] = edges.map((edge) => ({
      id: edge.id,
      source: edge.source,
      target: edge.target,
      label: typeof edge.label === 'string' ? edge.label : undefined,
    }));

    const flowchart: HACCPFlowchart = {
      id: initialFlowchart?.id,
      productId,
      productName,
      title: flowchartTitle,
      description: flowchartDescription,
      version: flowchartVersion,
      nodes: haccpNodes,
      edges: haccpEdges,
      metadata: {
        ...initialFlowchart?.metadata,
        status: 'draft',
        updatedAt: new Date().toISOString(),
      },
    };

    if (onSave) {
      onSave(flowchart);
    }
    setSaveDialogOpen(false);
    showSnackbar('Flowchart saved successfully', 'success');
  };

  const exportFlowchart = () => {
    if (reactFlowInstance) {
      const flow = reactFlowInstance.toObject();
      const dataStr = JSON.stringify(flow, null, 2);
      const dataUri = 'data:application/json;charset=utf-8,'+ encodeURIComponent(dataStr);
      
      const exportFileDefaultName = `haccp_flowchart_${productName.replace(/\s+/g, '_')}.json`;
      
      const linkElement = document.createElement('a');
      linkElement.setAttribute('href', dataUri);
      linkElement.setAttribute('download', exportFileDefaultName);
      linkElement.click();
    }
  };

  const clearFlowchart = () => {
    if (readOnly) return;
    setNodes([]);
    setEdges([]);
    showSnackbar('Flowchart cleared', 'info');
  };

  const selectedNode = selectedNodeId ? nodes.find(n => n.id === selectedNodeId) : null;

  return (
    <Box sx={{ height: '100vh', width: '100%', display: 'flex', flexDirection: 'column' }}>
      {/* Top Toolbar */}
      <AppBar position="static" color="default" elevation={1}>
        <Toolbar variant="dense" sx={{ gap: 1 }}>
          <Typography variant="h6" sx={{ flexGrow: 1 }}>
            HACCP Flowchart Builder
            {productName && ` - ${productName}`}
          </Typography>
          
          {!readOnly && (
            <>
              <Button
                startIcon={<Save />}
                variant="contained"
                size="small"
                onClick={() => setSaveDialogOpen(true)}
                disabled={nodes.length === 0}
              >
                Save
              </Button>
              <Button
                startIcon={<Download />}
                size="small"
                onClick={exportFlowchart}
                disabled={nodes.length === 0}
              >
                Export
              </Button>
              <Divider orientation="vertical" flexItem sx={{ mx: 1 }} />
              <Tooltip title="Clear All">
                <IconButton size="small" onClick={clearFlowchart}>
                  <Delete />
                </IconButton>
              </Tooltip>
            </>
          )}
          
          <Tooltip title="Zoom In">
            <IconButton size="small" onClick={() => zoomIn()}>
              <ZoomIn />
            </IconButton>
          </Tooltip>
          <Tooltip title="Zoom Out">
            <IconButton size="small" onClick={() => zoomOut()}>
              <ZoomOut />
            </IconButton>
          </Tooltip>
          <Tooltip title="Fit View">
            <IconButton size="small" onClick={() => fitView()}>
              <FitScreen />
            </IconButton>
          </Tooltip>
          
          {onClose && (
            <IconButton size="small" onClick={onClose}>
              <Close />
            </IconButton>
          )}
        </Toolbar>
      </AppBar>

      {/* Main Content */}
      <Box sx={{ flex: 1, display: 'flex' }}>
        {/* Node Palette */}
        {!readOnly && <NodePalette onDragStart={onDragStart} />}
        
        {/* Flowchart Canvas */}
        <Box sx={{ flex: 1, position: 'relative' }} ref={reactFlowWrapper}>
          <ReactFlow
            nodes={nodes}
            edges={edges}
            onNodesChange={onNodesChange}
            onEdgesChange={onEdgesChange}
            onConnect={onConnect}
            onInit={setReactFlowInstance}
            onDrop={onDrop}
            onDragOver={onDragOver}
            nodeTypes={nodeTypes}
            fitView
            snapToGrid
            snapGrid={[20, 20]}
            defaultEdgeOptions={{
              type: 'smoothstep',
              animated: true,
            }}
          >
            <Controls />
            <MiniMap />
            <Background variant={BackgroundVariant.Dots} gap={20} size={1} />
            
            {/* Stats Panel */}
            <Panel position="top-left">
              <Box sx={{ bgcolor: 'background.paper', p: 1, borderRadius: 1, border: 1, borderColor: 'divider' }}>
                <Typography variant="caption" display="block">
                  Nodes: {nodes.length}
                </Typography>
                <Typography variant="caption" display="block">
                  Connections: {edges.length}
                </Typography>
                <Typography variant="caption" display="block">
                  CCPs: {nodes.filter(n => n.data.ccp?.number).length}
                </Typography>
              </Box>
            </Panel>

            {/* Legend Panel */}
            <Panel position="bottom-left">
              <Box sx={{ bgcolor: 'background.paper', p: 1, borderRadius: 1, border: 1, borderColor: 'divider' }}>
                <Typography variant="caption" fontWeight="bold" display="block" mb={0.5}>
                  Risk Levels
                </Typography>
                <Box sx={{ display: 'flex', gap: 0.5, flexWrap: 'wrap' }}>
                  <Chip size="small" label="Critical" color="error" variant="filled" sx={{ fontSize: '0.6rem', height: 16 }} />
                  <Chip size="small" label="High" color="warning" variant="filled" sx={{ fontSize: '0.6rem', height: 16 }} />
                  <Chip size="small" label="Medium" color="info" variant="outlined" sx={{ fontSize: '0.6rem', height: 16 }} />
                </Box>
              </Box>
            </Panel>
          </ReactFlow>
        </Box>
      </Box>

      {/* Node Edit Dialog */}
      {selectedNode && (
        <NodeEditDialog
          open={editDialogOpen}
          node={selectedNode}
          onClose={() => setEditDialogOpen(false)}
          onSave={handleNodeUpdate}
          readOnly={readOnly}
        />
      )}

      {/* Save Dialog */}
      <Dialog open={saveDialogOpen} onClose={() => setSaveDialogOpen(false)} maxWidth="sm" fullWidth>
        <DialogTitle>Save HACCP Flowchart</DialogTitle>
        <DialogContent>
          <TextField
            fullWidth
            label="Title"
            value={flowchartTitle}
            onChange={(e) => setFlowchartTitle(e.target.value)}
            margin="normal"
            required
          />
          <TextField
            fullWidth
            label="Description"
            value={flowchartDescription}
            onChange={(e) => setFlowchartDescription(e.target.value)}
            margin="normal"
            multiline
            rows={3}
          />
          <TextField
            fullWidth
            label="Version"
            value={flowchartVersion}
            onChange={(e) => setFlowchartVersion(e.target.value)}
            margin="normal"
            required
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setSaveDialogOpen(false)}>Cancel</Button>
          <Button onClick={handleSave} variant="contained">Save</Button>
        </DialogActions>
      </Dialog>

      {/* Snackbar */}
      <Snackbar
        open={snackbar.open}
        autoHideDuration={4000}
        onClose={() => setSnackbar({ ...snackbar, open: false })}
      >
        <Alert severity={snackbar.severity} onClose={() => setSnackbar({ ...snackbar, open: false })}>
          {snackbar.message}
        </Alert>
      </Snackbar>
    </Box>
  );
};

const FlowchartBuilder: React.FC<FlowchartBuilderProps> = (props) => {
  return (
    <ReactFlowProvider>
      <FlowchartBuilderContent {...props} />
    </ReactFlowProvider>
  );
};

export default FlowchartBuilder;
