import React, { useState } from 'react';
import {
  Box,
  Typography,
  Tabs,
  Tab,
  Paper,
  Container
} from '@mui/material';
import {
  Assignment as AssignmentIcon,
  People as PeopleIcon,
  Assessment as AssessmentIcon
} from '@mui/icons-material';

import ActionsLogManagement from '../components/ActionsLog/ActionsLogManagement';
import InterestedPartiesManagement from '../components/ActionsLog/InterestedPartiesManagement';
import SWOTPESTELAnalysis from '../components/ActionsLog/SWOTPESTELAnalysis';

interface TabPanelProps {
  children?: React.ReactNode;
  index: number;
  value: number;
}

function TabPanel(props: TabPanelProps) {
  const { children, value, index, ...other } = props;

  return (
    <div
      role="tabpanel"
      hidden={value !== index}
      id={`actions-tabpanel-${index}`}
      aria-labelledby={`actions-tab-${index}`}
      {...other}
    >
      {value === index && <Box sx={{ p: 3 }}>{children}</Box>}
    </div>
  );
}

const ActionsLog: React.FC = () => {
  const [activeTab, setActiveTab] = useState(0);

  const handleTabChange = (event: React.SyntheticEvent, newValue: number) => {
    setActiveTab(newValue);
  };

  return (
    <Container maxWidth="xl">
      <Box sx={{ py: 3 }}>
        <Typography variant="h4" component="h1" gutterBottom>
          Actions Log System
        </Typography>
        <Typography variant="body1" color="text.secondary" paragraph>
          Manage actions, interested parties, and strategic analysis for ISO 22000 compliance
        </Typography>

        <Paper sx={{ width: '100%', mt: 3 }}>
          <Box sx={{ borderBottom: 1, borderColor: 'divider' }}>
            <Tabs value={activeTab} onChange={handleTabChange} aria-label="actions log tabs">
              <Tab 
                icon={<AssignmentIcon />} 
                label="Actions Log" 
                iconPosition="start"
              />
              <Tab 
                icon={<PeopleIcon />} 
                label="Interested Parties" 
                iconPosition="start"
              />
              <Tab 
                icon={<AssessmentIcon />} 
                label="SWOT/PESTEL Analysis" 
                iconPosition="start"
              />
            </Tabs>
          </Box>

          <TabPanel value={activeTab} index={0}>
            <ActionsLogManagement />
          </TabPanel>

          <TabPanel value={activeTab} index={1}>
            <InterestedPartiesManagement />
          </TabPanel>

          <TabPanel value={activeTab} index={2}>
            <SWOTPESTELAnalysis />
          </TabPanel>
        </Paper>
      </Box>
    </Container>
  );
};

export default ActionsLog;

