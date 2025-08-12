import React, { useEffect, useState } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { useParams } from 'react-router-dom';
import { Box, Typography, Paper, Stack, Button, TextField, Table, TableHead, TableRow, TableCell, TableBody, Dialog, DialogTitle, DialogContent, DialogActions, Autocomplete, IconButton, TablePagination, Checkbox, FormControlLabel, RadioGroup, Radio } from '@mui/material';
import EditIcon from '@mui/icons-material/Edit';
import DeleteIcon from '@mui/icons-material/Delete';
import { AppDispatch, RootState } from '../store';
import { fetchProgram, fetchSessions, createSession, updateSession, deleteSession } from '../store/slices/trainingSlice';
import { trainingAPI, usersAPI } from '../services/api';

const TrainingProgramDetail: React.FC = () => {
  const { id } = useParams();
  const programId = Number(id);
  const dispatch = useDispatch<AppDispatch>();
  const { selectedProgram, sessions } = useSelector((s: RootState) => s.training as any);
  const [open, setOpen] = useState(false);
  const [form, setForm] = useState({ session_date: '', location: '', trainer: '', notes: '' });
  const [attendOpen, setAttendOpen] = useState(false);
  const [selectedSessionId, setSelectedSessionId] = useState<number | null>(null);
  const [attendForm, setAttendForm] = useState({ user_id: '', attended: true as boolean, comments: '' });
  const [attendance, setAttendance] = useState<any[]>([]);
  const [userOptions, setUserOptions] = useState<Array<{ id: number; username: string; full_name?: string }>>([]);
  const [userSearch, setUserSearch] = useState('');
  const [userOpen, setUserOpen] = useState(false);
  const [userInput, setUserInput] = useState('');
  const [materials, setMaterials] = useState<any[]>([]);
  const [uploading, setUploading] = useState(false);
  const [quizzes, setQuizzes] = useState<any[]>([]);
  const [quizOpen, setQuizOpen] = useState(false);
  const [quizForm, setQuizForm] = useState<{ title: string; description: string; pass_threshold: number; is_published: boolean; questions: Array<{ text: string; order_index: number; options: Array<{ text: string; is_correct: boolean }> }> }>({ title: '', description: '', pass_threshold: 70, is_published: false, questions: [{ text: '', order_index: 0, options: [{ text: '', is_correct: true }, { text: '', is_correct: false }] }] });
  const [takeOpen, setTakeOpen] = useState(false);
  const [activeQuiz, setActiveQuiz] = useState<any | null>(null);
  const [answers, setAnswers] = useState<Record<number, number>>({});
  const [submitResult, setSubmitResult] = useState<{ score_percent: number; passed: boolean } | null>(null);
  const [sessionCertificates, setSessionCertificates] = useState<any[]>([]);
  const [certUploading, setCertUploading] = useState(false);

  const handleProgramMaterialUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const inputEl = e.currentTarget;
    const file = inputEl.files?.[0];
    if (!file) return;
    setUploading(true);
    try {
      await trainingAPI.uploadProgramMaterial(programId, file);
      const mats = await trainingAPI.listProgramMaterials(programId);
      setMaterials(mats || []);
    } finally {
      setUploading(false);
      // Reset input safely using stored element reference
      try { inputEl.value = ''; } catch {}
    }
  };
  const [editOpen, setEditOpen] = useState(false);
  const [editForm, setEditForm] = useState<{ id?: number; session_date: string; location?: string; trainer?: string; notes?: string }>({ session_date: '' });
  const [page, setPage] = useState(0);
  const [rowsPerPage, setRowsPerPage] = useState(5);

  useEffect(() => {
    if (!Number.isNaN(programId)) {
      dispatch(fetchProgram(programId));
      dispatch(fetchSessions(programId));
      (async () => {
        const mats = await trainingAPI.listProgramMaterials(programId);
        setMaterials(mats || []);
        const qz = await trainingAPI.listProgramQuizzes(programId);
        setQuizzes(qz || []);
      })();
    }
  }, [dispatch, programId]);

  const onCreateSession = async () => {
    await dispatch(createSession({ programId, payload: { session_date: new Date(`${form.session_date}T00:00:00`).toISOString(), location: form.location || undefined, trainer: form.trainer || undefined, notes: form.notes || undefined } }));
    setOpen(false);
    setForm({ session_date: '', location: '', trainer: '', notes: '' });
  };

  const openAttendance = async (sessionId: number) => {
    try {
      setSelectedSessionId(sessionId);
      const res = await trainingAPI.getAttendance(sessionId);
      setAttendance(res || []);
      // Load certificates for this session
      try {
        const certs = await trainingAPI.listSessionCertificates(sessionId);
        setSessionCertificates(certs || []);
      } catch (e) {
        setSessionCertificates([]);
      }
      setAttendOpen(true);
    } catch (err: any) {
      console.error('Failed to load attendance', err);
      alert(err?.response?.data?.message || 'Failed to load attendance');
    }
  };

  const addAttendance = async () => {
    if (!selectedSessionId) return;
    try {
      await trainingAPI.addAttendance(selectedSessionId, { user_id: Number(attendForm.user_id), attended: attendForm.attended, comments: attendForm.comments || undefined });
      const res = await trainingAPI.getAttendance(selectedSessionId);
      setAttendance(res || []);
      setAttendForm({ user_id: '', attended: true, comments: '' });
    } catch (err: any) {
      console.error('Failed to add attendance', err);
      alert(err?.response?.data?.message || 'Failed to add attendance');
    }
  };

  // Debounced user search for dropdown
  useEffect(() => {
    let active = true;
    if (!userOpen) return;
    const t = setTimeout(async () => {
      try {
        const resp: any = await usersAPI.getUsers({ page: 1, size: 10, search: userSearch });
        const items = (resp?.data?.items || resp?.items || []) as Array<any>;
        if (active) setUserOptions(items.map((u) => ({ id: u.id, username: u.username, full_name: u.full_name })));
      } catch {
        if (active) setUserOptions([]);
      }
    }, 300);
    return () => { active = false; clearTimeout(t); };
  }, [userSearch, userOpen]);

  if (!selectedProgram) return null;

  return (
    <Box p={3}>
      <Typography variant="h5" fontWeight="bold">{selectedProgram.title}</Typography>
      <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>{selectedProgram.description}</Typography>

      <Paper sx={{ p: 2, mb: 2 }}>
        <Stack direction={{ xs: 'column', sm: 'row' }} justifyContent="space-between" alignItems="center">
          <Typography variant="subtitle1">Materials</Typography>
          <Button component="label" variant="outlined" disabled={uploading}>
            {uploading ? 'Uploading...' : 'Upload'}
            <input hidden type="file" onChange={handleProgramMaterialUpload} />
          </Button>
        </Stack>
        <Table size="small" sx={{ mt: 1 }}>
          <TableHead>
            <TableRow>
              <TableCell>File</TableCell>
              <TableCell>Type</TableCell>
              <TableCell>Uploaded</TableCell>
              <TableCell align="right">Actions</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {materials.map((m: any) => (
              <TableRow key={m.id}>
                <TableCell>{m.original_filename}</TableCell>
                <TableCell>{m.file_type || '-'}</TableCell>
                <TableCell>{m.uploaded_at}</TableCell>
                <TableCell align="right">
                  <Button size="small" onClick={async () => {
                    const blob = await trainingAPI.downloadMaterial(m.id);
                    const url = window.URL.createObjectURL(blob);
                    const a = document.createElement('a');
                    a.href = url; a.download = m.original_filename; a.click();
                    window.URL.revokeObjectURL(url);
                  }}>Download</Button>
                  <Button size="small" color="error" onClick={async () => {
                    await trainingAPI.deleteMaterial(m.id);
                    const mats = await trainingAPI.listProgramMaterials(programId);
                    setMaterials(mats || []);
                  }}>Delete</Button>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </Paper>

      <Paper sx={{ p: 2, mb: 2 }}>
        <Stack direction={{ xs: 'column', sm: 'row' }} justifyContent="space-between" alignItems="center">
          <Typography variant="subtitle1">Quizzes</Typography>
          <Button variant="contained" onClick={() => setQuizOpen(true)}>New Quiz</Button>
        </Stack>
        <Table size="small" sx={{ mt: 1 }}>
          <TableHead>
            <TableRow>
              <TableCell>Title</TableCell>
              <TableCell>Pass %</TableCell>
              <TableCell>Published</TableCell>
              <TableCell>Questions</TableCell>
              <TableCell>Created</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {quizzes.map((q: any) => (
              <TableRow key={q.id}>
                <TableCell>{q.title}</TableCell>
                <TableCell>{q.pass_threshold}</TableCell>
                <TableCell>{String(q.is_published)}</TableCell>
                <TableCell>{q.questions?.length || 0}</TableCell>
                <TableCell>
                  <Stack direction="row" spacing={1} alignItems="center">
                    <span>{q.created_at}</span>
                    <Button size="small" variant="outlined" onClick={async () => {
                      const full = await trainingAPI.getQuiz(q.id);
                      setActiveQuiz(full);
                      setAnswers({});
                      setSubmitResult(null);
                      setTakeOpen(true);
                    }}>Take</Button>
                  </Stack>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </Paper>

      <Paper sx={{ p: 2, mb: 2 }}>
        <Stack direction={{ xs: 'column', sm: 'row' }} justifyContent="space-between" alignItems="center">
          <Typography variant="subtitle1">Sessions</Typography>
          <Button variant="contained" onClick={() => setOpen(true)}>New Session</Button>
        </Stack>
        <Table size="small" sx={{ mt: 1 }}>
          <TableHead>
            <TableRow>
              <TableCell>Date</TableCell>
              <TableCell>Location</TableCell>
              <TableCell>Trainer</TableCell>
              <TableCell>Notes</TableCell>
              <TableCell align="right">Actions</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {sessions.slice(page * rowsPerPage, page * rowsPerPage + rowsPerPage).map((s: any) => (
              <TableRow key={s.id}>
                <TableCell>{s.session_date}</TableCell>
                <TableCell>{s.location || '-'}</TableCell>
                <TableCell>{s.trainer || '-'}</TableCell>
                <TableCell>{s.notes || '-'}</TableCell>
                <TableCell align="right">
                  <Button size="small" onClick={() => openAttendance(s.id)} sx={{ mr: 1 }}>Attendance</Button>
                  <IconButton size="small" onClick={() => { setEditForm({ id: s.id, session_date: (s.session_date || '').slice(0, 10), location: s.location, trainer: s.trainer, notes: s.notes }); setEditOpen(true); }}>
                    <EditIcon fontSize="small" />
                  </IconButton>
                  <IconButton size="small" color="error" onClick={() => dispatch(deleteSession(s.id) as any)}>
                    <DeleteIcon fontSize="small" />
                  </IconButton>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
        <TablePagination
          component="div"
          count={sessions.length}
          page={page}
          onPageChange={(_, newPage) => setPage(newPage)}
          rowsPerPage={rowsPerPage}
          onRowsPerPageChange={(e) => { setRowsPerPage(parseInt(e.target.value, 10)); setPage(0); }}
          rowsPerPageOptions={[5, 10, 25]}
        />
      </Paper>

      {/* Create Session */}
      <Dialog open={open} onClose={() => setOpen(false)} maxWidth="sm" fullWidth>
        <DialogTitle>New Session</DialogTitle>
        <DialogContent>
          <Stack spacing={2} sx={{ mt: 1 }}>
            <TextField type="date" label="Date" InputLabelProps={{ shrink: true }} value={form.session_date} onChange={e => setForm({ ...form, session_date: e.target.value })} />
            <TextField label="Location" value={form.location} onChange={e => setForm({ ...form, location: e.target.value })} />
            <TextField label="Trainer" value={form.trainer} onChange={e => setForm({ ...form, trainer: e.target.value })} />
            <TextField label="Notes" multiline rows={3} value={form.notes} onChange={e => setForm({ ...form, notes: e.target.value })} />
          </Stack>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setOpen(false)}>Cancel</Button>
          <Button variant="contained" onClick={onCreateSession}>Create</Button>
        </DialogActions>
      </Dialog>

      {/* Attendance */}
      <Dialog open={attendOpen} onClose={() => setAttendOpen(false)} maxWidth="md" fullWidth>
        <DialogTitle>Attendance</DialogTitle>
        <DialogContent>
          <Stack spacing={2} sx={{ mt: 1 }}>
            <Stack direction={{ xs: 'column', sm: 'row' }} spacing={2}>
              <Autocomplete
                options={userOptions}
                open={userOpen}
                onOpen={() => setUserOpen(true)}
                onClose={() => setUserOpen(false)}
                getOptionLabel={(opt) => (opt.full_name ? `${opt.full_name} (${opt.username})` : opt.username)}
                value={userOptions.find(o => String(o.id) === attendForm.user_id) || null}
                onChange={(_, val) => setAttendForm({ ...attendForm, user_id: val ? String(val.id) : '' })}
                inputValue={userInput}
                onInputChange={(_, val) => { setUserInput(val); setUserSearch(val); }}
                isOptionEqualToValue={(opt, val) => opt.id === val.id}
                renderInput={(params) => <TextField {...params} label="User" placeholder="Search user..." />}
              />
              <TextField label="Comments" value={attendForm.comments} onChange={e => setAttendForm({ ...attendForm, comments: e.target.value })} />
              <Button variant="contained" onClick={addAttendance}>Add</Button>
            </Stack>
            <Paper variant="outlined" sx={{ p: 1 }}>
              <Table size="small">
                <TableHead>
                  <TableRow>
                    <TableCell>User</TableCell>
                    <TableCell>Attended</TableCell>
                    <TableCell>Comments</TableCell>
                    <TableCell>Created</TableCell>
                    <TableCell align="right">Actions</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {attendance.map((a: any) => (
                    <TableRow key={a.id}>
                      <TableCell>{a.user_full_name ? `${a.user_full_name} (${a.username})` : a.user_id}</TableCell>
                      <TableCell>
                        <Button size="small" variant={a.attended ? 'contained' : 'outlined'} onClick={async () => {
                          await trainingAPI.updateAttendance?.(a.id, { attended: !a.attended });
                          const res = await trainingAPI.getAttendance(selectedSessionId!);
                          setAttendance(res || []);
                        }}>{a.attended ? 'Present' : 'Absent'}</Button>
                      </TableCell>
                      <TableCell>{a.comments || '-'}</TableCell>
                      <TableCell>{a.created_at}</TableCell>
                      <TableCell align="right">
                        <Button size="small" color="error" onClick={async () => { await trainingAPI.deleteAttendance?.(a.id); const res = await trainingAPI.getAttendance(selectedSessionId!); setAttendance(res || []); }}>Delete</Button>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </Paper>

            {/* Certificates for this session */}
            <Paper variant="outlined" sx={{ p: 1 }}>
              <Stack direction={{ xs: 'column', sm: 'row' }} justifyContent="space-between" alignItems="center">
                <Typography variant="subtitle2">Certificates</Typography>
                <Button component="label" size="small" variant="outlined" disabled={certUploading}>
                  {certUploading ? 'Uploading...' : 'Upload Certificate'}
                  <input hidden type="file" onChange={async (e) => {
                    const file = e.currentTarget.files?.[0];
                    if (!file || !selectedSessionId) return;
                    setCertUploading(true);
                    try {
                      await trainingAPI.uploadCertificate(selectedSessionId, file);
                      const certs = await trainingAPI.listSessionCertificates(selectedSessionId);
                      setSessionCertificates(certs || []);
                    } finally {
                      setCertUploading(false);
                      try { e.currentTarget.value = ''; } catch {}
                    }
                  }} />
                </Button>
              </Stack>
              <Table size="small" sx={{ mt: 1 }}>
                <TableHead>
                  <TableRow>
                    <TableCell>File</TableCell>
                    <TableCell>Issued</TableCell>
                    <TableCell>Verification Code</TableCell>
                    <TableCell align="right">Actions</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {sessionCertificates.map((c: any) => (
                    <TableRow key={c.id}>
                      <TableCell>{c.original_filename}</TableCell>
                      <TableCell>{c.issued_at}</TableCell>
                      <TableCell>{c.verification_code}</TableCell>
                      <TableCell align="right">
                        <Button size="small" onClick={async () => {
                          const blob = await trainingAPI.downloadCertificate(c.id);
                          const url = window.URL.createObjectURL(blob);
                          const a = document.createElement('a'); a.href = url; a.download = c.original_filename; a.click(); window.URL.revokeObjectURL(url);
                        }}>Download</Button>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </Paper>
          </Stack>
        </DialogContent>
        <DialogActions>
          <Button onClick={async () => { if (!selectedSessionId) return; const blob = await trainingAPI.exportAttendanceCSV?.(selectedSessionId); const url = window.URL.createObjectURL(blob); const a = document.createElement('a'); a.href = url; a.download = `attendance_${selectedSessionId}.csv`; a.click(); window.URL.revokeObjectURL(url); }}>Export CSV</Button>
          <Button onClick={() => setAttendOpen(false)}>Close</Button>
        </DialogActions>
      </Dialog>

      {/* Edit Session */}
      <Dialog open={editOpen} onClose={() => setEditOpen(false)} maxWidth="sm" fullWidth>
        <DialogTitle>Edit Session</DialogTitle>
        <DialogContent>
          <Stack spacing={2} sx={{ mt: 1 }}>
            <TextField type="date" label="Date" InputLabelProps={{ shrink: true }} value={editForm.session_date} onChange={e => setEditForm({ ...editForm, session_date: e.target.value })} />
            <TextField label="Location" value={editForm.location || ''} onChange={e => setEditForm({ ...editForm, location: e.target.value })} />
            <TextField label="Trainer" value={editForm.trainer || ''} onChange={e => setEditForm({ ...editForm, trainer: e.target.value })} />
            <TextField label="Notes" multiline rows={3} value={editForm.notes || ''} onChange={e => setEditForm({ ...editForm, notes: e.target.value })} />
          </Stack>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setEditOpen(false)}>Cancel</Button>
          <Button variant="contained" onClick={async () => {
            if (!editForm.id) return;
            await dispatch(updateSession({ sessionId: editForm.id, payload: {
              session_date: editForm.session_date ? new Date(`${editForm.session_date}T00:00:00`).toISOString() : undefined,
              location: editForm.location || undefined,
              trainer: editForm.trainer || undefined,
              notes: editForm.notes || undefined,
            } }) as any);
            setEditOpen(false);
          }}>Save</Button>
        </DialogActions>
      </Dialog>

      {/* New Quiz */}
      <Dialog open={quizOpen} onClose={() => setQuizOpen(false)} maxWidth="md" fullWidth>
        <DialogTitle>New Quiz</DialogTitle>
        <DialogContent>
          <Stack spacing={2} sx={{ mt: 1 }}>
            <TextField label="Title" value={quizForm.title} onChange={e => setQuizForm({ ...quizForm, title: e.target.value })} />
            <TextField label="Description" value={quizForm.description} onChange={e => setQuizForm({ ...quizForm, description: e.target.value })} />
            <Stack direction={{ xs: 'column', sm: 'row' }} spacing={2}>
              <TextField type="number" label="Pass Threshold (%)" value={quizForm.pass_threshold} onChange={e => setQuizForm({ ...quizForm, pass_threshold: Number(e.target.value || 0) })} />
              <FormControlLabel control={<Checkbox checked={quizForm.is_published} onChange={e => setQuizForm({ ...quizForm, is_published: e.target.checked })} />} label="Published" />
            </Stack>
            {quizForm.questions.map((q, qi) => (
              <Paper key={qi} variant="outlined" sx={{ p: 1 }}>
                <Stack spacing={1}>
                  <TextField label={`Question ${qi + 1}`} value={q.text} onChange={e => {
                    const qs = [...quizForm.questions];
                    qs[qi] = { ...qs[qi], text: e.target.value };
                    setQuizForm({ ...quizForm, questions: qs });
                  }} />
                  {q.options.map((op, oi) => (
                    <Stack key={oi} direction={{ xs: 'column', sm: 'row' }} spacing={1} alignItems="center">
                      <Checkbox checked={op.is_correct} onChange={e => {
                        const qs = [...quizForm.questions];
                        qs[qi].options[oi].is_correct = e.target.checked;
                        setQuizForm({ ...quizForm, questions: qs });
                      }} />
                      <TextField label={`Option ${oi + 1}`} value={op.text} onChange={e => {
                        const qs = [...quizForm.questions];
                        qs[qi].options[oi].text = e.target.value;
                        setQuizForm({ ...quizForm, questions: qs });
                      }} />
                    </Stack>
                  ))}
                  <Stack direction="row" spacing={1}>
                    <Button size="small" onClick={() => {
                      const qs = [...quizForm.questions];
                      qs[qi].options.push({ text: '', is_correct: false });
                      setQuizForm({ ...quizForm, questions: qs });
                    }}>Add Option</Button>
                    <Button size="small" color="error" onClick={() => {
                      const qs = [...quizForm.questions];
                      if (qs[qi].options.length > 1) { qs[qi].options.pop(); setQuizForm({ ...quizForm, questions: qs }); }
                    }}>Remove Option</Button>
                  </Stack>
                </Stack>
              </Paper>
            ))}
            <Button onClick={() => setQuizForm({ ...quizForm, questions: [...quizForm.questions, { text: '', order_index: quizForm.questions.length, options: [{ text: '', is_correct: true }, { text: '', is_correct: false }] }] })}>Add Question</Button>
          </Stack>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setQuizOpen(false)}>Cancel</Button>
          <Button variant="contained" onClick={async () => {
            const payload = {
              title: quizForm.title,
              description: quizForm.description || undefined,
              pass_threshold: quizForm.pass_threshold,
              is_published: quizForm.is_published,
              questions: quizForm.questions.map((q, idx) => ({ text: q.text, order_index: idx, options: q.options.map(o => ({ text: o.text, is_correct: !!o.is_correct })) })),
            };
            await trainingAPI.createProgramQuiz(programId, payload);
            const qz = await trainingAPI.listProgramQuizzes(programId);
            setQuizzes(qz || []);
            setQuizOpen(false);
            setQuizForm({ title: '', description: '', pass_threshold: 70, is_published: false, questions: [{ text: '', order_index: 0, options: [{ text: '', is_correct: true }, { text: '', is_correct: false }] }] });
          }}>Create</Button>
        </DialogActions>
      </Dialog>

      {/* Take Quiz */}
      <Dialog open={takeOpen} onClose={() => setTakeOpen(false)} maxWidth="md" fullWidth>
        <DialogTitle>{activeQuiz ? `Take Quiz: ${activeQuiz.title}` : 'Take Quiz'}</DialogTitle>
        <DialogContent>
          <Stack spacing={2} sx={{ mt: 1 }}>
            {submitResult && (
              <Paper variant="outlined" sx={{ p: 2, bgcolor: submitResult.passed ? 'success.light' : 'error.light' }}>
                <Typography variant="subtitle2">Result</Typography>
                <Typography>{`Score: ${submitResult.score_percent.toFixed(1)}% — ${submitResult.passed ? 'Passed' : 'Failed'}`}</Typography>
              </Paper>
            )}
            {activeQuiz?.questions?.map((q: any, idx: number) => (
              <Paper key={q.id} variant="outlined" sx={{ p: 2 }}>
                <Typography variant="subtitle2" sx={{ mb: 1 }}>{`Q${idx + 1}. ${q.text}`}</Typography>
                <RadioGroup value={answers[q.id] || ''} onChange={(_, val) => setAnswers({ ...answers, [q.id]: Number(val) })}>
                  {q.options?.map((op: any) => (
                    <FormControlLabel key={op.id} value={op.id} control={<Radio />} label={op.text} />
                  ))}
                </RadioGroup>
              </Paper>
            ))}
          </Stack>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setTakeOpen(false)}>Close</Button>
          <Button variant="contained" disabled={!activeQuiz || (activeQuiz?.questions || []).some((q: any) => !answers[q.id])} onClick={async () => {
            if (!activeQuiz) return;
            const payload = Object.entries(answers).map(([qid, oid]) => ({ question_id: Number(qid), selected_option_id: Number(oid) }));
            const res = await trainingAPI.submitQuiz(activeQuiz.id, payload);
            setSubmitResult({ score_percent: res.score_percent, passed: !!res.passed });
          }}>Submit</Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default TrainingProgramDetail;


