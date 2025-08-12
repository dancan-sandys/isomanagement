import React from 'react';
import { Box, Typography, Card, CardContent } from '@mui/material';

const DashboardReports: React.FC = () => {
  return (
    <Box sx={{ p: 2 }}>
      <Typography variant="h4" gutterBottom>
        Reports (Coming Soon)
      </Typography>
      <Card>
        <CardContent>
          <Typography variant="body1" color="text.secondary">
            This page will host cross-module reports. For now, use module-specific reporting endpoints (e.g., PRP/HACCP/Traceability) or export data directly.
          </Typography>
        </CardContent>
      </Card>
    </Box>
  );
};

export default DashboardReports;


