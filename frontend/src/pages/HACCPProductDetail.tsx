import React, { useEffect, useRef, useState } from 'react';
import { useParams } from 'react-router-dom';
import { useDispatch, useSelector } from 'react-redux';
import { Box, Grid, Typography, Chip, Tabs, Tab, Button, Stack, Table, TableBody, TableCell, TableContainer, TableHead, TableRow, Paper, Dialog, DialogTitle, DialogContent, DialogActions, TextField, IconButton, FormControl, InputLabel, Select, MenuItem } from '@mui/material';
import { Add, Edit, Visibility, Delete, Security } from '@mui/icons-material';
import { Autocomplete } from '@mui/material';
import { traceabilityAPI, usersAPI } from '../services/api';
import HACCPFlowchartBuilder from '../components/HACCP/FlowchartBuilder';
import HazardDialog from '../components/HACCP/HazardDialog';
import HazardViewDialog from '../components/HACCP/HazardViewDialog';
import { AppDispatch, RootState } from '../store';
import { fetchProduct, setSelectedProduct, createProcessFlow, updateProcessFlow, deleteProcessFlow, createHazard, updateHazard, deleteHazard, createCCP, updateCCP, createOPRP, updateProduct } from '../store/slices/haccpSlice';

function TabPanel({ children, value, index }: { children?: React.ReactNode; value: number; index: number }) {
  return (
    <div role="tabpanel" hidden={value !== index}>
      {value === index && <Box sx={{ py: 3 }}>{children}</Box>}
    </div>
  );
}

const HACCPProductDetail: React.FC = () => {
  const { id } = useParams();
  const productId = Number(id);
  const dispatch = useDispatch<AppDispatch>();
  const { selectedProduct, processFlows, hazards, ccps, oprps } = useSelector((s: RootState) => s.haccp);

  const [selectedTab, setSelectedTab] = useState(0);
  const [processFlowDialogOpen, setProcessFlowDialogOpen] = useState(false);
  const [hazardDialogOpen, setHazardDialogOpen] = useState(false);
  const [hazardViewDialogOpen, setHazardViewDialogOpen] = useState(false);
  const [ccpDialogOpen, setCcpDialogOpen] = useState(false);
  const [selectedFlow, setSelectedFlow] = useState<any>(null);
  const [selectedHazardItem, setSelectedHazardItem] = useState<any>(null);
  const [selectedCcpItem, setSelectedCcpItem] = useState<any>(null);
  const [flowchartDialogOpen, setFlowchartDialogOpen] = useState(false);

  const [flowForm, setFlowForm] = useState({ step_number: '', step_name: '', description: '', equipment: '', temperature: '', time_minutes: '', ph: '', aw: '' });
  // Hazard form removed - now handled by HazardDialog component
  const [ccpForm, setCcpForm] = useState({ hazard_id: '', ccp_number: '', ccp_name: '', description: '', critical_limit_min: '', critical_limit_max: '', critical_limit_unit: '', monitoring_frequency: '', monitoring_method: '', monitoring_responsible: '', monitoring_equipment: '', corrective_actions: '', verification_frequency: '', verification_method: '', verification_responsible: '' });

  const [userSearch, setUserSearch] = useState('');
  const [userOptions, setUserOptions] = useState<Array<{ id: number; username: string; full_name?: string }>>([]);
  const [userLoading, setUserLoading] = useState(false);
  const [userOpen, setUserOpen] = useState(false);
  const userReqIdRef = useRef(0);
  const [monitoringUserValue, setMonitoringUserValue] = useState<{ id: number; username: string; full_name?: string } | null>(null);
  const [verificationUserValue, setVerificationUserValue] = useState<{ id: number; username: string; full_name?: string } | null>(null);
  
  useEffect(() => {
    dispatch(fetchProduct(productId));
  }, [dispatch, productId]);

  useEffect(() => {
    dispatch(setSelectedProduct({ id: productId } as any));
  }, [dispatch, productId]);

  useEffect(() => {
    // Only trigger search when dropdown is open and at least 2 chars typed
    if (!userOpen || (userSearch || '').trim().length < 2) return;
    const reqId = ++userReqIdRef.current;
    setUserLoading(true);
    const t = setTimeout(async () => {
      try {
        const res: any = await usersAPI.getUsers({ page: 1, size: 10, search: userSearch || undefined });
        if (userReqIdRef.current !== reqId) return;
        const items = (res?.data?.items || res?.items || res?.data || []) as Array<any>;
        setUserOptions(items.map((u: any) => ({ id: u.id, username: u.username, full_name: u.full_name })));
      } catch {
        if (userReqIdRef.current !== reqId) return;
        setUserOptions([]);
      } finally {
        if (userReqIdRef.current === reqId) setUserLoading(false);
      }
    }, 250);
    return () => { clearTimeout(t); };
  }, [userSearch, userOpen]);

  // Stabilize selected values when editing an existing CCP
  useEffect(() => {
    const populateSelectedUsers = async () => {
      try {
        if (ccpForm.monitoring_responsible) {
          const idNum = Number(ccpForm.monitoring_responsible);
          if (!monitoringUserValue || monitoringUserValue.id !== idNum) {
            const res: any = await usersAPI.getUser(idNum);
            const u = res?.data || res;
            if (u?.id) setMonitoringUserValue({ id: u.id, username: u.username, full_name: u.full_name });
          }
        } else {
          setMonitoringUserValue(null);
        }
        if (ccpForm.verification_responsible) {
          const idNum = Number(ccpForm.verification_responsible);
          if (!verificationUserValue || verificationUserValue.id !== idNum) {
            const res: any = await usersAPI.getUser(idNum);
            const u = res?.data || res;
            if (u?.id) setVerificationUserValue({ id: u.id, username: u.username, full_name: u.full_name });
          }
        } else {
          setVerificationUserValue(null);
        }
      } catch {}
    };
    populateSelectedUsers();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [ccpForm.monitoring_responsible, ccpForm.verification_responsible]);

  useEffect(() => {
    if (selectedFlow) {
      setFlowForm({ step_number: String(selectedFlow.step_number ?? ''), step_name: selectedFlow.step_name || '', description: selectedFlow.description || '', equipment: selectedFlow.equipment || '', temperature: String(selectedFlow.temperature ?? ''), time_minutes: String(selectedFlow.time_minutes ?? ''), ph: String(selectedFlow.ph ?? ''), aw: String(selectedFlow.aw ?? '') });
    } else {
      setFlowForm({ step_number: '', step_name: '', description: '', equipment: '', temperature: '', time_minutes: '', ph: '', aw: '' });
    }
  }, [selectedFlow]);

  // Hazard form population removed - now handled by HazardDialog component

  useEffect(() => {
    if (selectedCcpItem) {
      setCcpForm({ hazard_id: String(selectedCcpItem.hazard_id ?? ''), ccp_number: selectedCcpItem.ccp_number || '', ccp_name: selectedCcpItem.ccp_name || '', description: selectedCcpItem.description || '', critical_limit_min: String(selectedCcpItem.critical_limit_min ?? ''), critical_limit_max: String(selectedCcpItem.critical_limit_max ?? ''), critical_limit_unit: selectedCcpItem.critical_limit_unit || '', monitoring_frequency: selectedCcpItem.monitoring_frequency || '', monitoring_method: selectedCcpItem.monitoring_method || '', monitoring_responsible: String(selectedCcpItem.monitoring_responsible ?? ''), monitoring_equipment: selectedCcpItem.monitoring_equipment || '', corrective_actions: selectedCcpItem.corrective_actions || '', verification_frequency: selectedCcpItem.verification_frequency || '', verification_method: selectedCcpItem.verification_method || '', verification_responsible: String(selectedCcpItem.verification_responsible ?? '') });
    } else {
      setCcpForm({ hazard_id: '', ccp_number: '', ccp_name: '', description: '', critical_limit_min: '', critical_limit_max: '', critical_limit_unit: '', monitoring_frequency: '', monitoring_method: '', monitoring_responsible: '', monitoring_equipment: '', corrective_actions: '', verification_frequency: '', verification_method: '', verification_responsible: '' });
    }
  }, [selectedCcpItem]);

  const handleTabChange = (_e: any, v: number) => setSelectedTab(v);

  const handleSaveFlow = async () => {
    // Validate required fields
    if (!flowForm.step_number || flowForm.step_number === '') {
      alert('Step number is required');
      return;
    }
    if (!flowForm.step_name || flowForm.step_name.trim() === '') {
      alert('Step name is required');
      return;
    }
    
    const payload: any = { 
      step_number: Number(flowForm.step_number), 
      step_name: flowForm.step_name.trim(), 
      description: flowForm.description, 
      equipment: flowForm.equipment, 
      temperature: flowForm.temperature === '' ? null : Number(flowForm.temperature), 
      time_minutes: flowForm.time_minutes === '' ? null : Number(flowForm.time_minutes), 
      ph: flowForm.ph === '' ? null : Number(flowForm.ph), 
      aw: flowForm.aw === '' ? null : Number(flowForm.aw) 
    };
    try {
      if (selectedFlow) await dispatch(updateProcessFlow({ flowId: selectedFlow.id, flowData: payload })).unwrap();
      else await dispatch(createProcessFlow({ productId, flowData: payload })).unwrap();
      setProcessFlowDialogOpen(false); setSelectedFlow(null); dispatch(fetchProduct(productId));
    } catch {}
  };

  const handleSaveHazard = async (hazardData: any) => {
    const payload: any = { 
      process_step_id: Number(hazardData.process_step_id), 
      hazard_type: hazardData.hazard_type, 
      hazard_name: hazardData.hazard_name.trim(), 
      description: hazardData.description, 
      consequences: hazardData.consequences,
      prp_reference_ids: hazardData.prp_reference_ids || [],
      references: hazardData.references || [], 
      likelihood: Number(hazardData.likelihood), 
      severity: Number(hazardData.severity), 
      control_measures: hazardData.control_measures,
      risk_strategy: hazardData.risk_strategy || 'opprp',
      risk_strategy_justification: hazardData.risk_strategy_justification,
      subsequent_step: hazardData.subsequent_step,
    };

    // Include decision tree answers if provided
    if (hazardData.decision_tree) {
      payload.decision_tree = hazardData.decision_tree;
    }

    try {
      let createdHazard: any;
      
      if (selectedHazardItem) {
        createdHazard = await dispatch(updateHazard({ hazardId: selectedHazardItem.id, hazardData: payload })).unwrap();
      } else {
        createdHazard = await dispatch(createHazard({ productId, hazardData: payload })).unwrap();
      }

      // Create CCP if strategy is CCP
      if (hazardData.ccp && hazardData.risk_strategy === 'ccp') {
        const ccpPayload = {
          hazard_id: createdHazard.id || createdHazard.data?.id,
          ccp_number: hazardData.ccp.ccp_number,
          ccp_name: hazardData.ccp.ccp_name,
          description: hazardData.ccp.description,
          critical_limit_min: hazardData.ccp.critical_limit_min ? Number(hazardData.ccp.critical_limit_min) : null,
          critical_limit_max: hazardData.ccp.critical_limit_max ? Number(hazardData.ccp.critical_limit_max) : null,
          critical_limit_unit: hazardData.ccp.critical_limit_unit,
          monitoring_frequency: hazardData.ccp.monitoring_frequency,
          monitoring_method: hazardData.ccp.monitoring_method,
          corrective_actions: hazardData.ccp.corrective_actions,
        };
        await dispatch(createCCP({ productId, ccpData: ccpPayload })).unwrap();
      }

      // Create OPRP if strategy is OPRP
      if (hazardData.oprp && hazardData.risk_strategy === 'opprp') {
        const oprpPayload = {
          hazard_id: createdHazard.id || createdHazard.data?.id,
          oprp_number: hazardData.oprp.oprp_number,
          oprp_name: hazardData.oprp.oprp_name,
          description: hazardData.oprp.description,
          justification: hazardData.risk_strategy_justification,
          // OPRP-specific fields
          objective: hazardData.oprp.objective,
          sop_reference: hazardData.oprp.sop_reference,
        };
        await dispatch(createOPRP({ productId, oprpData: oprpPayload })).unwrap();
      }

      setHazardDialogOpen(false); 
      setSelectedHazardItem(null); 
      dispatch(fetchProduct(productId));
    } catch (error) {
      console.error('Failed to save hazard:', error);
    }
  };

  const handleSaveCCP = async () => {
    const payload: any = { hazard_id: ccpForm.hazard_id === '' ? null : Number(ccpForm.hazard_id), ccp_number: ccpForm.ccp_number, ccp_name: ccpForm.ccp_name, description: ccpForm.description, critical_limit_min: ccpForm.critical_limit_min === '' ? null : Number(ccpForm.critical_limit_min), critical_limit_max: ccpForm.critical_limit_max === '' ? null : Number(ccpForm.critical_limit_max), critical_limit_unit: ccpForm.critical_limit_unit, monitoring_frequency: ccpForm.monitoring_frequency, monitoring_method: ccpForm.monitoring_method, monitoring_responsible: ccpForm.monitoring_responsible === '' ? null : Number(ccpForm.monitoring_responsible), monitoring_equipment: ccpForm.monitoring_equipment, corrective_actions: ccpForm.corrective_actions, verification_frequency: ccpForm.verification_frequency, verification_method: ccpForm.verification_method, verification_responsible: ccpForm.verification_responsible === '' ? null : Number(ccpForm.verification_responsible) };
    try {
      if (selectedCcpItem) await dispatch(updateCCP({ ccpId: selectedCcpItem.id, ccpData: payload })).unwrap();
      else await dispatch(createCCP({ productId, ccpData: payload })).unwrap();
      setCcpDialogOpen(false); setSelectedCcpItem(null); dispatch(fetchProduct(productId));
    } catch {}
  };

  const [monitoringForm, setMonitoringForm] = useState<{ ccp_id?: string; batch?: string; batch_id?: string; value?: string; unit?: string; evidence_files?: string }>({});
  const [monitoringLogs, setMonitoringLogs] = useState<any[]>([]);
  const [batchOptions, setBatchOptions] = useState<any[]>([]);
  const [batchSearch, setBatchSearch] = useState('');
  const [batchOpen, setBatchOpen] = useState(false);

  // Fetch batches when autocomplete opens or search text changes
  useEffect(() => {
    let active = true;
    if (!batchOpen) return () => { active = false; };
    const t = setTimeout(async () => {
      try {
        const resp: any = await traceabilityAPI.getBatches({ search: batchSearch, size: 10 });
        const items = resp?.data?.items || resp?.items || [];
        if (active) setBatchOptions(items);
      } catch (e) {
        if (active) setBatchOptions([]);
      }
    }, 250);
    return () => { active = false; clearTimeout(t); };
  }, [batchOpen, batchSearch]);

  // Fetch existing monitoring logs whenever a CCP is selected
  useEffect(() => {
    let active = true;
    const fetchLogs = async () => {
      const ccpIdStr = monitoringForm.ccp_id || '';
      if (!ccpIdStr) { if (active) setMonitoringLogs([]); return; }
      try {
        const api = (await import('../services/api')).api;
        const resp = await api.get(`/haccp/ccps/${Number(ccpIdStr)}/monitoring-logs`);
        const logsJson = resp.data;
        const items = logsJson?.data?.items || logsJson?.items || [];
        if (active) setMonitoringLogs(items);
      } catch {
        if (active) setMonitoringLogs([]);
      }
    };
    fetchLogs();
    return () => { active = false; };
  }, [monitoringForm.ccp_id]);

  const [riskConfigDialogOpen, setRiskConfigDialogOpen] = useState(false);
  const [riskConfigForm, setRiskConfigForm] = useState({
    calculation_method: 'multiplication',
    likelihood_scale: 5,
    severity_scale: 5,
    risk_thresholds: {
      low_threshold: 4,
      medium_threshold: 8,
      high_threshold: 15,
    },
  });

  const handleSaveRiskConfig = async () => {
    try {
      // Validate form data
      if (!riskConfigForm.calculation_method) {
        alert('Please select a calculation method');
        return;
      }
      
      if (!riskConfigForm.likelihood_scale || riskConfigForm.likelihood_scale < 1 || riskConfigForm.likelihood_scale > 10) {
        alert('Please enter a valid likelihood scale (1-10)');
        return;
      }
      
      if (!riskConfigForm.severity_scale || riskConfigForm.severity_scale < 1 || riskConfigForm.severity_scale > 10) {
        alert('Please enter a valid severity scale (1-10)');
        return;
      }
      
      if (!riskConfigForm.risk_thresholds.low_threshold || 
          !riskConfigForm.risk_thresholds.medium_threshold || 
          !riskConfigForm.risk_thresholds.high_threshold) {
        alert('Please enter all risk thresholds');
        return;
      }
      
      if (riskConfigForm.risk_thresholds.low_threshold >= riskConfigForm.risk_thresholds.medium_threshold ||
          riskConfigForm.risk_thresholds.medium_threshold >= riskConfigForm.risk_thresholds.high_threshold) {
        alert('Risk thresholds must be in ascending order: Low < Medium < High');
        return;
      }
      
      console.log('Saving risk config:', { productId, riskConfigForm });
      const result = await dispatch(updateProduct({ productId, productData: { risk_config: riskConfigForm } })).unwrap();
      console.log('Risk config saved successfully:', result);
      setRiskConfigDialogOpen(false);
      dispatch(fetchProduct(productId));
    } catch (error: any) {
      console.error('Failed to save risk config:', error);
      const errorMessage = error?.response?.data?.detail || error?.message || 'Failed to save risk config';
      alert(`Failed to save risk config: ${errorMessage}`);
    }
  };

  useEffect(() => {
    console.log('Selected product risk config:', selectedProduct?.risk_config);
    if (selectedProduct?.risk_config) {
      setRiskConfigForm(selectedProduct.risk_config);
    }
  }, [selectedProduct?.risk_config]);

  return (
    <Box sx={{ p: 3 }}>
      {/* <HACCPBreadcrumbs 
        customTitle="Product Details" 
        productName={selectedProduct?.name}
      /> */}
      <Typography variant="h4" gutterBottom>Product Details</Typography>
      {selectedProduct && (
        <Box sx={{ mb: 3 }}>
          <Typography variant="h5">{selectedProduct.name}</Typography>
          <Typography color="textSecondary">{selectedProduct.product_code}</Typography>
          <Stack direction="row" spacing={2} sx={{ mt: 1 }}>
            <Chip label={selectedProduct.haccp_plan_approved ? 'Plan Approved' : 'Plan Pending'} color={selectedProduct.haccp_plan_approved ? 'success' : 'warning'} />
            <Chip label={`${hazards.length} Hazards`} color="secondary" />
            <Chip label={`${ccps.length} CCPs`} color="error" />
            <Chip label={`${oprps.length} OPRPs`} color="warning" />
          </Stack>
        </Box>
      )}

      <Tabs value={selectedTab} onChange={handleTabChange}>
        <Tab label="Process Flow" />
        <Tab label="Hazards" />
        <Tab label="CCPs" />
        <Tab label="OPRPs" />
        <Tab label="Monitoring" />
        <Tab label="Risk Configuration" />
      </Tabs>

      <TabPanel value={selectedTab} index={0}>
        <Box sx={{ mb: 2, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <Typography variant="h6">Process Flow</Typography>
          <Box sx={{ display: 'flex', gap: 1 }}>
            <Button variant="outlined" onClick={() => setFlowchartDialogOpen(true)}>Open Flowchart Builder</Button>
            <Button variant="contained" startIcon={<Add />} onClick={() => { setSelectedFlow(null); setProcessFlowDialogOpen(true); }}>Add Step</Button>
          </Box>
        </Box>
        <TableContainer component={Paper}>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell>Step</TableCell>
                <TableCell>Name</TableCell>
                <TableCell>Equipment</TableCell>
                <TableCell>Temperature</TableCell>
                <TableCell>Time</TableCell>
                <TableCell>Actions</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {processFlows.map((flow) => (
                <TableRow key={flow.id}>
                  <TableCell>{flow.step_number}</TableCell>
                  <TableCell>{flow.step_name}</TableCell>
                  <TableCell>{flow.equipment}</TableCell>
                  <TableCell>{flow.temperature}°C</TableCell>
                  <TableCell>{flow.time_minutes} min</TableCell>
                  <TableCell>
                    <Stack direction="row" spacing={1}>
                      <IconButton size="small" onClick={() => { setSelectedFlow(flow); setProcessFlowDialogOpen(true); }}><Edit /></IconButton>
                      <IconButton size="small" onClick={() => { if (window.confirm('Delete this process step?')) dispatch(deleteProcessFlow(flow.id)).then(() => dispatch(fetchProduct(productId))); }}><Delete /></IconButton>
                    </Stack>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </TableContainer>
      </TabPanel>

      <TabPanel value={selectedTab} index={1}>
        <Box sx={{ mb: 2, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <Typography variant="h6">Hazards</Typography>
          <Button variant="contained" startIcon={<Add />} onClick={() => { setSelectedHazardItem(null); setHazardDialogOpen(true); }}>Add Hazard</Button>
        </Box>
        <Grid container spacing={2}>
          {hazards.map((hazard) => (
            <Grid item xs={12} sm={6} md={4} key={hazard.id}>
              <Paper sx={{ p: 2 }}>
                <Typography variant="h6">{hazard.hazard_name}</Typography>
                <Typography color="textSecondary">{hazard.hazard_type}</Typography>
                <Typography variant="body2" paragraph>{hazard.description}</Typography>
                <Stack direction="row" spacing={1} flexWrap="wrap" gap={0.5}>
                  <Chip label={`Risk: ${hazard.risk_level}`} color="warning" size="small" />
                  <Chip label={`Score: ${hazard.risk_score}`} color="primary" size="small" />
                  {hazard.risk_strategy && hazard.risk_strategy !== 'not_determined' && (
                    <Chip 
                      label={hazard.risk_strategy === 'ccp' ? 'CCP' : hazard.risk_strategy === 'opprp' ? 'OPRP' : hazard.risk_strategy === 'use_existing_prps' ? 'PRPs' : 'Analysis Needed'} 
                      color={hazard.risk_strategy === 'ccp' ? 'error' : hazard.risk_strategy === 'opprp' ? 'warning' : 'info'} 
                      size="small" 
                    />
                  )}
                  {hazard.is_ccp === true && <Chip label="CCP" color="error" size="small" />}
                </Stack>
                <Stack direction="row" spacing={1} sx={{ mt: 1, justifyContent: 'flex-end' }}>
                  <IconButton 
                    size="small" 
                    onClick={() => { 
                      setSelectedHazardItem(hazard); 
                      setHazardViewDialogOpen(true); 
                    }} 
                    title="View Hazard"
                  >
                    <Visibility />
                  </IconButton>
                  <IconButton 
                    size="small" 
                    onClick={async () => { 
                      if (window.confirm('Delete this hazard?')) {
                        try {
                          await dispatch(deleteHazard(hazard.id)).unwrap();
                          await dispatch(fetchProduct(productId));
                          alert('Hazard deleted successfully!');
                        } catch (error: any) {
                          console.error('Failed to delete hazard:', error);
                          alert(`Failed to delete hazard: ${error}`);
                        }
                      }
                    }}
                    title="Delete Hazard"
                  >
                    <Delete />
                  </IconButton>
                </Stack>
              </Paper>
            </Grid>
          ))}
        </Grid>
      </TabPanel>

      <TabPanel value={selectedTab} index={2}>
        <Box sx={{ mb: 2 }}>
          <Typography variant="h6">Critical Control Points</Typography>
        </Box>
        <Grid container spacing={2}>
          {ccps.map((ccp) => {
            // Check if CCP has incomplete fields
            const hasEmptyFields = !ccp.ccp_number || !ccp.ccp_name || !ccp.description || 
                                  !ccp.critical_limit_min || !ccp.critical_limit_max || 
                                  !ccp.critical_limit_unit || !ccp.monitoring_frequency || 
                                  !ccp.monitoring_method || !ccp.corrective_actions ||
                                  !ccp.monitoring_responsible || !ccp.verification_responsible;
            
            return (
              <Grid item xs={12} sm={6} md={4} key={ccp.id}>
                <Paper sx={{ p: 2 }}>
                  <Typography variant="h6">{ccp.ccp_name}</Typography>
                  <Typography color="textSecondary">{ccp.ccp_number}</Typography>
                  <Typography variant="body2" paragraph>{ccp.description}</Typography>
                  {ccp.critical_limit_min && ccp.critical_limit_max && (
                    <Typography variant="body2" color="textSecondary">Limits: {ccp.critical_limit_min} - {ccp.critical_limit_max} {ccp.critical_limit_unit}</Typography>
                  )}
                  <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mt: 1 }}>
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                      {hasEmptyFields ? (
                        <>
                          <Typography variant="body2" color="error.main">
                            This ccp needs a complete haccp plan
                          </Typography>
                          <Chip 
                            icon={<Security />} 
                            label="" 
                            size="small" 
                            sx={{ bgcolor: 'error.main', cursor: 'pointer', '& .MuiChip-icon': { color: 'white' } }} 
                            onClick={() => { setSelectedCcpItem(ccp); setCcpDialogOpen(true); }} 
                          />
                        </>
                      ) : (
                        <Chip 
                          icon={<Security />} 
                          label="" 
                          size="small" 
                          color="primary" 
                          sx={{ cursor: 'pointer' }} 
                          onClick={() => { setSelectedCcpItem(ccp); setCcpDialogOpen(true); }} 
                        />
                      )}
                    </Box>
                  </Box>
                </Paper>
              </Grid>
            );
          })}
        </Grid>
      </TabPanel>

      <TabPanel value={selectedTab} index={3}>
        <Box sx={{ mb: 2, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <Typography variant="h6">Operational Prerequisite Programs (OPRPs)</Typography>
        </Box>
        <Grid container spacing={2}>
          {oprps.map((oprp: any) => (
            <Grid item xs={12} sm={6} md={4} key={oprp.id}>
              <Paper sx={{ p: 2 }}>
                <Typography variant="h6">{oprp.oprp_name}</Typography>
                <Typography color="textSecondary" variant="body2" gutterBottom>
                  {oprp.oprp_number}
                </Typography>
                <Typography variant="body2" paragraph>
                  {oprp.description}
                </Typography>
                <Stack direction="row" spacing={1} flexWrap="wrap" gap={0.5}>
                  <Chip 
                    label={oprp.status || 'Active'} 
                    color={oprp.status === 'active' ? 'success' : 'default'} 
                    size="small" 
                  />
                  {oprp.monitoring_frequency && (
                    <Chip 
                      label={`Monitor: ${oprp.monitoring_frequency}`} 
                      size="small" 
                      variant="outlined"
                    />
                  )}
                </Stack>
                {oprp.operational_limits && (
                  <Box sx={{ mt: 1, p: 1, bgcolor: 'background.default', borderRadius: 1 }}>
                    <Typography variant="caption" color="textSecondary">
                      Operational Limits:
                    </Typography>
                    <Typography variant="body2">
                      {oprp.operational_limits}
                    </Typography>
                  </Box>
                )}
              </Paper>
            </Grid>
          ))}
        </Grid>
        {oprps.length === 0 && (
          <Paper sx={{ p: 3, textAlign: 'center' }}>
            <Typography color="textSecondary">
              No OPRPs defined yet. OPRPs are created automatically when a hazard is assigned the OPRP risk strategy.
            </Typography>
          </Paper>
        )}
      </TabPanel>

      <TabPanel value={selectedTab} index={4}>
        <Typography variant="h6" gutterBottom>Monitoring & Verification</Typography>
        <Stack spacing={2} sx={{ maxWidth: 700, mt: 1 }}>
          <Autocomplete options={ccps} getOptionLabel={(ccp: any) => `${ccp.ccp_number || ''} - ${ccp.ccp_name || ''}`.trim()} value={ccps.find((c: any) => String(c.id) === (monitoringForm.ccp_id || '')) || null} onChange={(_, val: any) => setMonitoringForm({ ...monitoringForm, ccp_id: val ? String(val.id) : '' })} isOptionEqualToValue={(opt: any, val: any) => opt.id === val.id} renderInput={(params) => <TextField {...params} label="Select CCP" placeholder="Choose CCP for monitoring" />} />
          <Autocomplete
            options={batchOptions}
            open={batchOpen}
            onOpen={() => setBatchOpen(true)}
            onClose={() => setBatchOpen(false)}
            getOptionLabel={(b: any) => b?.batch_number || ''}
            value={batchOptions.find((b: any) => String(b?.id || '') === (monitoringForm.batch_id || '')) || null}
            onChange={(_, val: any) => setMonitoringForm({ ...monitoringForm, batch_id: val ? String(val.id) : '', batch: val ? String(val.batch_number) : '' })}
            inputValue={batchSearch}
            onInputChange={(_, val) => setBatchSearch(val)}
            isOptionEqualToValue={(opt: any, val: any) => opt?.id === val?.id}
            renderInput={(params) => <TextField {...params} label="Batch" placeholder="Search batches..." />}
          />
          <TextField type="number" label="Measured Value" value={monitoringForm.value || ''} onChange={e => setMonitoringForm({ ...monitoringForm, value: e.target.value })} />
          <TextField label="Unit" value={monitoringForm.unit || ''} onChange={e => setMonitoringForm({ ...monitoringForm, unit: e.target.value })} />
          {/* Evidence upload */}
          <Box>
            <Typography variant="subtitle2" gutterBottom>Attach Evidence (photos, files)</Typography>
            <input
              type="file"
              multiple
              onChange={async (e) => {
                const files = e.target.files;
                if (!files || !monitoringForm.ccp_id) return;
                const api = (await import('../services/api')).api;
                const ccpId = Number(monitoringForm.ccp_id);
                const uploaded: string[] = [];
                for (const file of Array.from(files)) {
                  const form = new FormData();
                  form.append('file', file);
                  try {
                    const res = await api.post(`/haccp/ccps/${ccpId}/monitoring-logs/upload-evidence`, form, {
                      headers: { 'Content-Type': 'multipart/form-data' },
                    });
                    const data = res?.data?.data || res?.data;
                    if (data?.file_path) uploaded.push(data.file_path);
                  } catch (err) {
                    console.error('Evidence upload failed', err);
                    alert(`Failed to upload ${file.name}`);
                  }
                }
                if (uploaded.length) {
                  setMonitoringForm({ ...monitoringForm, evidence_files: JSON.stringify(uploaded) });
                }
              }}
            />
          </Box>
          <Stack direction="row" spacing={2}>
            <Button variant="contained" disabled={!monitoringForm.ccp_id} onClick={async () => {
              const ccpId = Number(monitoringForm.ccp_id);
              try {
                // Prepare the request body, filtering out undefined values
                const requestBody: any = {};
                
                if (monitoringForm.batch_id) {
                  requestBody.batch_id = Number(monitoringForm.batch_id);
                }
                if (monitoringForm.batch) {
                  requestBody.batch_number = monitoringForm.batch;
                }
                if (monitoringForm.value && !isNaN(Number(monitoringForm.value))) {
                  requestBody.measured_value = Number(monitoringForm.value);
                } else {
                  alert('Please enter a valid measured value');
                  return;
                }
                if (monitoringForm.unit) {
                  requestBody.unit = monitoringForm.unit;
                }
                if (monitoringForm.evidence_files) {
                  requestBody.evidence_files = monitoringForm.evidence_files;
                }
                
                console.log('Sending monitoring log request:', requestBody);
                
                // Use the API service instead of direct fetch
                const api = (await import('../services/api')).api;
                await api.post(`/haccp/ccps/${ccpId}/monitoring-logs/enhanced`, requestBody);
                
                // reload logs
                try {
                  const resp = await api.get(`/haccp/ccps/${ccpId}/monitoring-logs`);
                  const logsJson = resp.data;
                  const items = logsJson?.data?.items || logsJson?.items || [];
                  setMonitoringLogs(items);
                } catch {}
                // open NC if created for this batch
                if (monitoringForm.batch) {
                  const res = await api.get(`/nonconformance/haccp/recent-nc?ccp_id=${ccpId}&batch_number=${encodeURIComponent(monitoringForm.batch)}`);
                  const data = res.data;
                  if (data?.found) window.open(`/nonconformance/${data.id}`, '_blank');
                }
              } catch (error) {
                console.error('Failed to create monitoring log:', error);
                alert('Failed to create monitoring log');
              }
            }}>Record Monitoring Log</Button>
          </Stack>
          <Typography variant="body2" color="text.secondary">After saving, if out-of-spec, a Non-Conformance will be auto-created and opened.</Typography>

          {/* Logs table */}
          {monitoringForm.ccp_id && (
            <Box>
              <Typography variant="subtitle1" sx={{ mt: 2, mb: 1 }}>Recent Monitoring Logs</Typography>
              <TableContainer component={Paper}>
                <Table size="small">
                  <TableHead>
                    <TableRow>
                      <TableCell>Date/Time</TableCell>
                      <TableCell>Batch</TableCell>
                      <TableCell align="right">Value</TableCell>
                      <TableCell>Unit</TableCell>
                      <TableCell>Status</TableCell>
                      <TableCell>Actions</TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {monitoringLogs.map((log: any) => (
                      <TableRow key={log.id}>
                        <TableCell>{log.monitoring_time || log.created_at}</TableCell>
                        <TableCell>{log.batch_number}</TableCell>
                        <TableCell align="right">{log.measured_value}</TableCell>
                        <TableCell>{log.unit}</TableCell>
                        <TableCell>
                          <Chip size="small" color={log.is_within_limits ? 'success' : 'error'} label={log.is_within_limits ? 'In Spec' : 'Out of Spec'} />
                        </TableCell>
                        <TableCell>
                          <Button size="small" onClick={async () => {
                            const ccpId = Number(monitoringForm.ccp_id);
                            const api = (await import('../services/api')).api;
                            const res = await api.get(`/nonconformance/haccp/recent-nc?ccp_id=${ccpId}&batch_number=${encodeURIComponent(log.batch_number || '')}`);
                            const data = res.data;
                            if (data?.found) window.open(`/nonconformance/${data.id}`, '_blank');
                            else alert('No NC linked for this reading');
                          }}>Open NC</Button>
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </TableContainer>
            </Box>
          )}
        </Stack>
      </TabPanel>

      <TabPanel value={selectedTab} index={5}>
        <Box sx={{ mb: 2, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <Typography variant="h6">Risk Configuration</Typography>
          <Button variant="contained" onClick={() => setRiskConfigDialogOpen(true)}>
            {selectedProduct?.risk_config ? 'Edit Risk Config' : 'Configure Risk Settings'}
          </Button>
        </Box>
        
        {selectedProduct?.risk_config ? (
          <Paper sx={{ p: 3 }}>
            <Grid container spacing={3}>
              <Grid item xs={12} md={6}>
                <Typography variant="subtitle1" gutterBottom>Calculation Method</Typography>
                <Chip label={selectedProduct.risk_config.calculation_method} color="primary" />
              </Grid>
              <Grid item xs={12} md={6}>
                <Typography variant="subtitle1" gutterBottom>Scales</Typography>
                <Typography>Likelihood: 1-{selectedProduct.risk_config.likelihood_scale}</Typography>
                <Typography>Severity: 1-{selectedProduct.risk_config.severity_scale}</Typography>
              </Grid>
              <Grid item xs={12}>
                <Typography variant="subtitle1" gutterBottom>Risk Thresholds</Typography>
                <Stack direction="row" spacing={2}>
                  <Chip label={`Low: ≤${selectedProduct.risk_config.risk_thresholds.low_threshold}`} color="success" />
                  <Chip label={`Medium: ${selectedProduct.risk_config.risk_thresholds.low_threshold + 1}-${selectedProduct.risk_config.risk_thresholds.medium_threshold}`} color="warning" />
                  <Chip label={`High: ≥${selectedProduct.risk_config.risk_thresholds.medium_threshold + 1}`} color="error" />
                </Stack>
              </Grid>
            </Grid>
          </Paper>
        ) : (
          <Paper sx={{ p: 3, textAlign: 'center' }}>
            <Typography color="textSecondary" gutterBottom>
              No risk configuration set for this product
            </Typography>
            <Typography variant="body2" color="textSecondary">
              Configure risk calculation parameters to enable proper hazard risk assessment and CCP determination.
            </Typography>
          </Paper>
        )}
      </TabPanel>

      {/* Dialogs */}
      <HACCPFlowchartBuilder
        open={flowchartDialogOpen}
        onClose={() => setFlowchartDialogOpen(false)}
        productId={String(productId)}
        productName={selectedProduct?.name || ''}
        hazards={hazards as any}
        ccps={ccps as any}
      />
      <Dialog open={processFlowDialogOpen} onClose={() => { setProcessFlowDialogOpen(false); setSelectedFlow(null); }} maxWidth="md" fullWidth>
        <DialogTitle>{selectedFlow ? 'Edit Process Step' : 'Add Process Step'}</DialogTitle>
        <DialogContent>
          <Grid container spacing={2} sx={{ mt: 1 }}>
            <Grid item xs={12} md={3}><TextField fullWidth type="number" label="Step #" value={flowForm.step_number} onChange={(e) => setFlowForm({ ...flowForm, step_number: e.target.value })} /></Grid>
            <Grid item xs={12} md={9}><TextField fullWidth label="Step Name" value={flowForm.step_name} onChange={(e) => setFlowForm({ ...flowForm, step_name: e.target.value })} /></Grid>
            <Grid item xs={12}><TextField fullWidth multiline rows={3} label="Description" value={flowForm.description} onChange={(e) => setFlowForm({ ...flowForm, description: e.target.value })} /></Grid>
            <Grid item xs={12} md={6}><TextField fullWidth label="Equipment" value={flowForm.equipment} onChange={(e) => setFlowForm({ ...flowForm, equipment: e.target.value })} /></Grid>
            <Grid item xs={12} md={3}><TextField fullWidth type="number" label="Temp (°C)" value={flowForm.temperature} onChange={(e) => setFlowForm({ ...flowForm, temperature: e.target.value })} /></Grid>
            <Grid item xs={12} md={3}><TextField fullWidth type="number" label="Time (min)" value={flowForm.time_minutes} onChange={(e) => setFlowForm({ ...flowForm, time_minutes: e.target.value })} /></Grid>
            <Grid item xs={12} md={3}><TextField fullWidth type="number" label="pH" value={flowForm.ph} onChange={(e) => setFlowForm({ ...flowForm, ph: e.target.value })} /></Grid>
            <Grid item xs={12} md={3}><TextField fullWidth type="number" label="aW" value={flowForm.aw} onChange={(e) => setFlowForm({ ...flowForm, aw: e.target.value })} /></Grid>
          </Grid>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => { setProcessFlowDialogOpen(false); setSelectedFlow(null); }}>Cancel</Button>
          <Button variant="contained" onClick={handleSaveFlow}>Save</Button>
        </DialogActions>
      </Dialog>

      {/* New Hazard Dialog Component - For Creating New Hazards */}
      <HazardDialog
        open={hazardDialogOpen}
        onClose={() => {
          setHazardDialogOpen(false);
          setSelectedHazardItem(null);
        }}
        onSave={handleSaveHazard}
        processFlows={processFlows}
        editData={null}
      />

      {/* Hazard View Dialog - For Viewing Existing Hazards */}
      <HazardViewDialog
        open={hazardViewDialogOpen}
        onClose={() => {
          setHazardViewDialogOpen(false);
          setSelectedHazardItem(null);
        }}
        hazardData={selectedHazardItem}
        processFlows={processFlows}
      />

      <Dialog open={ccpDialogOpen} onClose={() => { setCcpDialogOpen(false); setSelectedCcpItem(null); }} maxWidth="md" fullWidth>
        <DialogTitle>{selectedCcpItem ? 'Edit CCP' : 'Add CCP'}</DialogTitle>
        <DialogContent>
          <Grid container spacing={2} sx={{ mt: 1 }}>
            <Grid item xs={12} md={4}>
              <TextField 
                fullWidth 
                type="number" 
                label="Hazard ID" 
                value={ccpForm.hazard_id} 
                onChange={(e) => setCcpForm({ ...ccpForm, hazard_id: e.target.value })} 
                disabled
                helperText="Hazard ID cannot be changed"
              />
            </Grid>
            <Grid item xs={12} md={4}><TextField fullWidth label="CCP Number" value={ccpForm.ccp_number} onChange={(e) => setCcpForm({ ...ccpForm, ccp_number: e.target.value })} disabled={!!selectedCcpItem} /></Grid>
            <Grid item xs={12} md={4}><TextField fullWidth label="CCP Name" value={ccpForm.ccp_name} onChange={(e) => setCcpForm({ ...ccpForm, ccp_name: e.target.value })} disabled={!!selectedCcpItem} /></Grid>
            <Grid item xs={12}><TextField fullWidth multiline rows={3} label="Description" value={ccpForm.description} onChange={(e) => setCcpForm({ ...ccpForm, description: e.target.value })} disabled={!!selectedCcpItem} /></Grid>
            <Grid item xs={12} md={4}><TextField fullWidth type="number" label="Critical Min" value={ccpForm.critical_limit_min} onChange={(e) => setCcpForm({ ...ccpForm, critical_limit_min: e.target.value })} disabled={!!selectedCcpItem} /></Grid>
            <Grid item xs={12} md={4}><TextField fullWidth type="number" label="Critical Max" value={ccpForm.critical_limit_max} onChange={(e) => setCcpForm({ ...ccpForm, critical_limit_max: e.target.value })} disabled={!!selectedCcpItem} /></Grid>
            <Grid item xs={12} md={4}><TextField fullWidth label="Unit" value={ccpForm.critical_limit_unit} onChange={(e) => setCcpForm({ ...ccpForm, critical_limit_unit: e.target.value })} disabled={!!selectedCcpItem} /></Grid>
            <Grid item xs={12} md={6}><TextField fullWidth label="Monitoring Frequency" value={ccpForm.monitoring_frequency} onChange={(e) => setCcpForm({ ...ccpForm, monitoring_frequency: e.target.value })} disabled={!!selectedCcpItem} /></Grid>
            <Grid item xs={12} md={6}><TextField fullWidth label="Monitoring Method" value={ccpForm.monitoring_method} onChange={(e) => setCcpForm({ ...ccpForm, monitoring_method: e.target.value })} disabled={!!selectedCcpItem} /></Grid>
            <Grid item xs={12} md={6}>
              <Autocomplete 
                options={userOptions}
                getOptionLabel={(opt) => (opt.full_name ? `${opt.full_name} (${opt.username})` : opt.username)}
                value={monitoringUserValue}
                onChange={(_, val) => { setMonitoringUserValue(val); setCcpForm({ ...ccpForm, monitoring_responsible: val ? String(val.id) : '' }); }}
                onInputChange={(_, val) => setUserSearch(val)}
                onOpen={() => setUserOpen(true)}
                onClose={() => setUserOpen(false)}
                loading={userLoading}
                isOptionEqualToValue={(opt, val) => opt.id === val.id}
                renderInput={(params) => <TextField {...params} label="Monitoring Responsible" placeholder="Search user..." fullWidth />} />
            </Grid>
            <Grid item xs={12} md={6}><TextField fullWidth label="Monitoring Equipment" value={ccpForm.monitoring_equipment} onChange={(e) => setCcpForm({ ...ccpForm, monitoring_equipment: e.target.value })} /></Grid>
            <Grid item xs={12}><TextField fullWidth label="Corrective Actions" value={ccpForm.corrective_actions} onChange={(e) => setCcpForm({ ...ccpForm, corrective_actions: e.target.value })} disabled={!!selectedCcpItem} /></Grid>
            <Grid item xs={12} md={6}><TextField fullWidth label="Verification Frequency" value={ccpForm.verification_frequency} onChange={(e) => setCcpForm({ ...ccpForm, verification_frequency: e.target.value })} /></Grid>
            <Grid item xs={12} md={6}><TextField fullWidth label="Verification Method" value={ccpForm.verification_method} onChange={(e) => setCcpForm({ ...ccpForm, verification_method: e.target.value })} /></Grid>
            <Grid item xs={12}>
              <Autocomplete 
                options={userOptions}
                getOptionLabel={(opt) => (opt.full_name ? `${opt.full_name} (${opt.username})` : opt.username)}
                value={verificationUserValue}
                onChange={(_, val) => { setVerificationUserValue(val); setCcpForm({ ...ccpForm, verification_responsible: val ? String(val.id) : '' }); }}
                onInputChange={(_, val) => setUserSearch(val)}
                onOpen={() => setUserOpen(true)}
                onClose={() => setUserOpen(false)}
                loading={userLoading}
                isOptionEqualToValue={(opt, val) => opt.id === val.id}
                renderInput={(params) => <TextField {...params} label="Verification Responsible" placeholder="Search user..." fullWidth />} />
            </Grid>
          </Grid>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => { setCcpDialogOpen(false); setSelectedCcpItem(null); }}>Cancel</Button>
          <Button variant="contained" onClick={handleSaveCCP}>Save</Button>
        </DialogActions>
      </Dialog>

      {/* Risk Configuration Dialog */}
      <Dialog open={riskConfigDialogOpen} onClose={() => setRiskConfigDialogOpen(false)} maxWidth="md" fullWidth>
        <DialogTitle>Product Risk Configuration</DialogTitle>
        <DialogContent>
          <Grid container spacing={2} sx={{ mt: 1 }}>
            <Grid item xs={12} md={6}>
              <FormControl fullWidth>
                <InputLabel>Calculation Method</InputLabel>
                <Select
                  value={riskConfigForm.calculation_method}
                  onChange={(e) => setRiskConfigForm({ ...riskConfigForm, calculation_method: e.target.value })}
                >
                  <MenuItem value="multiplication">Multiplication (Likelihood × Severity)</MenuItem>
                  <MenuItem value="addition">Addition (Likelihood + Severity)</MenuItem>
                  <MenuItem value="matrix">Matrix (Custom Risk Matrix)</MenuItem>
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12} md={3}>
              <TextField
                fullWidth
                type="number"
                label="Likelihood Scale"
                value={riskConfigForm.likelihood_scale}
                onChange={(e) => setRiskConfigForm({ ...riskConfigForm, likelihood_scale: Number(e.target.value) })}
                inputProps={{ min: 1, max: 10 }}
              />
            </Grid>
            <Grid item xs={12} md={3}>
              <TextField
                fullWidth
                type="number"
                label="Severity Scale"
                value={riskConfigForm.severity_scale}
                onChange={(e) => setRiskConfigForm({ ...riskConfigForm, severity_scale: Number(e.target.value) })}
                inputProps={{ min: 1, max: 10 }}
              />
            </Grid>
            <Grid item xs={12}>
              <Typography variant="subtitle1" gutterBottom>Risk Thresholds</Typography>
            </Grid>
            <Grid item xs={12} md={4}>
              <TextField
                fullWidth
                type="number"
                label="Low Threshold"
                value={riskConfigForm.risk_thresholds.low_threshold}
                onChange={(e) => setRiskConfigForm({
                  ...riskConfigForm,
                  risk_thresholds: { ...riskConfigForm.risk_thresholds, low_threshold: Number(e.target.value) }
                })}
              />
            </Grid>
            <Grid item xs={12} md={4}>
              <TextField
                fullWidth
                type="number"
                label="Medium Threshold"
                value={riskConfigForm.risk_thresholds.medium_threshold}
                onChange={(e) => setRiskConfigForm({
                  ...riskConfigForm,
                  risk_thresholds: { ...riskConfigForm.risk_thresholds, medium_threshold: Number(e.target.value) }
                })}
              />
            </Grid>
            <Grid item xs={12} md={4}>
              <TextField
                fullWidth
                type="number"
                label="High Threshold"
                value={riskConfigForm.risk_thresholds.high_threshold}
                onChange={(e) => setRiskConfigForm({
                  ...riskConfigForm,
                  risk_thresholds: { ...riskConfigForm.risk_thresholds, high_threshold: Number(e.target.value) }
                })}
              />
            </Grid>
          </Grid>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setRiskConfigDialogOpen(false)}>Cancel</Button>
          <Button variant="contained" onClick={handleSaveRiskConfig}>Save</Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default HACCPProductDetail;

