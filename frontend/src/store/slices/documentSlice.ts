import { createSlice, createAsyncThunk, PayloadAction } from '@reduxjs/toolkit';
import { documentsAPI } from '../../services/api';

// Types
export interface Document {
  id: number;
  document_number: string;
  title: string;
  description?: string;
  document_type: string;
  category: string;
  status: string;
  version: string;
  file_path?: string;
  file_size?: number;
  file_type?: string;
  original_filename?: string;
  department?: string;
  product_line?: string;
  applicable_products?: number[];
  keywords?: string;
  created_by: string;
  approved_by?: string;
  approved_at?: string;
  effective_date?: string;
  review_date?: string;
  created_at: string;
  updated_at?: string;
}

export interface DocumentVersion {
  id: number;
  version_number: string;
  file_path: string;
  file_size?: number;
  file_type?: string;
  original_filename?: string;
  change_description?: string;
  change_reason?: string;
  created_by: string;
  approved_by?: string;
  approved_at?: string;
  created_at: string;
  is_current: boolean;
}

export interface DocumentChangeLog {
  id: number;
  change_type: string;
  change_description?: string;
  old_version?: string;
  new_version?: string;
  changed_by: string;
  created_at: string;
}

export interface DocumentStats {
  total_documents: number;
  documents_by_status: Record<string, number>;
  documents_by_category: Record<string, number>;
  documents_by_type: Record<string, number>;
  pending_reviews: number;
  expired_documents: number;
  documents_requiring_approval: number;
}

export interface DocumentState {
  documents: Document[];
  selectedDocument: Document | null;
  documentVersions: DocumentVersion[];
  changeLog: DocumentChangeLog[];
  stats: DocumentStats | null;
  pendingApprovals: any[];
  loading: boolean;
  error: string | null;
  pagination: {
    page: number;
    size: number;
    total: number;
    pages: number;
  };
  filters: {
    search: string;
    category: string;
    status: string;
    document_type: string;
    department: string;
    product_line: string;
    created_by: number | null;
    date_from: string;
    date_to: string;
    review_date_from: string;
    review_date_to: string;
    keywords: string;
  };
}

const initialState: DocumentState = {
  documents: [],
  selectedDocument: null,
  documentVersions: [],
  changeLog: [],
  stats: null,
  pendingApprovals: [],
  loading: false,
  error: null,
  pagination: {
    page: 1,
    size: 10,
    total: 0,
    pages: 0,
  },
  filters: {
    search: '',
    category: '',
    status: '',
    document_type: '',
    department: '',
    product_line: '',
    created_by: null,
    date_from: '',
    date_to: '',
    review_date_from: '',
    review_date_to: '',
    keywords: '',
  },
};

// Async thunks
export const fetchDocuments = createAsyncThunk(
  'documents/fetchDocuments',
  async (params: any = {}, { rejectWithValue }) => {
    try {
      // Filter out empty string parameters for enum fields and date fields
      const filteredParams: any = {};
      if (params) {
        Object.entries(params).forEach(([key, value]) => {
          if (value !== undefined && value !== null && value !== '') {
            // For enum fields, only send if it's a valid value
            if (['category', 'status', 'document_type'].includes(key)) {
              if (value && typeof value === 'string' && value.trim() !== '') {
                filteredParams[key] = value;
              }
            }
            // For date fields, only send if it's a valid date string
            else if (['date_from', 'date_to', 'review_date_from', 'review_date_to'].includes(key)) {
              if (value && typeof value === 'string' && value.trim() !== '') {
                // Convert date to ISO format if it's a valid date
                try {
                  const date = new Date(value);
                  if (!isNaN(date.getTime())) {
                    filteredParams[key] = date.toISOString();
                  }
                } catch (e) {
                  // If date parsing fails, skip this parameter
                  console.warn(`Invalid date format for ${key}: ${value}`);
                }
              }
            }
            // For other fields, send if not empty
            else {
              filteredParams[key] = value;
            }
          }
        });
      }
      const response = await documentsAPI.getDocuments(filteredParams);
      return response;
    } catch (error: any) {
      return rejectWithValue(error.response?.data?.detail || 'Failed to fetch documents');
    }
  }
);

export const fetchDocument = createAsyncThunk(
  'documents/fetchDocument',
  async (documentId: number, { rejectWithValue }) => {
    try {
      const response = await documentsAPI.getDocument(documentId);
      return response;
    } catch (error: any) {
      return rejectWithValue(error.response?.data?.detail || 'Failed to fetch document');
    }
  }
);

export const createDocument = createAsyncThunk(
  'documents/createDocument',
  async (formData: FormData, { rejectWithValue }) => {
    try {
      const response = await documentsAPI.createDocument(formData);
      return response;
    } catch (error: any) {
      return rejectWithValue(error.response?.data?.detail || 'Failed to create document');
    }
  }
);

export const updateDocument = createAsyncThunk(
  'documents/updateDocument',
  async ({ documentId, formData }: { documentId: number; formData: FormData }, { rejectWithValue }) => {
    try {
      const response = await documentsAPI.updateDocument(documentId, formData);
      return response;
    } catch (error: any) {
      return rejectWithValue(error.response?.data?.detail || 'Failed to update document');
    }
  }
);

export const deleteDocument = createAsyncThunk(
  'documents/deleteDocument',
  async (documentId: number, { rejectWithValue }) => {
    try {
      const response = await documentsAPI.deleteDocument(documentId);
      return { documentId, response };
    } catch (error: any) {
      return rejectWithValue(error.response?.data?.detail || 'Failed to delete document');
    }
  }
);

export const fetchDocumentVersions = createAsyncThunk(
  'documents/fetchDocumentVersions',
  async (documentId: number, { rejectWithValue }) => {
    try {
      const response = await documentsAPI.getVersionHistory(documentId);
      return response;
    } catch (error: any) {
      return rejectWithValue(error.response?.data?.detail || 'Failed to fetch document versions');
    }
  }
);

export const createNewVersion = createAsyncThunk(
  'documents/createNewVersion',
  async ({ documentId, formData }: { documentId: number; formData: FormData }, { rejectWithValue }) => {
    try {
      const response = await documentsAPI.createNewVersion(documentId, formData);
      return response;
    } catch (error: any) {
      return rejectWithValue(error.response?.data?.detail || 'Failed to create new version');
    }
  }
);

// Legacy direct version approval removed in favor of workflow approvals chain

export const fetchChangeLog = createAsyncThunk(
  'documents/fetchChangeLog',
  async (documentId: number, { rejectWithValue }) => {
    try {
      const response = await documentsAPI.getChangeLog(documentId);
      return response;
    } catch (error: any) {
      return rejectWithValue(error.response?.data?.detail || 'Failed to fetch change log');
    }
  }
);

export const fetchDocumentStats = createAsyncThunk(
  'documents/fetchDocumentStats',
  async (_, { rejectWithValue }) => {
    try {
      const response = await documentsAPI.getDocumentStats();
      return response;
    } catch (error: any) {
      return rejectWithValue(error.response?.data?.detail || 'Failed to fetch document stats');
    }
  }
);

// Approvals (multi-step)
export const fetchPendingApprovals = createAsyncThunk(
  'documents/fetchPendingApprovals',
  async (_, { rejectWithValue }) => {
    try {
      const response = await documentsAPI.getPendingApprovals();
      return response;
    } catch (error: any) {
      return rejectWithValue(error.response?.data?.detail || 'Failed to fetch pending approvals');
    }
  }
);

export const approveApprovalStep = createAsyncThunk(
  'documents/approveApprovalStep',
  async (
    { documentId, approvalId, password, comments }: { documentId: number; approvalId: number; password?: string; comments?: string },
    { rejectWithValue }
  ) => {
    try {
      const response = await documentsAPI.approveApprovalStep(documentId, approvalId, { password, comments });
      return response;
    } catch (error: any) {
      return rejectWithValue(error.response?.data?.detail || 'Failed to approve');
    }
  }
);

export const rejectApprovalStep = createAsyncThunk(
  'documents/rejectApprovalStep',
  async (
    { documentId, approvalId, comments }: { documentId: number; approvalId: number; comments?: string },
    { rejectWithValue }
  ) => {
    try {
      const response = await documentsAPI.rejectApprovalStep(documentId, approvalId, { comments });
      return response;
    } catch (error: any) {
      return rejectWithValue(error.response?.data?.detail || 'Failed to reject');
    }
  }
);

export const bulkUpdateStatus = createAsyncThunk(
  'documents/bulkUpdateStatus',
  async ({ documentIds, action, reason }: { documentIds: number[]; action: string; reason?: string }, { rejectWithValue }) => {
    try {
      const response = await documentsAPI.bulkUpdateStatus(documentIds, action, reason);
      return response;
    } catch (error: any) {
      return rejectWithValue(error.response?.data?.detail || 'Failed to update document status');
    }
  }
);

export const archiveObsoleteDocuments = createAsyncThunk(
  'documents/archiveObsoleteDocuments',
  async (_, { rejectWithValue }) => {
    try {
      const response = await documentsAPI.archiveObsoleteDocuments();
      return response;
    } catch (error: any) {
      return rejectWithValue(error.response?.data?.detail || 'Failed to archive obsolete documents');
    }
  }
);

export const fetchExpiredDocuments = createAsyncThunk(
  'documents/fetchExpiredDocuments',
  async (_, { rejectWithValue }) => {
    try {
      const response = await documentsAPI.getExpiredDocuments();
      return response;
    } catch (error: any) {
      return rejectWithValue(error.response?.data?.detail || 'Failed to fetch expired documents');
    }
  }
);

export const downloadDocument = createAsyncThunk(
  'documents/downloadDocument',
  async (documentId: number, { rejectWithValue }) => {
    try {
      const response = await documentsAPI.downloadDocument(documentId);
      return response;
    } catch (error: any) {
      return rejectWithValue(error.response?.data?.detail || 'Failed to download document');
    }
  }
);

export const downloadVersion = createAsyncThunk(
  'documents/downloadVersion',
  async ({ documentId, versionId }: { documentId: number; versionId: number }, { rejectWithValue }) => {
    try {
      const response = await documentsAPI.downloadVersion(documentId, versionId);
      return response;
    } catch (error: any) {
      return rejectWithValue(error.response?.data?.detail || 'Failed to download version');
    }
  }
);

const documentSlice = createSlice({
  name: 'documents',
  initialState,
  reducers: {
    clearError: (state) => {
      state.error = null;
    },
    setSelectedDocument: (state, action: PayloadAction<Document | null>) => {
      state.selectedDocument = action.payload;
    },
    setFilters: (state, action: PayloadAction<Partial<DocumentState['filters']>>) => {
      state.filters = { ...state.filters, ...action.payload };
    },
    clearFilters: (state) => {
      state.filters = initialState.filters;
    },
    setPagination: (state, action: PayloadAction<Partial<DocumentState['pagination']>>) => {
      state.pagination = { ...state.pagination, ...action.payload };
    },
  },
  extraReducers: (builder) => {
    builder
      // Fetch Documents
      .addCase(fetchDocuments.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(fetchDocuments.fulfilled, (state, action) => {
        state.loading = false;
        state.documents = action.payload.data.items || [];
        state.pagination = {
          page: action.payload.data.page || 1,
          size: action.payload.data.size || 10,
          total: action.payload.data.total || 0,
          pages: action.payload.data.pages || 0,
        };
      })
      .addCase(fetchDocuments.rejected, (state, action) => {
        state.loading = false;
        state.error = typeof action.payload === 'string' ? action.payload : 'Failed to fetch documents';
      })

      // Fetch Single Document
      .addCase(fetchDocument.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(fetchDocument.fulfilled, (state, action) => {
        state.loading = false;
        state.selectedDocument = action.payload.data;
      })
      .addCase(fetchDocument.rejected, (state, action) => {
        state.loading = false;
        state.error = typeof action.payload === 'string' ? action.payload : 'Failed to fetch document';
      })

      // Create Document
      .addCase(createDocument.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(createDocument.fulfilled, (state) => {
        state.loading = false;
      })
      .addCase(createDocument.rejected, (state, action) => {
        state.loading = false;
        state.error = typeof action.payload === 'string' ? action.payload : 'Failed to create document';
      })

      // Update Document
      .addCase(updateDocument.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(updateDocument.fulfilled, (state) => {
        state.loading = false;
      })
      .addCase(updateDocument.rejected, (state, action) => {
        state.loading = false;
        state.error = typeof action.payload === 'string' ? action.payload : 'Failed to update document';
      })

      // Delete Document
      .addCase(deleteDocument.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(deleteDocument.fulfilled, (state, action) => {
        state.loading = false;
        // Remove deleted document from state
        state.documents = state.documents.filter(doc => doc.id !== action.payload.documentId);
      })
      .addCase(deleteDocument.rejected, (state, action) => {
        state.loading = false;
        state.error = typeof action.payload === 'string' ? action.payload : 'Failed to delete document';
      })

      // Fetch Document Versions
      .addCase(fetchDocumentVersions.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(fetchDocumentVersions.fulfilled, (state, action) => {
        state.loading = false;
        state.documentVersions = action.payload.data.versions || [];
      })
      .addCase(fetchDocumentVersions.rejected, (state, action) => {
        state.loading = false;
        state.error = typeof action.payload === 'string' ? action.payload : 'Failed to fetch document versions';
      })

      // Create New Version
      .addCase(createNewVersion.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(createNewVersion.fulfilled, (state) => {
        state.loading = false;
      })
      .addCase(createNewVersion.rejected, (state, action) => {
        state.loading = false;
        state.error = typeof action.payload === 'string' ? action.payload : 'Failed to create new version';
      })

      // Direct version approval removed; workflow updates list via refresh/fetch

      // Fetch Change Log
      .addCase(fetchChangeLog.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(fetchChangeLog.fulfilled, (state, action) => {
        state.loading = false;
        state.changeLog = action.payload.data.changes || [];
      })
      .addCase(fetchChangeLog.rejected, (state, action) => {
        state.loading = false;
        state.error = typeof action.payload === 'string' ? action.payload : 'Failed to fetch change log';
      })

      // Fetch Document Stats
      .addCase(fetchDocumentStats.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(fetchDocumentStats.fulfilled, (state, action) => {
        state.loading = false;
        state.stats = action.payload.data;
      })
      .addCase(fetchDocumentStats.rejected, (state, action) => {
        state.loading = false;
        state.error = typeof action.payload === 'string' ? action.payload : 'Failed to fetch document stats';
      })

      // Pending approvals
      .addCase(fetchPendingApprovals.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(fetchPendingApprovals.fulfilled, (state, action) => {
        state.loading = false;
        state.pendingApprovals = action.payload.data?.items || action.payload.data || [];
      })
      .addCase(fetchPendingApprovals.rejected, (state, action) => {
        state.loading = false;
        state.error = typeof action.payload === 'string' ? action.payload : 'Failed to fetch pending approvals';
      })

      .addCase(approveApprovalStep.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(approveApprovalStep.fulfilled, (state) => {
        state.loading = false;
      })
      .addCase(approveApprovalStep.rejected, (state, action) => {
        state.loading = false;
        state.error = typeof action.payload === 'string' ? action.payload : 'Failed to approve';
      })

      .addCase(rejectApprovalStep.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(rejectApprovalStep.fulfilled, (state) => {
        state.loading = false;
      })
      .addCase(rejectApprovalStep.rejected, (state, action) => {
        state.loading = false;
        state.error = typeof action.payload === 'string' ? action.payload : 'Failed to reject';
      })

      // Bulk Update Status
      .addCase(bulkUpdateStatus.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(bulkUpdateStatus.fulfilled, (state) => {
        state.loading = false;
      })
      .addCase(bulkUpdateStatus.rejected, (state, action) => {
        state.loading = false;
        state.error = typeof action.payload === 'string' ? action.payload : 'Failed to update document status';
      })

      // Archive Obsolete Documents
      .addCase(archiveObsoleteDocuments.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(archiveObsoleteDocuments.fulfilled, (state) => {
        state.loading = false;
      })
      .addCase(archiveObsoleteDocuments.rejected, (state, action) => {
        state.loading = false;
        state.error = typeof action.payload === 'string' ? action.payload : 'Failed to archive obsolete documents';
      })

      // Fetch Expired Documents
      .addCase(fetchExpiredDocuments.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(fetchExpiredDocuments.fulfilled, (state, action) => {
        state.loading = false;
        // Handle expired documents data if needed
      })
      .addCase(fetchExpiredDocuments.rejected, (state, action) => {
        state.loading = false;
        state.error = typeof action.payload === 'string' ? action.payload : 'Failed to fetch expired documents';
      })

      // Download Document
      .addCase(downloadDocument.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(downloadDocument.fulfilled, (state) => {
        state.loading = false;
      })
      .addCase(downloadDocument.rejected, (state, action) => {
        state.loading = false;
        state.error = typeof action.payload === 'string' ? action.payload : 'Failed to download document';
      })

      // Download Version
      .addCase(downloadVersion.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(downloadVersion.fulfilled, (state) => {
        state.loading = false;
      })
      .addCase(downloadVersion.rejected, (state, action) => {
        state.loading = false;
        state.error = typeof action.payload === 'string' ? action.payload : 'Failed to download version';
      });
  },
});

export const { clearError, setSelectedDocument, setFilters, clearFilters, setPagination } = documentSlice.actions;

export default documentSlice.reducer; 