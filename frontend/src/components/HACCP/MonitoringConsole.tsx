import React, { useState } from 'react';
import {
  Box,
  Card,
  CardContent,
  CardHeader,
  Typography,
  Button,
  Chip,
  Alert,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
} from '@mui/material';
import {
  Science,
  Warning,
  CheckCircle,
  Error,
  Timer,
} from '@mui/icons-material';

const MonitoringConsole: React.FC = () => {
  const [tasks] = useState([
    {
      id: '1',
      ccpName: 'Temperature Control',
      ccpNumber: 1,
      productName: 'Chicken Breast',
      status: 'due',
      priority: 'high',
      dueTime: '2024-01-15 14:30',
    },
    {
      id: '2',
      ccpName: 'pH Control',
      ccpNumber: 2,
      productName: 'Pickled Vegetables',
      status: 'overdue',
      priority: 'critical',
      dueTime: '2024-01-15 13:00',
    },
  ]);

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'due':
        return <Timer color="info" />;
      case 'overdue':
        return <Warning color="warning" />;
      case 'completed':
        return <CheckCircle color="success" />;
      default:
        return <Timer />;
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'due':
        return 'info';
      case 'overdue':
        return 'warning';
      case 'completed':
        return 'success';
      default:
        return 'default';
    }
  };

  return (
    <Box sx={{ p: 3 }}>
      <Card>
        <CardHeader
          title="Monitoring Console"
          subheader={`${tasks.length} tasks due`}
        />
        <CardContent>
          {tasks.length === 0 ? (
            <Alert severity="success">
              No monitoring tasks due at this time.
            </Alert>
          ) : (
            <List>
              {tasks.map((task) => (
                <ListItem key={task.id} divider>
                  <ListItemIcon>
                    {getStatusIcon(task.status)}
                  </ListItemIcon>
                  <ListItemText
                    primary={
                      <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                        <Typography variant="h6">
                          CCP {task.ccpNumber}: {task.ccpName}
                        </Typography>
                        <Chip
                          label={task.status.toUpperCase()}
                          color={getStatusColor(task.status) as any}
                          size="small"
                        />
                        <Chip
                          label={task.priority.toUpperCase()}
                          color="warning"
                          size="small"
                          variant="outlined"
                        />
                      </Box>
                    }
                    secondary={
                      <Typography variant="body2" color="textSecondary">
                        Product: {task.productName} • Due: {task.dueTime}
                      </Typography>
                    }
                  />
                  <Button
                    variant="contained"
                    startIcon={<Science />}
                    color={task.status === 'overdue' ? 'error' : 'primary'}
                  >
                    Start Monitoring
                  </Button>
                </ListItem>
              ))}
            </List>
          )}
        </CardContent>
      </Card>
    </Box>
  );
};

export default MonitoringConsole;
