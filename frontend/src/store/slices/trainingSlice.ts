import { createSlice, createAsyncThunk, PayloadAction } from '@reduxjs/toolkit';
import { trainingAPI } from '../../services/api';

export interface TrainingProgram {
  id: number;
  code: string;
  title: string;
  description?: string;
  department?: string;
  created_at: string;
  created_by: number;
}

export interface TrainingSession {
  id: number;
  program_id: number;
  session_date: string;
  location?: string;
  trainer?: string;
  notes?: string;
}

interface TrainingState {
  programs: TrainingProgram[];
  selectedProgram?: TrainingProgram;
  sessions: TrainingSession[];
  loading: boolean;
  error?: string;
}

const initialState: TrainingState = {
  programs: [],
  sessions: [],
  loading: false,
};

export const fetchPrograms = createAsyncThunk('training/fetchPrograms', async (search?: string) => {
  const res = await trainingAPI.getPrograms(search ? { search } : undefined);
  return res as TrainingProgram[];
});

export const createProgram = createAsyncThunk('training/createProgram', async (payload: { code: string; title: string; description?: string; department?: string }) => {
  const res = await trainingAPI.createProgram(payload);
  return res as TrainingProgram;
});

export const fetchProgram = createAsyncThunk('training/fetchProgram', async (programId: number) => {
  const res = await trainingAPI.getProgram(programId);
  return res as TrainingProgram;
});

export const updateProgram = createAsyncThunk('training/updateProgram', async ({ programId, payload }: { programId: number; payload: { title?: string; description?: string; department?: string } }) => {
  const res = await trainingAPI.updateProgram(programId, payload);
  return res as TrainingProgram;
});

export const deleteProgram = createAsyncThunk('training/deleteProgram', async (programId: number) => {
  await trainingAPI.deleteProgram(programId);
  return programId;
});

export const fetchSessions = createAsyncThunk('training/fetchSessions', async (programId: number) => {
  const res = await trainingAPI.getSessions(programId);
  return res as TrainingSession[];
});

export const createSession = createAsyncThunk('training/createSession', async ({ programId, payload }: { programId: number; payload: { session_date: string; location?: string; trainer?: string; notes?: string } }) => {
  const res = await trainingAPI.createSession(programId, payload);
  return res as TrainingSession;
});

export const updateSession = createAsyncThunk('training/updateSession', async ({ sessionId, payload }: { sessionId: number; payload: { session_date?: string; location?: string; trainer?: string; notes?: string } }) => {
  const res = await trainingAPI.updateSession(sessionId, payload);
  return res as TrainingSession;
});

export const deleteSession = createAsyncThunk('training/deleteSession', async (sessionId: number) => {
  await trainingAPI.deleteSession(sessionId);
  return sessionId;
});

export const trainingSlice = createSlice({
  name: 'training',
  initialState,
  reducers: {
    resetSelectedProgram(state) {
      state.selectedProgram = undefined;
      state.sessions = [];
    }
  },
  extraReducers: (builder) => {
    builder
      .addCase(fetchPrograms.pending, (state) => { state.loading = true; state.error = undefined; })
      .addCase(fetchPrograms.fulfilled, (state, action: PayloadAction<TrainingProgram[]>) => { state.loading = false; state.programs = action.payload; })
      .addCase(fetchPrograms.rejected, (state, action) => { state.loading = false; state.error = action.error.message; })
      .addCase(createProgram.fulfilled, (state, action: PayloadAction<TrainingProgram>) => { state.programs.unshift(action.payload); })
      .addCase(fetchProgram.fulfilled, (state, action: PayloadAction<TrainingProgram>) => { state.selectedProgram = action.payload; })
      .addCase(updateProgram.fulfilled, (state, action: PayloadAction<TrainingProgram>) => { state.selectedProgram = action.payload; state.programs = state.programs.map(p => p.id === action.payload.id ? action.payload : p); })
      .addCase(deleteProgram.fulfilled, (state, action: PayloadAction<number>) => { state.programs = state.programs.filter(p => p.id !== action.payload); })
      .addCase(fetchSessions.fulfilled, (state, action: PayloadAction<TrainingSession[]>) => { state.sessions = action.payload; })
      .addCase(createSession.fulfilled, (state, action: PayloadAction<TrainingSession>) => { state.sessions.unshift(action.payload); })
      .addCase(updateSession.fulfilled, (state, action: PayloadAction<TrainingSession>) => { state.sessions = state.sessions.map(s => s.id === action.payload.id ? action.payload : s); })
      .addCase(deleteSession.fulfilled, (state, action: PayloadAction<number>) => { state.sessions = state.sessions.filter(s => s.id !== action.payload); });
  }
});

export const { resetSelectedProgram } = trainingSlice.actions;
export default trainingSlice.reducer;


