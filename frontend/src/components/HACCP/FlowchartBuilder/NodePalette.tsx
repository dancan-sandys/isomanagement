import React from 'react';
import {
  Box,
  Typography,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  Paper,
  IconButton,
  Tooltip,
  alpha,
} from '@mui/material';
import {
  ExpandMore,
  PlayArrow,
  Stop,
  Inventory,
  Science,
  Thermostat,
  LocalShipping,
  CheckCircle,
  Build,
  Dining,
  LocalDrink,
  AcUnit,
  FilterAlt,
  Sync,
  QuestionMark,
  Delete,
  Refresh,
  Add,
} from '@mui/icons-material';
import { HACCPNodeType, NodePaletteCategory } from './types';

interface NodePaletteProps {
  onDragStart: (event: React.DragEvent, nodeType: HACCPNodeType, nodeData: any) => void;
}

const NodePalette: React.FC<NodePaletteProps> = ({ onDragStart }) => {
  const nodeCategories: NodePaletteCategory[] = [
    {
      id: 'start_end',
      name: 'Start & End',
      icon: 'PlayArrow',
      nodes: [
        {
          type: HACCPNodeType.START,
          label: 'Start',
          icon: 'PlayArrow',
          description: 'Beginning of the process flow',
          defaultData: {
            description: 'Process start point',
            isRequired: true,
          },
        },
        {
          type: HACCPNodeType.END,
          label: 'End',
          icon: 'Stop',
          description: 'End of the process flow',
          defaultData: {
            description: 'Process end point',
            isRequired: true,
          },
        },
      ],
    },
    {
      id: 'receiving',
      name: 'Receiving & Inspection',
      icon: 'Inventory',
      nodes: [
        {
          type: HACCPNodeType.RAW_MATERIAL_RECEIVING,
          label: 'Raw Material Receiving',
          icon: 'Inventory',
          description: 'Receive raw materials from suppliers',
          defaultData: {
            description: 'Receive and check raw materials',
            temperature: { min: 2, max: 6, unit: 'C' as const },
            hazards: [
              {
                id: 'recv_bio_1',
                type: 'biological' as const,
                description: 'Pathogenic bacteria in raw milk',
                likelihood: 3,
                severity: 4,
                riskLevel: 'high' as const,
                controlMeasures: 'Supplier verification, temperature check',
              },
            ],
          },
        },
        {
          type: HACCPNodeType.INSPECTION,
          label: 'Inspection',
          icon: 'CheckCircle',
          description: 'Visual and quality inspection',
          defaultData: {
            description: 'Inspect for quality and safety',
            hazards: [
              {
                id: 'insp_phy_1',
                type: 'physical' as const,
                description: 'Foreign objects',
                likelihood: 2,
                severity: 3,
                riskLevel: 'medium' as const,
              },
            ],
          },
        },
      ],
    },
    {
      id: 'storage',
      name: 'Storage',
      icon: 'AcUnit',
      nodes: [
        {
          type: HACCPNodeType.COLD_STORAGE,
          label: 'Cold Storage',
          icon: 'AcUnit',
          description: 'Refrigerated storage',
          defaultData: {
            description: 'Store at refrigerated temperature',
            temperature: { min: 2, max: 6, target: 4, unit: 'C' as const },
            hazards: [
              {
                id: 'cold_bio_1',
                type: 'biological' as const,
                description: 'Temperature abuse leading to bacterial growth',
                likelihood: 2,
                severity: 4,
                riskLevel: 'high' as const,
                isCCP: true,
              },
            ],
            ccp: {
              number: 'CCP-1',
              criticalLimits: [
                { parameter: 'Temperature', max: 6, unit: '°C' },
              ],
              monitoringFrequency: 'Continuous',
              monitoringMethod: 'Temperature data logger',
              correctiveActions: 'Adjust cooling system, check product temperature',
              verificationMethod: 'Daily review of temperature records',
            },
          },
        },
        {
          type: HACCPNodeType.DRY_STORAGE,
          label: 'Dry Storage',
          icon: 'Inventory',
          description: 'Ambient temperature storage',
          defaultData: {
            description: 'Store dry ingredients at ambient temperature',
            temperature: { max: 25, unit: 'C' as const },
            hazards: [
              {
                id: 'dry_phy_1',
                type: 'physical' as const,
                description: 'Pest contamination',
                likelihood: 2,
                severity: 3,
                riskLevel: 'medium' as const,
              },
            ],
          },
        },
        {
          type: HACCPNodeType.FREEZER_STORAGE,
          label: 'Freezer Storage',
          icon: 'AcUnit',
          description: 'Frozen storage',
          defaultData: {
            description: 'Store at frozen temperature',
            temperature: { max: -18, unit: 'C' as const },
          },
        },
      ],
    },
    {
      id: 'processing',
      name: 'Processing',
      icon: 'Build',
      nodes: [
        {
          type: HACCPNodeType.PASTEURIZATION,
          label: 'Pasteurization',
          icon: 'Thermostat',
          description: 'Heat treatment to eliminate pathogens',
          defaultData: {
            description: 'HTST pasteurization',
            temperature: { min: 72, target: 72, unit: 'C' as const },
            time: { duration: 15, unit: 'seconds' as const },
            hazards: [
              {
                id: 'past_bio_1',
                type: 'biological' as const,
                description: 'Survival of pathogenic bacteria',
                likelihood: 2,
                severity: 5,
                riskLevel: 'critical' as const,
                isCCP: true,
              },
            ],
            ccp: {
              number: 'CCP-2',
              criticalLimits: [
                { parameter: 'Temperature', min: 72, unit: '°C' },
                { parameter: 'Time', min: 15, unit: 'seconds' },
              ],
              monitoringFrequency: 'Continuous',
              monitoringMethod: 'Temperature recorder and flow rate',
              correctiveActions: 'Reprocess, adjust time/temperature',
              verificationMethod: 'Calibration of instruments, product testing',
            },
          },
        },
        {
          type: HACCPNodeType.COOLING,
          label: 'Cooling',
          icon: 'AcUnit',
          description: 'Cool product after heat treatment',
          defaultData: {
            description: 'Rapid cooling to prevent recontamination',
            temperature: { target: 4, unit: 'C' as const },
            hazards: [
              {
                id: 'cool_bio_1',
                type: 'biological' as const,
                description: 'Slow cooling allowing bacterial growth',
                likelihood: 2,
                severity: 4,
                riskLevel: 'high' as const,
              },
            ],
          },
        },
        {
          type: HACCPNodeType.HOMOGENIZATION,
          label: 'Homogenization',
          icon: 'Sync',
          description: 'Mechanical treatment for uniform consistency',
          defaultData: {
            description: 'Homogenize for uniform fat distribution',
            equipment: 'High-pressure homogenizer',
          },
        },
        {
          type: HACCPNodeType.FERMENTATION,
          label: 'Fermentation',
          icon: 'Science',
          description: 'Controlled fermentation process',
          defaultData: {
            description: 'Lactic acid fermentation',
            temperature: { target: 42, unit: 'C' as const },
            ph: { target: 4.6 },
            time: { duration: 4, unit: 'hours' as const },
          },
        },
        {
          type: HACCPNodeType.SEPARATION,
          label: 'Separation',
          icon: 'FilterAlt',
          description: 'Separate components (cream, skim)',
          defaultData: {
            description: 'Centrifugal separation',
            equipment: 'Cream separator',
          },
        },
        {
          type: HACCPNodeType.STANDARDIZATION,
          label: 'Standardization',
          icon: 'Sync',
          description: 'Adjust fat content',
          defaultData: {
            description: 'Standardize fat content',
          },
        },
        {
          type: HACCPNodeType.MIXING,
          label: 'Mixing',
          icon: 'Sync',
          description: 'Mix ingredients',
          defaultData: {
            description: 'Mix ingredients uniformly',
          },
        },
        {
          type: HACCPNodeType.FILTRATION,
          label: 'Filtration',
          icon: 'FilterAlt',
          description: 'Filter product',
          defaultData: {
            description: 'Remove particles and impurities',
          },
        },
        {
          type: HACCPNodeType.CONCENTRATION,
          label: 'Concentration',
          icon: 'Science',
          description: 'Concentrate product',
          defaultData: {
            description: 'Remove water to concentrate',
          },
        },
      ],
    },
    {
      id: 'packaging',
      name: 'Packaging',
      icon: 'Dining',
      nodes: [
        {
          type: HACCPNodeType.FILLING,
          label: 'Filling',
          icon: 'LocalDrink',
          description: 'Fill product into containers',
          defaultData: {
            description: 'Fill product into packaging',
            hazards: [
              {
                id: 'fill_bio_1',
                type: 'biological' as const,
                description: 'Post-pasteurization contamination',
                likelihood: 2,
                severity: 4,
                riskLevel: 'high' as const,
                isCCP: true,
              },
            ],
          },
        },
        {
          type: HACCPNodeType.SEALING,
          label: 'Sealing',
          icon: 'Build',
          description: 'Seal containers',
          defaultData: {
            description: 'Heat seal containers',
          },
        },
        {
          type: HACCPNodeType.LABELING,
          label: 'Labeling',
          icon: 'Add',
          description: 'Apply labels',
          defaultData: {
            description: 'Apply product labels',
            hazards: [
              {
                id: 'label_allergen_1',
                type: 'allergen' as const,
                description: 'Incorrect allergen labeling',
                likelihood: 1,
                severity: 5,
                riskLevel: 'critical' as const,
              },
            ],
          },
        },
        {
          type: HACCPNodeType.CODING,
          label: 'Coding',
          icon: 'Add',
          description: 'Apply date/lot codes',
          defaultData: {
            description: 'Apply date and lot codes',
          },
        },
        {
          type: HACCPNodeType.FINAL_PACKAGING,
          label: 'Final Packaging',
          icon: 'Dining',
          description: 'Secondary packaging',
          defaultData: {
            description: 'Pack into shipping containers',
          },
        },
      ],
    },
    {
      id: 'quality',
      name: 'Quality Control',
      icon: 'CheckCircle',
      nodes: [
        {
          type: HACCPNodeType.QUALITY_CHECK,
          label: 'Quality Check',
          icon: 'CheckCircle',
          description: 'Quality control check',
          defaultData: {
            description: 'Visual and sensory quality check',
          },
        },
        {
          type: HACCPNodeType.TESTING,
          label: 'Testing',
          icon: 'Science',
          description: 'Laboratory testing',
          defaultData: {
            description: 'Microbiological and chemical testing',
          },
        },
      ],
    },
    {
      id: 'final',
      name: 'Final Steps',
      icon: 'LocalShipping',
      nodes: [
        {
          type: HACCPNodeType.SHIPPING,
          label: 'Shipping',
          icon: 'LocalShipping',
          description: 'Ship to customers',
          defaultData: {
            description: 'Ship finished product',
            temperature: { max: 6, unit: 'C' as const },
          },
        },
      ],
    },
    {
      id: 'other',
      name: 'Other',
      icon: 'QuestionMark',
      nodes: [
        {
          type: HACCPNodeType.DECISION,
          label: 'Decision Point',
          icon: 'QuestionMark',
          description: 'Decision or branch point',
          defaultData: {
            description: 'Decision point in process',
          },
        },
        {
          type: HACCPNodeType.REWORK,
          label: 'Rework',
          icon: 'Refresh',
          description: 'Rework process',
          defaultData: {
            description: 'Rework non-conforming product',
          },
        },
        {
          type: HACCPNodeType.WASTE,
          label: 'Waste',
          icon: 'Delete',
          description: 'Waste disposal',
          defaultData: {
            description: 'Dispose of waste product',
          },
        },
        {
          type: HACCPNodeType.CUSTOM,
          label: 'Custom Process',
          icon: 'Add',
          description: 'Custom process step',
          defaultData: {
            description: 'Custom process step',
          },
        },
      ],
    },
  ];

  const getIcon = (iconName: string) => {
    const icons: Record<string, React.ReactElement> = {
      PlayArrow: <PlayArrow />,
      Stop: <Stop />,
      Inventory: <Inventory />,
      CheckCircle: <CheckCircle />,
      AcUnit: <AcUnit />,
      Build: <Build />,
      Thermostat: <Thermostat />,
      Science: <Science />,
      FilterAlt: <FilterAlt />,
      Sync: <Sync />,
      LocalDrink: <LocalDrink />,
      Add: <Add />,
      Dining: <Dining />,
      LocalShipping: <LocalShipping />,
      QuestionMark: <QuestionMark />,
      Refresh: <Refresh />,
      Delete: <Delete />,
    };
    return icons[iconName] || <Add />;
  };

  const handleDragStart = (event: React.DragEvent, nodeType: HACCPNodeType, defaultData: any) => {
    onDragStart(event, nodeType, defaultData);
  };

  return (
    <Box sx={{ width: 300, height: '100%', overflow: 'auto', bgcolor: 'background.paper', borderRight: 1, borderColor: 'divider' }}>
      <Typography variant="h6" sx={{ p: 2, fontWeight: 'bold', borderBottom: 1, borderColor: 'divider' }}>
        Process Nodes
      </Typography>
      
      {nodeCategories.map((category) => (
        <Accordion key={category.id} defaultExpanded>
          <AccordionSummary
            expandIcon={<ExpandMore />}
            sx={{ minHeight: 48, '&.Mui-expanded': { minHeight: 48 } }}
          >
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
              {getIcon(category.icon)}
              <Typography variant="subtitle2" fontWeight="medium">
                {category.name}
              </Typography>
            </Box>
          </AccordionSummary>
          <AccordionDetails sx={{ pt: 0 }}>
            <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1 }}>
              {category.nodes.map((node) => (
                <Paper
                  key={node.type}
                  draggable
                  onDragStart={(e) => handleDragStart(e, node.type, node.defaultData)}
                  sx={{
                    p: 1.5,
                    cursor: 'grab',
                    border: 1,
                    borderColor: 'divider',
                    borderRadius: 1,
                    transition: 'all 0.2s',
                    '&:hover': {
                      borderColor: 'primary.main',
                      bgcolor: alpha('#1976d2', 0.04),
                      transform: 'translateY(-1px)',
                      boxShadow: 2,
                    },
                    '&:active': {
                      cursor: 'grabbing',
                      transform: 'scale(0.98)',
                    },
                  }}
                >
                  <Tooltip title={node.description} placement="right">
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                      {getIcon(node.icon)}
                      <Typography variant="body2" fontWeight="medium" noWrap>
                        {node.label}
                      </Typography>
                    </Box>
                  </Tooltip>
                </Paper>
              ))}
            </Box>
          </AccordionDetails>
        </Accordion>
      ))}
    </Box>
  );
};

export default NodePalette;
