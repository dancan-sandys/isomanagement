import React, { useEffect, useRef, useState, useMemo } from 'react';
import { useParams } from 'react-router-dom';
import { useDispatch, useSelector } from 'react-redux';
import { Box, Grid, Typography, Chip, Tabs, Tab, Button, Stack, Table, TableBody, TableCell, TableContainer, TableHead, TableRow, Paper, Dialog, DialogTitle, DialogContent, DialogActions, TextField, IconButton, FormControl, InputLabel, Select, MenuItem, Tooltip, FormControlLabel, Switch, Badge, Radio, RadioGroup, Alert, CircularProgress } from '@mui/material';
import { Add, Edit, Visibility, Delete, Security, Save } from '@mui/icons-material';
import { Autocomplete } from '@mui/material';
import { traceabilityAPI, usersAPI, haccpAPI } from '../services/api';
import { hasRole } from '../store/slices/authSlice';
import HACCPFlowchartBuilder from '../components/HACCP/FlowchartBuilder';
import HazardDialog from '../components/HACCP/HazardDialog';
import HazardViewDialog from '../components/HACCP/HazardViewDialog';
import { AppDispatch, RootState } from '../store';
import { hasPermission, isSystemAdministrator } from '../store/slices/authSlice';
import { fetchProduct, createProcessFlow, updateProcessFlow, deleteProcessFlow, createHazard, updateHazard, deleteHazard, createCCP, updateCCP, createOPRP, updateOPRP, updateProduct } from '../store/slices/haccpSlice';

function TabPanel({ children, value, index }: { children?: React.ReactNode; value: number; index: number }) {
  return (
    <div role="tabpanel" hidden={value !== index}>
      {value === index && <Box sx={{ py: 3 }}>{children}</Box>}
    </div>
  );
}

const PRIVILEGED_ROLE_NAMES = [
  'System Administrator',
  'QA Manager',
  'QA Specialist',
  'Production Manager',
  'Compliance Officer',
] as const;

function formatDateTime(value: string | number | Date | null | undefined): string {
  if (value == null) return '—';
  const d = typeof value === 'string' || typeof value === 'number' ? new Date(value) : value;
  return isNaN(d.getTime()) ? String(value) : d.toLocaleString();
}

const HACCPProductDetail: React.FC = () => {
  const { id } = useParams();
  const productId = Number(id);
  const dispatch = useDispatch<AppDispatch>();
  const { selectedProduct, processFlows, hazards, ccps, oprps, loading, error } = useSelector((s: RootState) => s.haccp);
  const productIdValid = Number.isFinite(productId) && productId >= 1;
  const currentUser = useSelector((s: RootState) => s.auth.user);
  const canManageProgram = !!currentUser && (hasPermission(currentUser, 'haccp', 'manage_program') || isSystemAdministrator(currentUser));
  const canCreateLogs = !!currentUser && hasPermission(currentUser, 'haccp', 'create');
  const canCreateVerificationLogs = !!currentUser && hasPermission(currentUser, 'haccp', 'verify');
  
  // Check if current user is assigned as monitoring_responsible or verification_responsible for any CCPs
  const currentUserId = currentUser?.id;
  const isMonitoringResponsible = useMemo(() => {
    return !!currentUserId && ccps && ccps.length > 0 && ccps.some((ccp: any) => ccp.monitoring_responsible === currentUserId);
  }, [currentUserId, ccps]);
  
  const isVerificationResponsible = useMemo(() => {
    return !!currentUserId && ccps && ccps.length > 0 && ccps.some((ccp: any) => ccp.verification_responsible === currentUserId);
  }, [currentUserId, ccps]);
  
  const monitoringEligibleCCPs = useMemo(() => {
    return isMonitoringResponsible 
      ? ccps.filter((ccp: any) => ccp.monitoring_responsible === currentUserId)
      : [];
  }, [isMonitoringResponsible, ccps, currentUserId]);
  
  const verificationEligibleCCPs = useMemo(() => {
    return isVerificationResponsible 
      ? ccps.filter((ccp: any) => ccp.verification_responsible === currentUserId)
      : [];
  }, [isVerificationResponsible, ccps, currentUserId]);

  const [rejectedLogsCount, setRejectedLogsCount] = useState(0);
  const visibleTabs = useMemo((): { label: string; logicalIndex: number; badge?: number }[] => {
    const base: { label: string; logicalIndex: number; badge?: number }[] = [
      { label: 'Process Flow', logicalIndex: 0 },
      { label: 'Hazards', logicalIndex: 1 },
      { label: 'CCPs', logicalIndex: 2 },
      { label: 'OPRPs', logicalIndex: 3 },
    ];
    if (isMonitoringResponsible || isVerificationResponsible || canCreateVerificationLogs) base.push({ label: 'Monitoring', logicalIndex: 4 });
    if (isMonitoringResponsible) base.push({ label: 'Rejected', logicalIndex: 5, badge: rejectedLogsCount });
    if (isVerificationResponsible) base.push({ label: 'Verification', logicalIndex: 6 });
    base.push({ label: 'Risk Configuration', logicalIndex: 7 });
    return base;
  }, [isMonitoringResponsible, isVerificationResponsible, canCreateVerificationLogs, rejectedLogsCount]);

  const [selectedTab, setSelectedTab] = useState(0);
  const selectedLogicalIndex = visibleTabs[selectedTab]?.logicalIndex ?? 0;
  const [processFlowDialogOpen, setProcessFlowDialogOpen] = useState(false);
  const [hazardDialogOpen, setHazardDialogOpen] = useState(false);
  const [hazardViewDialogOpen, setHazardViewDialogOpen] = useState(false);
  const [ccpDialogOpen, setCcpDialogOpen] = useState(false);
  const [selectedFlow, setSelectedFlow] = useState<any>(null);
  const [selectedHazardItem, setSelectedHazardItem] = useState<any>(null);
  const [selectedCcpItem, setSelectedCcpItem] = useState<any>(null);
  const [selectedOprpItem, setSelectedOprpItem] = useState<any>(null);
  const [oprpDetailDialogOpen, setOprpDetailDialogOpen] = useState(false);
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
  const [oprpVerificationUserValue, setOprpVerificationUserValue] = useState<{ id: number; username: string; full_name?: string } | null>(null);
  const [oprpForm, setOprpForm] = useState({ verification_frequency: '', verification_method: '', verification_responsible: '' });
  const [oprpVerificationLogs, setOprpVerificationLogs] = useState<any[]>([]);
  const [oprpVerificationBatchValue, setOprpVerificationBatchValue] = useState<{ id: number; batch_number?: string } | null>(null);
  const [oprpVerificationNotes, setOprpVerificationNotes] = useState('');
  const [oprpVerificationConductedAsExpected, setOprpVerificationConductedAsExpected] = useState<boolean>(true);
  
  useEffect(() => {
    if (!productIdValid) return;
    dispatch(fetchProduct(productId));
  }, [dispatch, productId, productIdValid]);

  // Clamp selectedTab when visible tabs shrink (e.g. user no longer has Monitoring/Verification access)
  useEffect(() => {
    if (selectedTab >= visibleTabs.length) {
      setSelectedTab(Math.max(0, visibleTabs.length - 1));
    }
  }, [visibleTabs.length, selectedTab]);

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
        const monId = ccpForm.monitoring_responsible ? Number(ccpForm.monitoring_responsible) : NaN;
        if (Number.isFinite(monId) && monId >= 1 && (!monitoringUserValue || monitoringUserValue.id !== monId)) {
          if (currentUser?.id === monId) {
            setMonitoringUserValue({ id: currentUser.id, username: currentUser.username ?? '', full_name: currentUser.full_name ?? '' });
          } else {
            const res: any = await usersAPI.getUser(monId);
            const u = res?.data || res;
            if (u?.id) setMonitoringUserValue({ id: u.id, username: u.username, full_name: u.full_name });
          }
        } else if (!ccpForm.monitoring_responsible || !Number.isFinite(monId)) setMonitoringUserValue(null);
        const verId = ccpForm.verification_responsible ? Number(ccpForm.verification_responsible) : NaN;
        if (Number.isFinite(verId) && verId >= 1 && (!verificationUserValue || verificationUserValue.id !== verId)) {
          if (currentUser?.id === verId) {
            setVerificationUserValue({ id: currentUser.id, username: currentUser.username ?? '', full_name: currentUser.full_name ?? '' });
          } else {
            const res: any = await usersAPI.getUser(verId);
            const u = res?.data || res;
            if (u?.id) setVerificationUserValue({ id: u.id, username: u.username, full_name: u.full_name });
          }
        } else if (!ccpForm.verification_responsible || !Number.isFinite(verId)) setVerificationUserValue(null);
      } catch {}
    };
    populateSelectedUsers();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [ccpForm.monitoring_responsible, ccpForm.verification_responsible, currentUser?.id]);

  // When OPRP detail is opened, fetch full OPRP and verification logs; populate OPRP form and verifier user
  useEffect(() => {
    if (!selectedOprpItem?.id || !oprpDetailDialogOpen) return;
    const oprpId = selectedOprpItem.id;
    setOprpForm({
      verification_frequency: selectedOprpItem.verification_frequency ?? '',
      verification_method: selectedOprpItem.verification_method ?? '',
      verification_responsible: selectedOprpItem.verification_responsible != null ? String(selectedOprpItem.verification_responsible) : '',
    });
    (async () => {
      try {
        const res: any = await haccpAPI.getOPRP(oprpId);
        const data = res?.data ?? res;
        const verId = data?.verification_responsible != null ? Number(data.verification_responsible) : NaN;
        if (Number.isFinite(verId) && verId >= 1) {
          if (currentUser?.id === verId) {
            setOprpVerificationUserValue({ id: currentUser.id, username: currentUser.username ?? '', full_name: currentUser.full_name ?? '' });
          } else {
            const u: any = await usersAPI.getUser(verId);
            const user = u?.data ?? u;
            if (user?.id) setOprpVerificationUserValue({ id: user.id, username: user.username, full_name: user.full_name });
          }
        } else {
          setOprpVerificationUserValue(null);
        }
        const logsRes: any = await haccpAPI.getOPRPVerificationLogs(oprpId);
        const logs = logsRes?.data ?? logsRes;
        setOprpVerificationLogs(Array.isArray(logs) ? logs : []);
      } catch {
        setOprpVerificationLogs([]);
        setOprpVerificationUserValue(null);
      }
    })();
  }, [selectedOprpItem?.id, oprpDetailDialogOpen, currentUser?.id]);

  useEffect(() => {
    const raw = oprpForm.verification_responsible;
    const idNum = raw !== '' && raw != null ? Number(raw) : NaN;
    if (Number.isFinite(idNum) && idNum >= 1 && (!oprpVerificationUserValue || idNum !== oprpVerificationUserValue.id)) {
      if (currentUser?.id === idNum) {
        setOprpVerificationUserValue({ id: currentUser.id, username: currentUser.username ?? '', full_name: currentUser.full_name ?? '' });
      } else {
        usersAPI.getUser(idNum).then((res: any) => {
          const u = res?.data ?? res;
          if (u?.id) setOprpVerificationUserValue({ id: u.id, username: u.username, full_name: u.full_name });
        }).catch(() => setOprpVerificationUserValue(null));
      }
    } else if (!raw || !Number.isFinite(idNum)) setOprpVerificationUserValue(null);
  }, [oprpForm.verification_responsible, currentUser?.id, currentUser?.username, currentUser?.full_name]);

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

  const handleTabChange = (_e: any, visualIndex: number) => {
    // visualIndex is the index into visibleTabs; TabPanels use logicalIndex (0–6)
    setSelectedTab(visualIndex);
  };

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

  const handleSaveOPRPDetail = async () => {
    if (!selectedOprpItem?.id) return;
    const verId = oprpForm.verification_responsible !== '' ? Number(oprpForm.verification_responsible) : NaN;
    const payload = {
      verification_frequency: oprpForm.verification_frequency || undefined,
      verification_method: oprpForm.verification_method || undefined,
      verification_responsible: Number.isFinite(verId) && verId >= 1 ? verId : null,
    };
    try {
      await dispatch(updateOPRP({ oprpId: selectedOprpItem.id, oprpData: payload })).unwrap();
      dispatch(fetchProduct(productId));
      setSelectedOprpItem((prev: any) => prev ? { ...prev, ...payload } : null);
      alert('OPRP updated.');
    } catch (e: any) {
      alert(e?.response?.data?.detail || 'Failed to update OPRP');
    }
  };

  const handleConfirmOPRPVerification = async () => {
    if (!selectedOprpItem?.id) return;
    try {
      await haccpAPI.createOPRPVerificationLog(selectedOprpItem.id, {
        batch_id: oprpVerificationBatchValue?.id,
        verification_type: 'batch_check',
        conducted_as_expected: oprpVerificationConductedAsExpected,
        findings: oprpVerificationNotes.trim() || undefined,
      });
      const res: any = await haccpAPI.getOPRPVerificationLogs(selectedOprpItem.id);
      setOprpVerificationLogs(Array.isArray(res?.data) ? res.data : (Array.isArray(res) ? res : []));
      setOprpVerificationNotes('');
      setOprpVerificationBatchValue(null);
      setOprpVerificationConductedAsExpected(true);
      alert('Verification recorded.');
    } catch (e: any) {
      alert(e?.response?.data?.detail || 'Failed to record verification');
    }
  };

  const [monitoringForm, setMonitoringForm] = useState<{ ccp_id?: string; batch?: string; batch_id?: string; value?: string; unit?: string; evidence_files?: string }>({});
  const [monitoringLogs, setMonitoringLogs] = useState<any[]>([]);
  const [monitoringLogsTab, setMonitoringLogsTab] = useState(0);
  const [verificationDialogOpen, setVerificationDialogOpen] = useState(false);
  const [selectedMonitoringLog, setSelectedMonitoringLog] = useState<any | null>(null);
  const [verificationForm, setVerificationForm] = useState<{
    verification_notes: string;
    allowOverride: boolean;
  }>({
    verification_notes: '',
    allowOverride: false,
  });
  const [batchOptions, setBatchOptions] = useState<any[]>([]);
  const [batchSearch, setBatchSearch] = useState('');
  const [batchOpen, setBatchOpen] = useState(false);

  const [verificationTabCcpId, setVerificationTabCcpId] = useState<string>('');
  const [verificationTabMonitoringLogs, setVerificationTabMonitoringLogs] = useState<any[]>([]);
  const [rejectedLogs, setRejectedLogs] = useState<any[]>([]);
  const [resolveDialogOpen, setResolveDialogOpen] = useState(false);
  const [selectedLogForResolve, setSelectedLogForResolve] = useState<any | null>(null);
  const [resolveForm, setResolveForm] = useState<{ new_value: string; unit: string; batch_number: string }>({ new_value: '', unit: '', batch_number: '' });

  const handleResolveRejected = async () => {
    const log = selectedLogForResolve;
    if (!log?.id || !log?.ccp_id) return;
    const num = Number(resolveForm.new_value);
    if (isNaN(num)) {
      alert('Enter a valid number for the new value');
      return;
    }
    try {
      await haccpAPI.resolveRejectedMonitoringLog(Number(log.ccp_id), log.id, {
        new_value: num,
        unit: resolveForm.unit.trim() || undefined,
        batch_number: resolveForm.batch_number.trim() || undefined,
      });
      setResolveDialogOpen(false);
      setSelectedLogForResolve(null);
      setResolveForm({ new_value: '', unit: '', batch_number: '' });
      const api = (await import('../services/api')).api;
      const resp = await api.get(`/haccp/ccps/${Number(log.ccp_id)}/monitoring-logs`);
      const logsJson = resp.data;
      const raw = logsJson?.data ?? logsJson;
      const items = Array.isArray(raw?.items) ? raw.items : (Array.isArray(raw) ? raw : logsJson?.items ?? []);
      setMonitoringLogs(items);
      if (String(log.ccp_id) === verificationTabCcpId) setVerificationTabMonitoringLogs(items);
      fetchRejectedLogs();
      alert('Log resolved. The new value has been saved and is pending re-verification.');
    } catch (e: any) {
      console.error('Resolve failed', e);
      alert(e?.response?.data?.detail || 'Failed to resolve');
    }
  };

  // Fetch batches when autocomplete opens or search text changes (scoped to current product)
  useEffect(() => {
    let active = true;
    if (!batchOpen) return () => { active = false; };
    const t = setTimeout(async () => {
      try {
        const params: any = { search: batchSearch, size: 10 };
        if (productId && Number.isInteger(productId)) params.product_id = productId;
        const resp: any = await traceabilityAPI.getBatches(params);
        const items = resp?.data?.items || resp?.items || [];
        if (active) {
          setBatchOptions(items);
        }
      } catch (e) {
        if (active) {
          setBatchOptions([]);
        }
      }
    }, 250);
    return () => { active = false; clearTimeout(t); };
  }, [batchOpen, batchSearch, productId]);

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
        const raw = logsJson?.data ?? logsJson;
        const items = Array.isArray(raw?.items) ? raw.items : (Array.isArray(raw) ? raw : logsJson?.items ?? []);
        if (active) setMonitoringLogs(items);
      } catch {
        if (active) setMonitoringLogs([]);
      }
    };
    fetchLogs();
    return () => { active = false; };
  }, [monitoringForm.ccp_id]);

  // Fetch monitoring logs for Verification tab when CCP is selected
  useEffect(() => {
    let active = true;
    const ccpIdStr = verificationTabCcpId || '';
    if (!ccpIdStr) { setVerificationTabMonitoringLogs([]); return () => { active = false; }; }
    (async () => {
      try {
        const api = (await import('../services/api')).api;
        const resp = await api.get(`/haccp/ccps/${Number(ccpIdStr)}/monitoring-logs`);
        if (!active) return;
        const logsJson = resp.data;
        const raw = logsJson?.data ?? logsJson;
        const items = Array.isArray(raw?.items) ? raw.items : (Array.isArray(raw) ? raw : logsJson?.items ?? []);
        setVerificationTabMonitoringLogs(items);
      } catch {
        if (active) setVerificationTabMonitoringLogs([]);
      }
    })();
    return () => { active = false; };
  }, [verificationTabCcpId]);

  const isLogRejected = (log: any) =>
    !!log?.is_verified && (log.verification_is_compliant === false || log.verification_result === 'Rejected');

  const fetchRejectedLogs = async () => {
    if (!isMonitoringResponsible) return;
    try {
      const res = await haccpAPI.getRejectedMonitoringLogs();
      const payload = res?.data ?? res;
      const items = payload?.items ?? [];
      setRejectedLogs(items);
      setRejectedLogsCount(payload?.total ?? items.length);
    } catch {
      setRejectedLogs([]);
      setRejectedLogsCount(0);
    }
  };

  useEffect(() => {
    fetchRejectedLogs();
  }, [isMonitoringResponsible, productId]);

  const handleCloseVerificationDialog = () => {
    setVerificationDialogOpen(false);
    setSelectedMonitoringLog(null);
    setVerificationForm({ verification_notes: '', allowOverride: false });
  };

  const submitVerificationAction = async (compliant: boolean) => {
    const log = selectedMonitoringLog;
    const ccpId = log?.ccp_id != null ? Number(log.ccp_id) : (monitoringForm.ccp_id ? Number(monitoringForm.ccp_id) : verificationTabCcpId ? Number(verificationTabCcpId) : null);
    if (!log?.id || ccpId == null) {
      alert('Missing log or CCP. Please close and try again from the monitoring logs table.');
      return;
    }
    try {
      await haccpAPI.verifyMonitoringLog(
        ccpId,
        log.id,
        {
          verification_is_compliant: compliant,
          verification_notes: verificationForm.verification_notes.trim() || undefined,
        },
        { allowOverride: verificationForm.allowOverride }
      );
      handleCloseVerificationDialog();
      const api = (await import('../services/api')).api;
      const resp = await api.get(`/haccp/ccps/${ccpId}/monitoring-logs`);
      const logsJson = resp.data;
      const raw = logsJson?.data ?? logsJson;
      const items = Array.isArray(raw?.items) ? raw.items : (Array.isArray(raw) ? raw : logsJson?.items ?? []);
      setMonitoringLogs(items);
      if (String(ccpId) === verificationTabCcpId) setVerificationTabMonitoringLogs(items);
      if (!compliant) fetchRejectedLogs();
      alert(compliant ? 'Log entry verified successfully.' : 'Log entry rejected.');
    } catch (e: any) {
      console.error('Verification action failed', e);
      alert(e?.response?.data?.detail || 'Failed to submit verification');
    }
  };

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

      {!productIdValid && (
        <Alert severity="error" sx={{ mb: 2 }}>Invalid product link.</Alert>
      )}
      {productIdValid && !selectedProduct && (loading || !error) && (
        <Box sx={{ display: 'flex', justifyContent: 'center', py: 6 }}>
          <CircularProgress />
        </Box>
      )}
      {productIdValid && !selectedProduct && !loading && error && (
        <Alert severity="error" sx={{ mb: 2 }}>{typeof error === 'string' ? error : 'Failed to load product.'}</Alert>
      )}

      {selectedProduct ? (
        <>
      <Tabs value={selectedTab} onChange={handleTabChange}>
        {visibleTabs.map((t, i) => (
          <Tab
            key={t.logicalIndex}
            label={typeof t.badge === 'number' && t.badge > 0 ? (
              <Badge badgeContent={t.badge} color="error">{t.label}</Badge>
            ) : t.label}
          />
        ))}
      </Tabs>

      <TabPanel value={selectedLogicalIndex} index={0}>
        <Box sx={{ mb: 2, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <Typography variant="h6">Process Flow</Typography>
          {canManageProgram && (
            <Box sx={{ display: 'flex', gap: 1 }}>
              <Button variant="outlined" onClick={() => setFlowchartDialogOpen(true)}>Open Flowchart Builder</Button>
              <Button variant="contained" startIcon={<Add />} onClick={() => { setSelectedFlow(null); setProcessFlowDialogOpen(true); }}>Add Step</Button>
            </Box>
          )}
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
                    {canManageProgram && (
                      <Stack direction="row" spacing={1}>
                        <IconButton size="small" onClick={() => { setSelectedFlow(flow); setProcessFlowDialogOpen(true); }}><Edit /></IconButton>
                        <IconButton size="small" onClick={() => { if (window.confirm('Delete this process step?')) dispatch(deleteProcessFlow(flow.id)).then(() => dispatch(fetchProduct(productId))); }}><Delete /></IconButton>
                      </Stack>
                    )}
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </TableContainer>
      </TabPanel>

      <TabPanel value={selectedLogicalIndex} index={1}>
        <Box sx={{ mb: 2, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <Typography variant="h6">Hazards</Typography>
          {canManageProgram && (
            <Button variant="contained" startIcon={<Add />} onClick={() => { setSelectedHazardItem(null); setHazardDialogOpen(true); }}>Add Hazard</Button>
          )}
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
                {canManageProgram && (
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
                )}
              </Paper>
            </Grid>
          ))}
        </Grid>
      </TabPanel>

      <TabPanel value={selectedLogicalIndex} index={2}>
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
                  {canManageProgram && (
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
                  )}
                </Paper>
              </Grid>
            );
          })}
        </Grid>
      </TabPanel>

      <TabPanel value={selectedLogicalIndex} index={3}>
        <Box sx={{ mb: 2, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <Typography variant="h6">Operational Prerequisite Programs (OPRPs)</Typography>
        </Box>
        <Grid container spacing={2}>
          {oprps.map((oprp: any) => (
            <Grid item xs={12} sm={6} md={4} key={oprp.id}>
              <Paper
                sx={{
                  p: 2,
                  cursor: 'pointer',
                  '&:hover': { bgcolor: 'action.hover' },
                }}
                onClick={() => {
                  setSelectedOprpItem(oprp);
                  setOprpDetailDialogOpen(true);
                }}
              >
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
                  <Chip
                    label={oprp.verification_responsible ? 'Verifier assigned' : 'Verifier not assigned'}
                    color={oprp.verification_responsible ? 'primary' : 'default'}
                    size="small"
                    variant="outlined"
                  />
                  {oprp.verification_frequency && (
                    <Chip
                      label={`Verify: ${oprp.verification_frequency}`}
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
                      {typeof oprp.operational_limits === 'string' ? oprp.operational_limits : JSON.stringify(oprp.operational_limits)}
                    </Typography>
                  </Box>
                )}
                <Typography variant="caption" color="text.secondary" sx={{ mt: 1, display: 'block' }}>
                  Tap to view details and assign verifier
                </Typography>
              </Paper>
            </Grid>
          ))}
        </Grid>
      </TabPanel>

      <TabPanel value={selectedLogicalIndex} index={4}>
          <Typography variant="h6" gutterBottom>Monitoring & Verification</Typography>
          <Stack spacing={2} sx={{ maxWidth: 700, mt: 1 }}>
            <Autocomplete options={monitoringEligibleCCPs} getOptionLabel={(ccp: any) => `${ccp.ccp_number || ''} - ${ccp.ccp_name || ''}`.trim()} value={monitoringEligibleCCPs.find((c: any) => String(c.id) === (monitoringForm.ccp_id || '')) || null} onChange={(_, val: any) => setMonitoringForm({ ...monitoringForm, ccp_id: val ? String(val.id) : '' })} isOptionEqualToValue={(opt: any, val: any) => opt.id === val.id} renderInput={(params) => <TextField {...params} label="Select CCP" placeholder="Choose CCP for monitoring" />} />
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
            <Tooltip title={(!canCreateLogs && !isMonitoringResponsible) ? 'You need haccp:create permission or to be assigned as monitoring responsible to record monitoring logs' : ''}>
              <span>
                <Button 
                  variant="contained" 
                  startIcon={<Save />}
                  disabled={(!canCreateLogs && !isMonitoringResponsible) || !monitoringForm.ccp_id || !monitoringForm.value || (monitoringForm.value && isNaN(Number(monitoringForm.value)))} 
                  onClick={async () => {
                    // Allow if user has permission OR is assigned as monitoring responsible
                    if (!canCreateLogs && !isMonitoringResponsible) return;
                    const ccpId = Number(monitoringForm.ccp_id);
                    try {
                      const requestBody: any = {};
                      if (monitoringForm.batch_id) requestBody.batch_id = Number(monitoringForm.batch_id);
                      if (monitoringForm.batch) requestBody.batch_number = monitoringForm.batch;
                      if (monitoringForm.value && !isNaN(Number(monitoringForm.value))) {
                        requestBody.measured_value = Number(monitoringForm.value);
                      } else {
                        alert('Please enter a valid measured value');
                        return;
                      }
                      if (monitoringForm.unit) requestBody.unit = monitoringForm.unit;
                      if (monitoringForm.evidence_files) requestBody.evidence_files = monitoringForm.evidence_files;
                      const api = (await import('../services/api')).api;
                      await api.post(`/haccp/ccps/${ccpId}/monitoring-logs/enhanced`, requestBody);
                      try {
                        const resp = await api.get(`/haccp/ccps/${ccpId}/monitoring-logs`);
                        const logsJson = resp.data;
                        const items = logsJson?.data?.items || logsJson?.items || [];
                        setMonitoringLogs(items);
                      } catch {}
                      if (monitoringForm.batch) {
                        const res = await api.get(`/nonconformance/haccp/recent-nc?ccp_id=${ccpId}&batch_number=${encodeURIComponent(monitoringForm.batch)}`);
                        const data = res.data;
                        if (data?.found) window.open(`/nonconformance/${data.id}`, '_blank');
                      }
                      // Clear form after successful save
                      setMonitoringForm({ ...monitoringForm, value: '', unit: '', batch: '', batch_id: '', evidence_files: undefined });
                    } catch (error) {
                      console.error('Failed to create monitoring log:', error);
                      alert('Failed to create monitoring log');
                    }
                  }}
                >
                  Save monitoring log
                </Button>
              </span>
            </Tooltip>
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
                    {monitoringLogs.map((log: any) => {
                      const rejected = isLogRejected(log);
                      return (
                        <TableRow key={log.id}>
                          <TableCell>{log.monitoring_time || log.created_at}</TableCell>
                          <TableCell>{log.batch_number ?? log.batch ?? '—'}</TableCell>
                          <TableCell align="right">{log.measured_value ?? log.value ?? '—'}</TableCell>
                          <TableCell>{log.unit ?? '—'}</TableCell>
                          <TableCell>
                            {rejected ? (
                              <Chip size="small" color="error" label="REJECTED" />
                            ) : (
                              <Chip size="small" color={log.is_within_limits ? 'success' : 'error'} label={log.is_within_limits ? 'In Spec' : 'Out of Spec'} />
                            )}
                          </TableCell>
                          <TableCell>
                            <Stack direction="row" spacing={1} flexWrap="wrap">
                              {rejected && isMonitoringResponsible && (
                                <Button size="small" color="warning" variant="contained" onClick={() => { setSelectedLogForResolve(log); setResolveForm({ new_value: String(log.measured_value ?? log.value ?? ''), unit: log.unit ?? '', batch_number: log.batch_number ?? log.batch ?? '' }); setResolveDialogOpen(true); }}>
                                  Resolve
                                </Button>
                              )}
                              {!rejected && (canCreateVerificationLogs || isVerificationResponsible) && (
                                <Button size="small" variant={log.is_verified ? 'outlined' : 'contained'} onClick={() => { setSelectedMonitoringLog(log); setVerificationDialogOpen(true); }}>
                                  {log.is_verified ? 'View / Re-verify' : 'Verify'}
                                </Button>
                              )}
                              <Button size="small" onClick={async () => {
                                const ccpId = Number(monitoringForm.ccp_id);
                                const api = (await import('../services/api')).api;
                                const res = await api.get(`/nonconformance/haccp/recent-nc?ccp_id=${ccpId}&batch_number=${encodeURIComponent(log.batch_number || log.batch || '')}`);
                                const data = res.data;
                                if (data?.found) window.open(`/nonconformance/${data.id}`, '_blank');
                                else alert('No NC linked for this reading');
                              }}>Open NC</Button>
                            </Stack>
                          </TableCell>
                        </TableRow>
                      );
                    })}
                  </TableBody>
                </Table>
              </TableContainer>
            </Box>
          )}
          </Stack>
        </TabPanel>

      <TabPanel value={selectedLogicalIndex} index={5}>
          <Typography variant="h6" gutterBottom>Rejected logs</Typography>
          <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
            Logs rejected by verification. Resolve by entering a new value.
          </Typography>
          <TableContainer component={Paper} variant="outlined">
            <Table size="small">
              <TableHead>
                <TableRow>
                  <TableCell>CCP</TableCell>
                  <TableCell>Product</TableCell>
                  <TableCell>Batch</TableCell>
                  <TableCell align="right">Value</TableCell>
                  <TableCell>Unit</TableCell>
                  <TableCell>Rejected at</TableCell>
                  <TableCell>Actions</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {rejectedLogs.length === 0 ? (
                  <TableRow><TableCell colSpan={7} align="center"><Typography variant="body2" color="text.secondary">No rejected logs.</Typography></TableCell></TableRow>
                ) : (
                  rejectedLogs.map((log: any) => (
                    <TableRow key={log.id}>
                      <TableCell>{log.ccp_number} – {log.ccp_name}</TableCell>
                      <TableCell>{log.product_name ?? '—'}</TableCell>
                      <TableCell>{log.batch_number ?? '—'}</TableCell>
                      <TableCell align="right">{log.measured_value ?? '—'}</TableCell>
                      <TableCell>{log.unit ?? '—'}</TableCell>
                      <TableCell>{log.verified_at ? new Date(log.verified_at).toLocaleString() : '—'}</TableCell>
                      <TableCell>
                        <Button size="small" color="warning" variant="contained" onClick={() => { setSelectedLogForResolve(log); setResolveForm({ new_value: String(log.measured_value ?? ''), unit: log.unit ?? '', batch_number: log.batch_number ?? '' }); setResolveDialogOpen(true); }}>
                          Resolve
                        </Button>
                      </TableCell>
                    </TableRow>
                  ))
                )}
              </TableBody>
            </Table>
          </TableContainer>
        </TabPanel>

      <TabPanel value={selectedLogicalIndex} index={6}>
          <Typography variant="h6" gutterBottom>Verify or Reject Monitoring Logs</Typography>
          <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
            Select a CCP to view its monitoring logs. Use Verify or Reject on each log; no form to fill.
          </Typography>
          <Stack spacing={2} sx={{ maxWidth: 700, mt: 1 }}>
            <Autocomplete
              options={verificationEligibleCCPs}
              getOptionLabel={(ccp: any) => `${ccp.ccp_number || ''} - ${ccp.ccp_name || ''}`.trim()}
              value={verificationEligibleCCPs.find((c: any) => String(c.id) === verificationTabCcpId) || null}
              onChange={(_, val: any) => setVerificationTabCcpId(val ? String(val.id) : '')}
              isOptionEqualToValue={(opt: any, val: any) => opt.id === val.id}
              renderInput={(params) => <TextField {...params} label="Select CCP" placeholder="Choose CCP" />}
            />
          </Stack>
          {verificationTabCcpId && (
            <Box sx={{ mt: 3 }}>
              <Typography variant="subtitle1" sx={{ mb: 1 }}>Monitoring logs</Typography>
              <TableContainer component={Paper} variant="outlined">
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
                    {verificationTabMonitoringLogs.length === 0 ? (
                      <TableRow><TableCell colSpan={6} align="center"><Typography variant="body2" color="text.secondary">No monitoring logs for this CCP.</Typography></TableCell></TableRow>
                    ) : (
                      verificationTabMonitoringLogs.map((log: any) => {
                        const rejected = isLogRejected(log);
                        return (
                          <TableRow key={log.id}>
                            <TableCell>{log.monitoring_time || log.created_at}</TableCell>
                            <TableCell>{log.batch_number ?? log.batch ?? '—'}</TableCell>
                            <TableCell align="right">{log.measured_value ?? log.value ?? '—'}</TableCell>
                            <TableCell>{log.unit ?? '—'}</TableCell>
                            <TableCell>
                              {rejected ? <Chip size="small" color="error" label="REJECTED" /> : <Chip size="small" color={log.is_within_limits ? 'success' : 'error'} label={log.is_within_limits ? 'In Spec' : 'Out of Spec'} />}
                            </TableCell>
                            <TableCell>
                              <Stack direction="row" spacing={1} flexWrap="wrap">
                                {rejected && isMonitoringResponsible && (
                                  <Button size="small" color="warning" variant="contained" onClick={() => { setSelectedLogForResolve(log); setResolveForm({ new_value: String(log.measured_value ?? log.value ?? ''), unit: log.unit ?? '', batch_number: log.batch_number ?? log.batch ?? '' }); setResolveDialogOpen(true); }}>Resolve</Button>
                                )}
                                {!rejected && (canCreateVerificationLogs || isVerificationResponsible) && (
                                  <Button size="small" variant={log.is_verified ? 'outlined' : 'contained'} onClick={() => { setSelectedMonitoringLog(log); setVerificationDialogOpen(true); }}>
                                    {log.is_verified ? 'View / Re-verify' : 'Verify'}
                                  </Button>
                                )}
                                <Button size="small" onClick={async () => {
                                  const api = (await import('../services/api')).api;
                                  const res = await api.get(`/nonconformance/haccp/recent-nc?ccp_id=${Number(log.ccp_id)}&batch_number=${encodeURIComponent(log.batch_number || log.batch || '')}`);
                                  const data = res.data;
                                  if (data?.found) window.open(`/nonconformance/${data.id}`, '_blank');
                                  else alert('No NC linked for this reading');
                                }}>Open NC</Button>
                              </Stack>
                            </TableCell>
                          </TableRow>
                        );
                      })
                    )}
                  </TableBody>
                </Table>
              </TableContainer>
            </Box>
          )}
        </TabPanel>

      <TabPanel value={selectedLogicalIndex} index={7}>
        <Box sx={{ mb: 2, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <Typography variant="h6">Risk Configuration</Typography>
          {canManageProgram && (
            <Button variant="contained" onClick={() => setRiskConfigDialogOpen(true)}>
              {selectedProduct?.risk_config ? 'Edit Risk Config' : 'Configure Risk Settings'}
            </Button>
          )}
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
            <Typography color="textSecondary">No risk configuration set for this product.</Typography>
          </Paper>
        )}
      </TabPanel>
        </>
      ) : null}

      {/* Verification Dialog: verify or reject only (no form to fill) */}
      <Dialog open={verificationDialogOpen} onClose={handleCloseVerificationDialog} maxWidth="sm" fullWidth>
        <DialogTitle>
          {selectedMonitoringLog?.is_verified ? 'Verification Details' : 'Verify or Reject Monitoring Log'}
        </DialogTitle>
        <DialogContent dividers>
          <Stack spacing={2} sx={{ mt: 1 }}>
            <Box>
              <Typography variant="subtitle2" color="text.secondary">
                Monitoring Snapshot
              </Typography>
              <Typography variant="body2">
                {`${selectedMonitoringLog?.batch_number || 'Batch N/A'} • ${
                  selectedMonitoringLog?.measured_value ?? '-'
                } ${selectedMonitoringLog?.unit || ''}`}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                {`Recorded: ${formatDateTime(
                  selectedMonitoringLog?.monitoring_time || selectedMonitoringLog?.created_at
                )}`}
              </Typography>
              <Chip
                size="small"
                color={selectedMonitoringLog?.is_within_limits ? 'success' : 'error'}
                label={selectedMonitoringLog?.is_within_limits ? 'In Spec' : 'Out of Spec'}
                sx={{ mt: 1 }}
              />
              {selectedMonitoringLog?.is_verified && (
                <Box sx={{ mt: 1 }}>
                  <Chip
                    size="small"
                    color={selectedMonitoringLog?.verification_is_compliant !== false ? 'success' : 'error'}
                    label={selectedMonitoringLog?.verification_result || (selectedMonitoringLog?.verification_is_compliant !== false ? 'Verified' : 'Rejected')}
                  />
                  {selectedMonitoringLog?.verified_at && (
                    <Typography variant="caption" display="block" color="text.secondary">
                      {formatDateTime(selectedMonitoringLog.verified_at)}
                      {selectedMonitoringLog?.verified_by_name && ` by ${selectedMonitoringLog.verified_by_name}`}
                    </Typography>
                  )}
                </Box>
              )}
            </Box>

            {selectedMonitoringLog?.is_verified && (
              <FormControlLabel
                control={
                  <Switch
                    checked={verificationForm.allowOverride}
                    onChange={(e) =>
                      setVerificationForm((prev) => ({ ...prev, allowOverride: e.target.checked }))
                    }
                  />
                }
                label="Override existing verification"
              />
            )}

            {(!selectedMonitoringLog?.is_verified || verificationForm.allowOverride) && (
              <TextField
                label="Note (optional)"
                value={verificationForm.verification_notes}
                onChange={(e) =>
                  setVerificationForm((prev) => ({ ...prev, verification_notes: e.target.value }))
                }
                fullWidth
                multiline
                rows={2}
                placeholder="e.g. reason for rejection or brief comment"
              />
            )}
          </Stack>
        </DialogContent>
        <DialogActions>
          <Button onClick={handleCloseVerificationDialog}>Close</Button>
          {(!selectedMonitoringLog?.is_verified || verificationForm.allowOverride) && (
            <>
              <Button
                color="error"
                variant="outlined"
                onClick={() => submitVerificationAction(false)}
              >
                Reject
              </Button>
              <Button
                variant="contained"
                color="success"
                onClick={() => submitVerificationAction(true)}
              >
                Verify
              </Button>
            </>
          )}
        </DialogActions>
      </Dialog>

      {/* Resolve rejected log dialog */}
      <Dialog open={resolveDialogOpen} onClose={() => { setResolveDialogOpen(false); setSelectedLogForResolve(null); }} maxWidth="sm" fullWidth>
        <DialogTitle>Resolve rejected log</DialogTitle>
        <DialogContent dividers>
          <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
            Enter the new value for this record. The log will be updated and set back to pending verification.
          </Typography>
          {selectedLogForResolve && (
            <Stack spacing={2} sx={{ mt: 1 }}>
              <Typography variant="body2">CCP: {selectedLogForResolve.ccp_number ?? selectedLogForResolve.ccp_name ?? selectedLogForResolve.ccp_id} – {selectedLogForResolve.ccp_name ?? '—'}</Typography>
              <TextField
                label="New value (required)"
                type="number"
                value={resolveForm.new_value}
                onChange={(e) => setResolveForm((prev) => ({ ...prev, new_value: e.target.value }))}
                fullWidth
                required
                inputProps={{ step: 'any' }}
              />
              <TextField label="Unit" value={resolveForm.unit} onChange={(e) => setResolveForm((prev) => ({ ...prev, unit: e.target.value }))} fullWidth />
              <TextField label="Batch number" value={resolveForm.batch_number} onChange={(e) => setResolveForm((prev) => ({ ...prev, batch_number: e.target.value }))} fullWidth />
            </Stack>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => { setResolveDialogOpen(false); setSelectedLogForResolve(null); }}>Cancel</Button>
          <Button variant="contained" color="warning" onClick={handleResolveRejected}>Resolve</Button>
        </DialogActions>
      </Dialog>

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

      {/* OPRP Detail Dialog – verification only (no monitoring); admin can assign verification person */}
      <Dialog open={oprpDetailDialogOpen} onClose={() => { setOprpDetailDialogOpen(false); setSelectedOprpItem(null); setOprpVerificationNotes(''); setOprpVerificationBatchValue(null); }} maxWidth="md" fullWidth>
        <DialogTitle>OPRP: {selectedOprpItem?.oprp_name ?? selectedOprpItem?.oprp_number ?? 'Details'}</DialogTitle>
        <DialogContent dividers>
          {selectedOprpItem && (
            <Stack spacing={2} sx={{ mt: 1 }}>
              <Typography variant="body2" color="text.secondary">{selectedOprpItem.oprp_number} · {selectedOprpItem.description}</Typography>
              {selectedOprpItem.justification && (
                <Box>
                  <Typography variant="subtitle2">Justification</Typography>
                  <Typography variant="body2">{selectedOprpItem.justification}</Typography>
                </Box>
              )}
              {(selectedOprpItem.operational_limits != null || selectedOprpItem.operational_limit_description) && (
                <Box>
                  <Typography variant="subtitle2">Operational limits</Typography>
                  <Typography variant="body2">
                    {selectedOprpItem.operational_limits != null
                      ? (typeof selectedOprpItem.operational_limits === 'string' ? selectedOprpItem.operational_limits : JSON.stringify(selectedOprpItem.operational_limits))
                      : selectedOprpItem.operational_limit_description ?? '—'}
                  </Typography>
                </Box>
              )}
              <Typography variant="subtitle1">Verification (no monitoring for OPRPs)</Typography>
              {canManageProgram && (
                <Grid container spacing={2}>
                  <Grid item xs={12} md={6}>
                    <TextField
                      fullWidth
                      label="Verification frequency"
                      value={oprpForm.verification_frequency}
                      onChange={(e) => setOprpForm((f) => ({ ...f, verification_frequency: e.target.value }))}
                    />
                  </Grid>
                  <Grid item xs={12} md={6}>
                    <TextField
                      fullWidth
                      label="Verification method"
                      value={oprpForm.verification_method}
                      onChange={(e) => setOprpForm((f) => ({ ...f, verification_method: e.target.value }))}
                    />
                  </Grid>
                  <Grid item xs={12}>
                    <Autocomplete
                      options={userOptions}
                      getOptionLabel={(opt) => (opt.full_name ? `${opt.full_name} (${opt.username})` : opt.username)}
                      value={oprpVerificationUserValue}
                      onChange={(_, val) => {
                        setOprpVerificationUserValue(val);
                        setOprpForm((f) => ({ ...f, verification_responsible: val ? String(val.id) : '' }));
                      }}
                      onInputChange={(_, val) => setUserSearch(val)}
                      onOpen={() => setUserOpen(true)}
                      onClose={() => setUserOpen(false)}
                      loading={userLoading}
                      isOptionEqualToValue={(opt, val) => opt.id === val.id}
                      renderInput={(params) => <TextField {...params} label="Verification responsible" placeholder="Assign verifier" fullWidth />}
                    />
                  </Grid>
                  <Grid item xs={12}>
                    <Button variant="contained" onClick={handleSaveOPRPDetail}>Save assignment</Button>
                  </Grid>
                </Grid>
              )}
              {!canManageProgram && (
                <Typography variant="body2">
                  Frequency: {selectedOprpItem.verification_frequency || '—'} · Method: {selectedOprpItem.verification_method || '—'}
                  {oprpVerificationUserValue && ` · Verifier: ${oprpVerificationUserValue.full_name || oprpVerificationUserValue.username}`}
                </Typography>
              )}
              <Typography variant="subtitle2">Verification records (per batch)</Typography>
              <TableContainer component={Paper} variant="outlined">
                <Table size="small">
                  <TableHead>
                    <TableRow>
                      <TableCell>Batch</TableCell>
                      <TableCell>Date</TableCell>
                      <TableCell>Verified by</TableCell>
                      <TableCell>Result</TableCell>
                      <TableCell>Findings</TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {oprpVerificationLogs.length === 0 ? (
                      <TableRow><TableCell colSpan={5} align="center"><Typography variant="body2" color="text.secondary">No verification records yet.</Typography></TableCell></TableRow>
                    ) : (
                      oprpVerificationLogs.map((log: any) => (
                        <TableRow key={log.id}>
                          <TableCell>{log.batch_number ?? log.batch_id ?? '—'}</TableCell>
                          <TableCell>{formatDateTime(log.verification_date || log.created_at)}</TableCell>
                          <TableCell>{log.verified_by_name ?? log.verified_by ?? '—'}</TableCell>
                          <TableCell>
                            {log.conducted_as_expected === true ? 'Yes' : log.conducted_as_expected === false ? 'No' : '—'}
                          </TableCell>
                          <TableCell>{log.findings || '—'}</TableCell>
                        </TableRow>
                      ))
                    )}
                  </TableBody>
                </Table>
              </TableContainer>
              <Typography variant="subtitle2">Confirm verified for a batch</Typography>
              <FormControl component="fieldset" sx={{ mb: 1 }}>
                <Typography variant="caption" color="text.secondary" sx={{ display: 'block', mb: 0.5 }}>
                  OPRP conducted as expected?
                </Typography>
                <RadioGroup
                  row
                  value={oprpVerificationConductedAsExpected ? 'yes' : 'no'}
                  onChange={(_, v) => setOprpVerificationConductedAsExpected(v === 'yes')}
                >
                  <FormControlLabel value="yes" control={<Radio size="small" />} label="Yes – conducted as expected" />
                  <FormControlLabel value="no" control={<Radio size="small" />} label="No – not conducted as expected" />
                </RadioGroup>
              </FormControl>
              <Stack direction="row" flexWrap="wrap" spacing={2} alignItems="center">
                <Autocomplete
                  sx={{ minWidth: 220 }}
                  options={batchOptions}
                  open={batchOpen}
                  onOpen={() => setBatchOpen(true)}
                  onClose={() => setBatchOpen(false)}
                  getOptionLabel={(b: any) => b?.batch_number ?? String(b?.id ?? '')}
                  value={oprpVerificationBatchValue}
                  onChange={(_, val: any) => setOprpVerificationBatchValue(val)}
                  inputValue={batchSearch}
                  onInputChange={(_, val) => setBatchSearch(val)}
                  isOptionEqualToValue={(a: any, b: any) => a?.id === b?.id}
                  renderInput={(params) => <TextField {...params} label="Batch (optional)" size="small" />}
                />
                <TextField
                  size="small"
                  label="Notes"
                  value={oprpVerificationNotes}
                  onChange={(e) => setOprpVerificationNotes(e.target.value)}
                  placeholder="e.g. OPRP checked / done"
                  sx={{ minWidth: 200 }}
                />
                <Button variant="contained" onClick={handleConfirmOPRPVerification}>
                  Confirm verified
                </Button>
              </Stack>
            </Stack>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => { setOprpDetailDialogOpen(false); setSelectedOprpItem(null); }}>Close</Button>
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

