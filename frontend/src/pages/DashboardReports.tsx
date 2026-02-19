import React, { useEffect, useState } from 'react';
import { Box, Paper, Typography } from '@mui/material';
import { complaintsAPI } from '../services/api';
import { ResponsiveContainer, BarChart, Bar, XAxis, YAxis, Tooltip, PieChart, Pie, Cell } from 'recharts';

const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042', '#8884d8', '#82ca9d'];

const DashboardReports: React.FC = () => {
  const [trends, setTrends] = useState<any>(null);
  useEffect(() => {
    (async () => {
      try { const t = await complaintsAPI.trends(); setTrends(t?.data || t); } catch {}
    })();
  }, []);
  return (
    <Box p={3}>
      <Typography variant="h6" fontWeight="bold" sx={{ mb: 2 }}>Complaints Trends</Typography>
      <Box sx={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: 2 }}>
        <Paper sx={{ p: 2, height: 320 }}>
          <Typography variant="subtitle1">Monthly Counts</Typography>
          <ResponsiveContainer width="100%" height={260}>
            <BarChart data={trends?.monthly_counts || []}>
              <XAxis dataKey="month" />
              <YAxis />
              <Tooltip />
              <Bar dataKey="count" fill="#8884d8" />
            </BarChart>
          </ResponsiveContainer>
        </Paper>
        <Paper sx={{ p: 2, height: 320 }}>
          <Typography variant="subtitle1">By Classification</Typography>
          <ResponsiveContainer width="100%" height={260}>
            <PieChart>
              <Pie dataKey="count" data={trends?.by_classification || []} nameKey="classification" cx="50%" cy="50%" outerRadius={80}>
                {(trends?.by_classification || []).map((_: any, idx: number) => (
                  <Cell key={`c-${idx}`} fill={COLORS[idx % COLORS.length]} />
                ))}
              </Pie>
              <Tooltip />
            </PieChart>
          </ResponsiveContainer>
        </Paper>
        <Paper sx={{ p: 2, height: 320 }}>
          <Typography variant="subtitle1">By Severity</Typography>
          <ResponsiveContainer width="100%" height={260}>
            <BarChart data={trends?.by_severity || []}>
              <XAxis dataKey="severity" />
              <YAxis />
              <Tooltip />
              <Bar dataKey="count" fill="#82ca9d" />
            </BarChart>
          </ResponsiveContainer>
        </Paper>
      </Box>
    </Box>
  );
};

export default DashboardReports;


