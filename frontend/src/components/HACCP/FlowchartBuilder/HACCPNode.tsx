import React, { memo, useState } from 'react';
import { Handle, Position, NodeProps } from 'reactflow';
import {
  Box,
  Typography,
  Paper,
  Chip,
  IconButton,
  Tooltip,
  Menu,
  MenuItem,
  alpha,
} from '@mui/material';
import {
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
  MoreVert,
  Edit,
  Warning,
  Security,
} from '@mui/icons-material';
import { HACCPNodeType, HACCPNodeData } from './types';

interface HACCPNodeProps extends NodeProps {
  data: HACCPNodeData & {
    label: string;
    nodeType: HACCPNodeType;
    onEdit?: (nodeId: string) => void;
    onDelete?: (nodeId: string) => void;
  };
}

const HACCPNode: React.FC<HACCPNodeProps> = memo(({ id, data, selected }) => {
  const [menuAnchor, setMenuAnchor] = useState<null | HTMLElement>(null);

  const getNodeIcon = (nodeType: HACCPNodeType) => {
    const iconMap: Record<HACCPNodeType, React.ReactElement> = {
      [HACCPNodeType.START]: <PlayArrow sx={{ color: 'success.main' }} />,
      [HACCPNodeType.END]: <Stop sx={{ color: 'error.main' }} />,
      [HACCPNodeType.RAW_MATERIAL_RECEIVING]: <Inventory sx={{ color: 'primary.main' }} />,
      [HACCPNodeType.INSPECTION]: <CheckCircle sx={{ color: 'info.main' }} />,
      [HACCPNodeType.COLD_STORAGE]: <AcUnit sx={{ color: 'info.main' }} />,
      [HACCPNodeType.DRY_STORAGE]: <Inventory sx={{ color: 'warning.main' }} />,
      [HACCPNodeType.FREEZER_STORAGE]: <AcUnit sx={{ color: 'primary.main' }} />,
      [HACCPNodeType.PASTEURIZATION]: <Thermostat sx={{ color: 'error.main' }} />,
      [HACCPNodeType.FERMENTATION]: <Science sx={{ color: 'secondary.main' }} />,
      [HACCPNodeType.HOMOGENIZATION]: <Sync sx={{ color: 'primary.main' }} />,
      [HACCPNodeType.SEPARATION]: <FilterAlt sx={{ color: 'info.main' }} />,
      [HACCPNodeType.STANDARDIZATION]: <Sync sx={{ color: 'warning.main' }} />,
      [HACCPNodeType.COOLING]: <AcUnit sx={{ color: 'info.main' }} />,
      [HACCPNodeType.HEATING]: <Thermostat sx={{ color: 'error.main' }} />,
      [HACCPNodeType.MIXING]: <Sync sx={{ color: 'primary.main' }} />,
      [HACCPNodeType.FILTRATION]: <FilterAlt sx={{ color: 'info.main' }} />,
      [HACCPNodeType.CONCENTRATION]: <Science sx={{ color: 'secondary.main' }} />,
      [HACCPNodeType.FILLING]: <LocalDrink sx={{ color: 'primary.main' }} />,
      [HACCPNodeType.SEALING]: <Build sx={{ color: 'warning.main' }} />,
      [HACCPNodeType.LABELING]: <Add sx={{ color: 'info.main' }} />,
      [HACCPNodeType.CODING]: <Add sx={{ color: 'secondary.main' }} />,
      [HACCPNodeType.FINAL_PACKAGING]: <Dining sx={{ color: 'primary.main' }} />,
      [HACCPNodeType.SHIPPING]: <LocalShipping sx={{ color: 'success.main' }} />,
      [HACCPNodeType.QUALITY_CHECK]: <CheckCircle sx={{ color: 'success.main' }} />,
      [HACCPNodeType.TESTING]: <Science sx={{ color: 'info.main' }} />,
      [HACCPNodeType.DECISION]: <QuestionMark sx={{ color: 'warning.main' }} />,
      [HACCPNodeType.REWORK]: <Refresh sx={{ color: 'warning.main' }} />,
      [HACCPNodeType.WASTE]: <Delete sx={{ color: 'error.main' }} />,
      [HACCPNodeType.CUSTOM]: <Add sx={{ color: 'grey.600' }} />,
    };
    return iconMap[nodeType] || <Add />;
  };

  const getNodeColor = (nodeType: HACCPNodeType) => {
    if (nodeType === HACCPNodeType.START) return 'success.main';
    if (nodeType === HACCPNodeType.END) return 'error.main';
    if (data.ccp?.number) return 'error.main'; // CCP nodes are critical
    if (data.hazards?.some(h => h.riskLevel === 'critical' || h.riskLevel === 'high')) return 'warning.main';
    return 'primary.main';
  };

  const getBorderColor = (nodeType: HACCPNodeType) => {
    if (data.ccp?.number) return 'error.main';
    if (data.hazards?.some(h => h.riskLevel === 'critical')) return 'error.main';
    if (data.hazards?.some(h => h.riskLevel === 'high')) return 'warning.main';
    return 'primary.main';
  };

  const getRiskChips = () => {
    if (!data.hazards?.length) return null;
    
    const criticalHazards = data.hazards.filter(h => h.riskLevel === 'critical').length;
    const highHazards = data.hazards.filter(h => h.riskLevel === 'high').length;
    const mediumHazards = data.hazards.filter(h => h.riskLevel === 'medium').length;
    
    return (
      <Box sx={{ display: 'flex', gap: 0.5, flexWrap: 'wrap', mt: 0.5 }}>
        {criticalHazards > 0 && (
          <Chip
            size="small"
            label={`${criticalHazards} Critical`}
            color="error"
            variant="filled"
            sx={{ fontSize: '0.65rem', height: 16 }}
          />
        )}
        {highHazards > 0 && (
          <Chip
            size="small"
            label={`${highHazards} High`}
            color="warning"
            variant="filled"
            sx={{ fontSize: '0.65rem', height: 16 }}
          />
        )}
        {mediumHazards > 0 && (
          <Chip
            size="small"
            label={`${mediumHazards} Medium`}
            color="info"
            variant="outlined"
            sx={{ fontSize: '0.65rem', height: 16 }}
          />
        )}
      </Box>
    );
  };

  const getParameterInfo = () => {
    const params = [];
    if (data.temperature) {
      const temp = data.temperature;
      const tempText = temp.target ? `${temp.target}°${temp.unit}` : 
                     temp.min && temp.max ? `${temp.min}-${temp.max}°${temp.unit}` :
                     temp.max ? `≤${temp.max}°${temp.unit}` : '';
      if (tempText) params.push(`T: ${tempText}`);
    }
    if (data.time?.duration) {
      params.push(`t: ${data.time.duration}${data.time.unit.charAt(0)}`);
    }
    if (data.ph?.target) {
      params.push(`pH: ${data.ph.target}`);
    }
    return params.length > 0 ? params.join(', ') : null;
  };

  const handleMenuClick = (event: React.MouseEvent<HTMLElement>) => {
    event.stopPropagation();
    setMenuAnchor(event.currentTarget);
  };

  const handleMenuClose = () => {
    setMenuAnchor(null);
  };

  const handleEdit = () => {
    handleMenuClose();
    if (data.onEdit) {
      data.onEdit(id);
    }
  };

  const handleDelete = () => {
    handleMenuClose();
    if (data.onDelete) {
      data.onDelete(id);
    }
  };

  const isStartOrEnd = data.nodeType === HACCPNodeType.START || data.nodeType === HACCPNodeType.END;
  const isDecision = data.nodeType === HACCPNodeType.DECISION;

  return (
    <>
      {/* Input handles */}
      {data.nodeType !== HACCPNodeType.START && (
        <Handle
          type="target"
          position={Position.Top}
          style={{
            background: getBorderColor(data.nodeType),
            border: '2px solid white',
            width: 10,
            height: 10,
          }}
        />
      )}

      <Paper
        elevation={selected ? 8 : 2}
        sx={{
          minWidth: 180,
          maxWidth: 250,
          border: 2,
          borderColor: selected ? 'primary.main' : getBorderColor(data.nodeType),
          borderRadius: isDecision ? '50%' : isStartOrEnd ? '20px' : '8px',
          backgroundColor: 'background.paper',
          position: 'relative',
          transition: 'all 0.2s',
          '&:hover': {
            boxShadow: 4,
            transform: 'scale(1.02)',
          },
        }}
      >
        {/* CCP Badge */}
        {data.ccp?.number && (
          <Box
            sx={{
              position: 'absolute',
              top: -8,
              left: -8,
              bgcolor: 'error.main',
              color: 'white',
              borderRadius: '50%',
              width: 24,
              height: 24,
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              fontSize: '0.75rem',
              fontWeight: 'bold',
              zIndex: 10,
            }}
          >
            {data.ccp.number.replace('CCP-', '')}
          </Box>
        )}

        {/* Menu Button */}
        <IconButton
          size="small"
          sx={{
            position: 'absolute',
            top: 4,
            right: 4,
            width: 20,
            height: 20,
            opacity: 0.7,
            '&:hover': { opacity: 1 },
          }}
          onClick={handleMenuClick}
        >
          <MoreVert sx={{ fontSize: 16 }} />
        </IconButton>

        <Box sx={{ p: 1.5, pt: 2 }}>
          {/* Node Header */}
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
            {getNodeIcon(data.nodeType)}
            <Typography
              variant="body2"
              fontWeight="bold"
              sx={{
                flex: 1,
                fontSize: '0.8rem',
                lineHeight: 1.2,
                wordBreak: 'break-word',
              }}
            >
              {data.label}
            </Typography>
          </Box>

          {/* Step Number */}
          {data.stepNumber && (
            <Typography variant="caption" color="text.secondary" sx={{ display: 'block', mb: 0.5 }}>
              Step {data.stepNumber}
            </Typography>
          )}

          {/* Description */}
          {data.description && (
            <Typography
              variant="caption"
              color="text.secondary"
              sx={{
                display: 'block',
                mb: 0.5,
                fontSize: '0.7rem',
                lineHeight: 1.1,
                overflow: 'hidden',
                textOverflow: 'ellipsis',
                display: '-webkit-box',
                WebkitLineClamp: 2,
                WebkitBoxOrient: 'vertical',
              }}
            >
              {data.description}
            </Typography>
          )}

          {/* Process Parameters */}
          {getParameterInfo() && (
            <Typography
              variant="caption"
              sx={{
                display: 'block',
                mb: 0.5,
                fontSize: '0.65rem',
                color: 'primary.main',
                fontWeight: 'medium',
              }}
            >
              {getParameterInfo()}
            </Typography>
          )}

          {/* Risk Chips */}
          {getRiskChips()}

          {/* Equipment */}
          {data.equipment && (
            <Typography
              variant="caption"
              color="text.secondary"
              sx={{
                display: 'block',
                mt: 0.5,
                fontSize: '0.65rem',
                fontStyle: 'italic',
              }}
            >
              {data.equipment}
            </Typography>
          )}
        </Box>
      </Paper>

      {/* Output handles */}
      {data.nodeType !== HACCPNodeType.END && (
        <>
          <Handle
            type="source"
            position={Position.Bottom}
            style={{
              background: getBorderColor(data.nodeType),
              border: '2px solid white',
              width: 10,
              height: 10,
            }}
          />
          {/* Decision nodes can have multiple outputs */}
          {isDecision && (
            <>
              <Handle
                type="source"
                position={Position.Right}
                id="yes"
                style={{
                  background: 'green',
                  border: '2px solid white',
                  width: 10,
                  height: 10,
                  top: '70%',
                }}
              />
              <Handle
                type="source"
                position={Position.Left}
                id="no"
                style={{
                  background: 'red',
                  border: '2px solid white',
                  width: 10,
                  height: 10,
                  top: '70%',
                }}
              />
            </>
          )}
        </>
      )}

      {/* Context Menu */}
      <Menu
        anchorEl={menuAnchor}
        open={Boolean(menuAnchor)}
        onClose={handleMenuClose}
        PaperProps={{
          sx: { minWidth: 150 },
        }}
      >
        <MenuItem onClick={handleEdit}>
          <Edit sx={{ mr: 1, fontSize: 16 }} />
          Edit Node
        </MenuItem>
        <MenuItem onClick={handleDelete} sx={{ color: 'error.main' }}>
          <Delete sx={{ mr: 1, fontSize: 16 }} />
          Delete Node
        </MenuItem>
      </Menu>
    </>
  );
});

HACCPNode.displayName = 'HACCPNode';

export default HACCPNode;
