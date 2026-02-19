// @ts-nocheck
import AxiosMockAdapter from 'axios-mock-adapter';
import axios from 'axios';
import api, { authAPI } from '../services/api';

// Simple in-memory database for demo
const db = {
  users: [] as any[],
  documents: [] as any[],
  documentApprovals: [] as any[],
  documentVersions: new Map<number, any[]>(),
  documentChangeLogs: new Map<number, any[]>(),
  haccp: {
    products: [] as any[],
    flows: [] as any[],
    hazards: [] as any[],
    ccps: [] as any[],
    contactSurfaces: [] as any[],
    dashboard: {
      total_products: 3,
      approved_plans: 2,
      total_ccps: 5,
      active_ccps: 4,
      recent_logs: [
        { description: 'CCP monitoring completed', created_at: new Date(Date.now() - 3600 * 1000).toISOString() },
        { description: 'Verification activity recorded', created_at: new Date(Date.now() - 2 * 3600 * 1000).toISOString() },
      ] as any[],
      out_of_spec_count: 1,
      out_of_spec_ccps: [
        { id: 1, ccp_number: 'CCP-1', ccp_name: 'Mix temp', process_step: 'Mixing', measured_value: 12, unit: 'C', limit_min: null, limit_max: 10, measured_at: new Date().toISOString() },
      ],
    },
  },
  suppliers: {
    suppliers: [] as any[],
    materials: [] as any[],
    evaluations: [] as any[],
    deliveries: [] as any[],
    alerts: [] as any[],
    dashboard: {
      total_suppliers: 6,
      active_suppliers: 5,
      pending_approval: 1,
      high_risk: 1,
    },
  },
  audits: {
    audits: [] as any[],
    attachments: [] as any[],
    stats: { total: 3, by_status: { planned: 1, completed: 1, in_progress: 1 }, by_type: { internal: 2, external: 1 } },
  },
  notifications: [] as any[],
  tokens: new Map<string, any>(),
};

function seedOnce() {
  if ((window as any).__ISO_MOCK_SEEDED__) return;
  (window as any).__ISO_MOCK_SEEDED__ = true;

  // Users
  const admin = {
    id: 1,
    username: 'admin',
    email: 'admin@example.com',
    full_name: 'System Administrator',
    role_id: 1,
    role_name: 'System Administrator',
    status: 'active',
    is_active: true,
    is_verified: true,
    last_login: new Date().toISOString(),
    created_at: new Date().toISOString(),
  };
  const qa = {
    id: 2,
    username: 'qa_manager',
    email: 'qa@example.com',
    full_name: 'QA Manager',
    role_id: 2,
    role_name: 'QA Manager',
    status: 'active',
    is_active: true,
    is_verified: true,
    created_at: new Date().toISOString(),
  };
  db.users = [admin, qa];

  // Documents
  const now = Date.now();
  db.documents = Array.from({ length: 18 }).map((_, i) => ({
    id: i + 1,
    document_number: `DOC-${1000 + i}`,
    title: `Procedure ${i + 1}`,
    description: 'Demo document for ISO 22000',
    document_type: ['procedure', 'policy', 'form', 'work_instruction'][i % 4],
    category: ['haccp', 'prp', 'training', 'audit', 'general'][i % 5],
    status: ['approved', 'draft', 'under_review', 'obsolete'][i % 4],
    version: `${1 + (i % 3)}.0`,
    department: ['Quality Assurance', 'Production', 'Maintenance'][i % 3],
    created_by: 'admin',
    created_at: new Date(now - i * 86400000).toISOString(),
    review_date: new Date(now + (i % 6) * 86400000).toISOString(),
    file_path: `/uploads/documents/demo_${i + 1}.pdf`,
    original_filename: `demo_${i + 1}.pdf`,
  }));
  db.documents.forEach((d) => {
    db.documentVersions.set(d.id, [
      {
        id: Number(`${d.id}01`),
        version_number: d.version,
        file_path: d.file_path,
        original_filename: d.original_filename,
        created_by: d.created_by,
        created_at: d.created_at,
        is_current: true,
      },
    ]);
    db.documentChangeLogs.set(d.id, [
      { id: Number(`${d.id}01`), change_type: 'create', changed_by: d.created_by, created_at: d.created_at },
    ]);
  });

  // HACCP seed
  const contactSurfaces = [
    {
      id: 1,
      name: 'Raw Milk Receiving Line',
      composition: '304 stainless steel piping with sanitary welds',
      description: 'Cold-side surface exposed to inbound raw milk; CIP after each tanker.',
      source: 'Facility fabrication',
      provenance: 'Installed 2022, CIP validation HVAC-22-014',
      point_of_contact: 'Receiving bay to balance tank',
      material: 'Stainless steel',
      main_processing_steps: 'Receiving, filtration',
      packaging_material: 'N/A',
      storage_conditions: 'Wet hold post-CIP',
      shelf_life: '5-year inspection interval',
      possible_inherent_hazards: 'Biofilm, allergen carryover',
      fs_acceptance_criteria: 'ATP <50 RLU, weekly Listeria swab negative',
      created_by: 1,
      created_at: new Date().toISOString(),
    },
    {
      id: 2,
      name: 'Pasteurizer Holding Tube',
      composition: '316 stainless steel tubing with insulation',
      description: 'High heat zone maintaining ≥72°C for 15 seconds.',
      source: 'HTST skid supplier',
      provenance: 'Commissioned 2021',
      point_of_contact: 'Between regenerator outlet and FDV',
      material: 'Stainless steel',
      main_processing_steps: 'Pasteurization',
      packaging_material: 'N/A',
      storage_conditions: 'Hot during production',
      shelf_life: 'Annual integrity test',
      possible_inherent_hazards: 'Under-processing if fouled',
      fs_acceptance_criteria: 'Differential pressure >10 psi',
      created_by: 1,
      created_at: new Date().toISOString(),
    },
    {
      id: 3,
      name: 'Fermentation & Blending Tanks',
      composition: 'Stainless vessels with food-grade seals',
      description: 'Used for yogurt culture fermentation and fruit blending.',
      source: 'FermaMix',
      provenance: 'Separate agitators, CIP recipe FMX-YG-04',
      point_of_contact: 'Post-pasteurization fermentation',
      material: 'Stainless steel',
      main_processing_steps: 'Fermentation, blending',
      packaging_material: 'N/A',
      storage_conditions: 'Closed, 4°C hold',
      shelf_life: 'Seal replacement every 12 months',
      possible_inherent_hazards: 'Post-process contamination',
      fs_acceptance_criteria: 'Environmental swabs <10 CFU/cm²',
      created_by: 1,
      created_at: new Date().toISOString(),
    },
    {
      id: 4,
      name: 'Cheese Vat & Press Surfaces',
      composition: 'Stainless vats, perforated molds, cheesecloth',
      description: 'Direct contact during curd cooking and pressing.',
      source: 'Cheese equipment line',
      provenance: 'Cloths replaced weekly',
      point_of_contact: 'Cheddar production',
      material: 'Stainless steel and cloth',
      main_processing_steps: 'Curd cooking, pressing, brining',
      packaging_material: 'Cheesecloth',
      storage_conditions: 'Humidity-controlled aging room',
      shelf_life: 'Cloths 1 week',
      possible_inherent_hazards: 'Biofilm, salt crystallization',
      fs_acceptance_criteria: 'ATP swabs <25 RLU',
      created_by: 1,
      created_at: new Date().toISOString(),
    },
    {
      id: 5,
      name: 'Butter Churn & Wrapper Table',
      composition: 'Polished stainless churn, HDPE cutting boards',
      description: 'Surfaces used for butter churning and packaging.',
      source: 'Legacy equipment refurbished 2020',
      provenance: 'Gaskets replaced quarterly',
      point_of_contact: 'Butter working and portioning',
      material: 'Stainless steel, HDPE',
      main_processing_steps: 'Churning, portion cutting',
      packaging_material: 'Wax paper',
      storage_conditions: 'Dry between shifts',
      shelf_life: 'HDPE boards rotated every 6 months',
      possible_inherent_hazards: 'Physical chips, allergen smears',
      fs_acceptance_criteria: 'Visual inspection ok, no gouges',
      created_by: 1,
      created_at: new Date().toISOString(),
    },
    {
      id: 6,
      name: 'Grinding & Stuffing Line',
      composition: 'Stainless augers, grinder plates, vacuum hoses',
      description: 'Direct contact for ground beef and chicken.',
      source: 'Meat processing suite',
      provenance: 'Plates sharpened monthly, hoses replaced annually',
      point_of_contact: 'Grinding, mixing, stuffing',
      material: 'Stainless steel, polymer hoses',
      main_processing_steps: 'Grinding, stuffing',
      packaging_material: 'Vacuum bags',
      storage_conditions: 'Disassembled, air-dried',
      shelf_life: 'Hoses 12 months',
      possible_inherent_hazards: 'Metal fragments, pathogen harborage',
      fs_acceptance_criteria: 'Metal detector verification, zero residue',
      created_by: 1,
      created_at: new Date().toISOString(),
    },
    {
      id: 7,
      name: 'Bakery Conveyor & Cooling Racks',
      composition: 'Food-grade mesh belt, anodized racks',
      description: 'Post-bake surfaces for breads and cookies.',
      source: 'Bakery line OEM',
      provenance: 'Belts deep-cleaned weekly',
      point_of_contact: 'Conveying, cooling prior to packaging',
      material: 'Stainless mesh, aluminum',
      main_processing_steps: 'Cooling, inspection',
      packaging_material: 'Paper bags, poly pouches',
      storage_conditions: 'Dry storage',
      shelf_life: 'Belts inspected quarterly',
      possible_inherent_hazards: 'Foreign material, allergen residues',
      fs_acceptance_criteria: 'Pre-op inspection checklist met',
      created_by: 1,
      created_at: new Date().toISOString(),
    },
  ];
  db.haccp.contactSurfaces = contactSurfaces;
  db.haccp.products = [
    { 
      id: 1, 
      product_code: 'P-001', 
      name: 'Yogurt', 
      description: 'Strawberry Yogurt', 
      composition: [
        { material_id: 101, material_code: 'RM-MILK-001', material_name: 'Raw Whole Milk', supplier_name: 'Green Valley Dairy Farm', category: 'raw_materials', percentage: 85, unit: '%', is_high_risk: true },
        { material_id: 102, material_code: 'RM-CULTURE-001', material_name: 'Thermophilic Yogurt Culture', supplier_name: 'Pure Cultures Inc', category: 'ingredients', percentage: 10, unit: '%' },
        { material_id: 103, material_code: 'RM-SUGAR-001', material_name: 'Granulated Cane Sugar', supplier_name: 'Sweet Sugar Co', category: 'ingredients', percentage: 5, unit: '%' }
      ],
      high_risk_ingredients: { material_id: 101, material_code: 'RM-MILK-001', material_name: 'Raw Whole Milk', supplier_name: 'Green Valley Dairy Farm', category: 'raw_materials', is_high_risk: true },
      physical_chemical_biological_description: 'Thick, creamy texture, white with pink tint, pH 4.0-4.5',
      main_processing_steps: 'Milk pasteurization, inoculation, fermentation, straining, flavoring, packaging',
      distribution_serving_methods: 'Refrigerated transport, cold chain maintenance',
      consumer_groups: 'General population, health-conscious consumers',
      storage_conditions: 'Refrigerated 2-4°C',
      shelf_life_days: 21,
      packaging_type: 'Plastic Cup',
      inherent_hazards: 'Bacterial contamination, yeast/mold growth',
      fs_acceptance_criteria: 'Total plate count <100,000 CFU/g, Yeast <100 CFU/g',
      law_regulation_requirement: 'FDA 21 CFR Part 131, Grade A standards',
      haccp_plan_approved: true, 
      haccp_plan_version: '1.2', 
      ccp_count: 2, 
      created_by: 'qa_manager',
      contact_surfaces: contactSurfaces.filter((surface) => [1, 2, 3].includes(surface.id)),
    },
    { 
      id: 2, 
      product_code: 'P-002', 
      name: 'Cheddar', 
      description: 'Cheddar Cheese', 
      composition: [
        { material_id: 101, material_code: 'RM-MILK-001', material_name: 'Raw Whole Milk', supplier_name: 'Green Valley Dairy Farm', category: 'raw_materials', percentage: 90, unit: '%', is_high_risk: true },
        { material_id: 102, material_code: 'RM-CULTURE-001', material_name: 'Thermophilic Yogurt Culture', supplier_name: 'Pure Cultures Inc', category: 'ingredients', percentage: 5, unit: '%' },
        { material_id: 104, material_code: 'RM-REN-001', material_name: 'Microbial Rennet', supplier_name: 'Pure Cultures Inc', category: 'ingredients', percentage: 1, unit: '%' },
        { material_id: 105, material_code: 'RM-SALT-001', material_name: 'Food Grade Sea Salt', supplier_name: 'Sweet Sugar Co', category: 'ingredients', percentage: 4, unit: '%' }
      ],
      high_risk_ingredients: { material_id: 101, material_code: 'RM-MILK-001', material_name: 'Raw Whole Milk', supplier_name: 'Green Valley Dairy Farm', category: 'raw_materials', is_high_risk: true },
      physical_chemical_biological_description: 'Firm texture, orange color, pH 5.1-5.3',
      main_processing_steps: 'Milk pasteurization, acidification, rennet addition, cutting, cooking, pressing, salting, aging',
      distribution_serving_methods: 'Refrigerated transport, temperature-controlled storage',
      consumer_groups: 'General population, cheese lovers',
      storage_conditions: 'Refrigerated 2-4°C',
      shelf_life_days: 90,
      packaging_type: 'Vacuum Pack',
      inherent_hazards: 'Bacterial contamination, mold growth, chemical residues',
      fs_acceptance_criteria: 'Total plate count <1,000,000 CFU/g, Listeria absent',
      law_regulation_requirement: 'FDA 21 CFR Part 133, Grade A standards',
      haccp_plan_approved: false, 
      haccp_plan_version: '0.9', 
      ccp_count: 1, 
      created_by: 'qa_manager',
      contact_surfaces: contactSurfaces.filter((surface) => [1, 4].includes(surface.id)),
    },
    { 
      id: 3, 
      product_code: 'P-003', 
      name: 'Milk', 
      description: 'Whole Milk', 
      composition: [
        { material_id: 101, material_code: 'RM-MILK-001', material_name: 'Raw Whole Milk', supplier_name: 'Green Valley Dairy Farm', category: 'raw_materials', percentage: 100, unit: '%', is_high_risk: true }
      ],
      high_risk_ingredients: { material_id: 101, material_code: 'RM-MILK-001', material_name: 'Raw Whole Milk', supplier_name: 'Green Valley Dairy Farm', category: 'raw_materials', is_high_risk: true },
      physical_chemical_biological_description: 'Liquid, white, homogeneous, pH 6.6-6.8',
      main_processing_steps: 'Raw milk reception, filtration, standardization, pasteurization (72°C/15s), cooling, packaging',
      distribution_serving_methods: 'Refrigerated transport in temperature-controlled vehicles',
      consumer_groups: 'General population, children over 12 months',
      storage_conditions: 'Refrigerated 2-4°C',
      shelf_life_days: 14,
      packaging_type: 'HDPE Bottle',
      inherent_hazards: 'Bacterial contamination (Listeria, Salmonella, E.coli)',
      fs_acceptance_criteria: 'Total plate count <10,000 CFU/ml, Pathogens absent',
      law_regulation_requirement: 'FDA 21 CFR Part 131, Grade A Pasteurized Milk Ordinance',
      haccp_plan_approved: true, 
      haccp_plan_version: '1.0', 
      ccp_count: 2, 
      created_by: 'qa_manager',
      contact_surfaces: contactSurfaces.filter((surface) => [1, 2].includes(surface.id)),
    },
  ];
  db.haccp.flows = [
    { id: 1, product_id: 1, step_number: 1, step_name: 'Receiving', equipment: 'Dock', temperature: 4, time_minutes: 30 },
    { id: 2, product_id: 1, step_number: 2, step_name: 'Mixing', equipment: 'Mixer 1', temperature: 8, time_minutes: 20 },
  ];
  db.haccp.hazards = [
    { id: 1, product_id: 1, process_step_id: 2, hazard_type: 'biological', hazard_name: 'Pathogen growth', description: 'Temperature abuse', likelihood: 2, severity: 3, risk_level: 'medium', risk_score: 6, is_controlled: true, is_ccp: true },
  ];
  db.haccp.ccps = [
    { id: 1, product_id: 1, hazard_id: 1, ccp_number: 'CCP-1', ccp_name: 'Mix temp', description: 'Maintain below 10C', status: 'active', critical_limit_min: null, critical_limit_max: 10, critical_limit_unit: 'C' },
  ];

  // Suppliers seed
  db.suppliers.suppliers = Array.from({ length: 8 }).map((_, i) => ({
    id: i + 1,
    name: `Supplier ${i + 1}`,
    supplier_type: ['raw_material', 'packaging'][i % 2],
    status: ['active', 'pending', 'suspended'][i % 3],
    risk_level: ['low', 'medium', 'high'][i % 3],
    created_at: new Date().toISOString(),
  }));
  db.suppliers.materials = Array.from({ length: 12 }).map((_, i) => ({
    id: i + 1,
    name: `Material ${i + 1}`,
    category: ['dairy', 'fruit', 'packaging'][i % 3],
    approval_status: ['approved', 'pending', 'rejected'][i % 3],
    supplier_id: (i % 8) + 1,
  }));
  db.suppliers.evaluations = [];
  db.suppliers.deliveries = [];

  // Audits seed
  db.audits.audits = [
    { id: 1, title: 'Q1 Internal Audit', audit_type: 'internal', status: 'planned', auditee_department: 'Production', start_date: '2025-09-01', end_date: '2025-09-03' },
    { id: 2, title: 'Supplier A Audit', audit_type: 'supplier', status: 'in_progress', auditee_department: 'Supplier', start_date: '2025-08-15' },
    { id: 3, title: 'External Certification', audit_type: 'external', status: 'completed', auditee_department: 'QA', start_date: '2025-07-10', end_date: '2025-07-11' },
  ];
}

function paginate<T>(items: T[], page = 1, size = 10) {
  const total = items.length;
  const pages = Math.ceil(total / size) || 1;
  const start = (page - 1) * size;
  return { items: items.slice(start, start + size), page, size, total, pages };
}

function ok(data: any) {
  return [200, { success: true, data }];
}

function blobOk(data: Blob) {
  return [200, data];
}

function parseQuery(url: string) {
  const q = url.split('?')[1];
  const params = new URLSearchParams(q || '');
  const out: Record<string, any> = {};
  params.forEach((v, k) => (out[k] = v));
  return out;
}

export async function initMockBackend() {
  seedOnce();

  // Mock on our configured axios instance and also base axios for refresh
  const mock = new AxiosMockAdapter(api, { delayResponse: 300 });
  const mockRaw = new AxiosMockAdapter(axios, { delayResponse: 300 });

  // Auth
  mock.onPost(/\/auth\/login$/).reply((config) => {
    const body = config.data instanceof URLSearchParams ? Object.fromEntries((config.data as any).entries()) : {};
    const username = (body as any).username || 'admin';
    const user = db.users.find((u) => u.username === username) || db.users[0];
    const token = btoa(JSON.stringify({ sub: String(user.id), exp: Math.floor(Date.now() / 1000) + 3600 })) + '.xx.yy';
    const refresh = btoa(JSON.stringify({ sub: String(user.id), exp: Math.floor(Date.now() / 1000) + 7 * 86400 })) + '.aa.bb';
    db.tokens.set(refresh, { userId: user.id });
    return ok({ user, access_token: token, refresh_token: refresh });
  });
  mock.onPost(/\/auth\/logout$/).reply(ok.bind(null, { message: 'ok' } as any));
  mock.onGet(/\/auth\/me$/).reply((config) => {
    const auth = config.headers?.Authorization as string;
    const sub = auth ? JSON.parse(atob(auth.replace('Bearer ', '').split('.')[0] || 'e30='))?.sub : '1';
    const user = db.users.find((u) => String(u.id) === String(sub)) || db.users[0];
    return ok(user);
  });
  mockRaw.onPost(new RegExp(`${(process.env.REACT_APP_API_URL || '/api/v1').replace(/[.*+?^${}()|[\]\\]/g, '\\$&')}/auth/refresh$`)).reply((config) => {
    const payload = JSON.parse(config.data || '{}');
    const data = db.tokens.get(payload.refresh_token);
    const user = db.users.find((u) => u.id === data?.userId) || db.users[0];
    const token = btoa(JSON.stringify({ sub: String(user.id), exp: Math.floor(Date.now() / 1000) + 3600 })) + '.xx.yy';
    const refresh = payload.refresh_token;
    return ok({ access_token: token, refresh_token: refresh });
  });

  // Users
  mock.onGet(/\/users\/?(\?.*)?$/).reply((config) => {
    const params = parseQuery(config.url || '');
    let items = [...db.users];
    if (params.search) items = items.filter((u) => (u.full_name || u.username).toLowerCase().includes(String(params.search).toLowerCase()));
    const page = Number(params.page || 1);
    const size = Number(params.size || 10);
    return ok(paginate(items, page, size));
  });
  mock.onGet(/\/users\/\d+$/).reply((config) => {
    const id = Number((config.url || '').split('/').pop());
    const user = db.users.find((u) => u.id === id);
    return user ? ok(user) : [404, { detail: 'Not found' }];
  });
  mock.onPost(/\/users\/?$/).reply((config) => {
    const body = JSON.parse(config.data || '{}');
    const id = Math.max(0, ...db.users.map((u) => u.id)) + 1;
    const user = { id, status: 'active', is_active: true, is_verified: true, created_at: new Date().toISOString(), ...body };
    db.users.unshift(user);
    return ok(user);
  });
  mock.onPut(/\/users\/\d+$/).reply((config) => {
    const id = Number((config.url || '').split('/').pop());
    const idx = db.users.findIndex((u) => u.id === id);
    const patch = JSON.parse(config.data || '{}');
    if (idx >= 0) db.users[idx] = { ...db.users[idx], ...patch };
    return ok(db.users[idx]);
  });
  mock.onDelete(/\/users\/\d+$/).reply((config) => {
    const id = Number((config.url || '').split('/').pop());
    db.users = db.users.filter((u) => u.id !== id);
    return ok({ message: 'deleted' });
  });

  // Documents
  mock.onGet(/\/documents(\?.*)?$/).reply((config) => {
    const params = parseQuery(config.url || '');
    let items = [...db.documents];
    const search = (params.search || '').toString().toLowerCase();
    if (search) items = items.filter((d) => (d.title || '').toLowerCase().includes(search) || (d.document_number || '').toLowerCase().includes(search));
    ['category', 'status', 'document_type', 'department'].forEach((f) => {
      if (params[f]) items = items.filter((d: any) => String(d[f]) === String(params[f]));
    });
    const page = Number(params.page || 1);
    const size = Number(params.size || 10);
    return ok(paginate(items, page, size));
  });
  mock.onGet(/\/documents\/\d+$/).reply((config) => {
    const id = Number((config.url || '').split('/').pop());
    const doc = db.documents.find((d) => d.id === id);
    return doc ? ok(doc) : [404, { detail: 'Not found' }];
  });
  mock.onPost(/\/documents$/).reply((config) => {
    const id = Math.max(0, ...db.documents.map((d) => d.id)) + 1;
    const now = new Date().toISOString();
    const doc = { id, document_number: `DOC-${1000 + id}`, title: `New Document ${id}`, document_type: 'procedure', category: 'general', status: 'draft', version: '1.0', created_by: 'admin', created_at: now, review_date: null };
    db.documents.unshift(doc);
    db.documentVersions.set(id, [{ id: Number(`${id}01`), version_number: '1.0', file_path: `/uploads/documents/new_${id}.pdf`, original_filename: `new_${id}.pdf`, created_by: 'admin', created_at: now, is_current: true }]);
    db.documentChangeLogs.set(id, [{ id: Number(`${id}01`), change_type: 'create', changed_by: 'admin', created_at: now }]);
    return ok(doc);
  });
  mock.onPut(/\/documents\/\d+$/).reply((config) => {
    const id = Number((config.url || '').split('/').pop());
    const idx = db.documents.findIndex((d) => d.id === id);
    const patch = {}; // multipart ignored in mock
    if (idx >= 0) db.documents[idx] = { ...db.documents[idx], ...patch, updated_at: new Date().toISOString() };
    return ok(db.documents[idx]);
  });
  mock.onDelete(/\/documents\/\d+$/).reply((config) => {
    const id = Number((config.url || '').split('/').pop());
    db.documents = db.documents.filter((d) => d.id !== id);
    db.documentVersions.delete(id);
    db.documentChangeLogs.delete(id);
    return ok({ message: 'deleted' });
  });
  mock.onGet(/\/documents\/stats\/overview$/).reply(() => {
    const total = db.documents.length;
    const byStatus: Record<string, number> = {};
    const byType: Record<string, number> = {};
    const byCat: Record<string, number> = {};
    db.documents.forEach((d) => {
      byStatus[d.status] = (byStatus[d.status] || 0) + 1;
      byType[d.document_type] = (byType[d.document_type] || 0) + 1;
      byCat[d.category] = (byCat[d.category] || 0) + 1;
    });
    const expired = db.documents.filter((d) => d.status !== 'obsolete' && d.review_date && new Date(d.review_date) < new Date()).length;
    const pending = byStatus['under_review'] || 0;
    return ok({
      total_documents: total,
      documents_by_status: byStatus,
      documents_by_type: byType,
      documents_by_category: byCat,
      expired_documents: expired,
      documents_requiring_approval: pending,
    });
  });
  mock.onGet(/\/documents\/\d+\/versions$/).reply((config) => {
    const id = Number((config.url || '').split('/')[2]);
    return ok({ versions: db.documentVersions.get(id) || [] });
  });
  mock.onGet(/\/documents\/\d+\/change-log$/).reply((config) => {
    const id = Number((config.url || '').split('/')[2]);
    return ok({ changes: db.documentChangeLogs.get(id) || [] });
  });
  mock.onGet(/\/documents\/\d+\/download$/).reply(() => {
    const blob = new Blob(['Demo PDF content'], { type: 'application/pdf' });
    return blobOk(blob);
  });
  mock.onPost(/\/documents\/bulk\/status$/).reply(ok.bind(null, { updated: true } as any));
  mock.onPost(/\/documents\/maintenance\/archive-obsolete$/).reply(ok.bind(null, { archived: true } as any));
  mock.onGet(/\/documents\/approvals\/pending$/).reply(() => {
    // Create a couple of pending approvals referencing docs
    const items = db.documents.filter((d) => d.status === 'under_review').slice(0, 3).map((d, i) => ({ id: i + 1, document_id: d.id, document_title: d.title, created_at: new Date().toISOString() }));
    return ok(items);
  });
  mock.onGet(/\/documents\/approval-users$/).reply(() => ok(db.users.map((u) => ({ id: u.id, username: u.username, full_name: u.full_name, email: u.email }))));
  mock.onPost(/\/documents\/\d+\/approvals$/).reply(ok.bind(null, { submitted: true } as any));
  mock.onPost(/\/documents\/\d+\/approvals\/\d+\/approve$/).reply((config) => ok({ approved: true }));
  mock.onPost(/\/documents\/\d+\/approvals\/\d+\/reject$/).reply((config) => ok({ rejected: true }));
  mock.onPost(/\/documents\/\d+\/status\/(obsolete|archive|activate)$/).reply((config) => {
    const parts = (config.url || '').split('/');
    const id = Number(parts[2]);
    const action = parts[4];
    const idx = db.documents.findIndex((d) => d.id === id);
    if (idx >= 0) {
      if (action === 'obsolete') db.documents[idx].status = 'obsolete';
      if (action === 'archive') db.documents[idx].status = 'archived';
      if (action === 'activate') db.documents[idx].status = 'approved';
    }
    return ok(db.documents[idx]);
  });
  mock.onPost(/\/documents\/export$/).reply(() => blobOk(new Blob(['demo'], { type: 'application/pdf' })));
  mock.onGet(/\/documents\/\d+\/versions\/\d+\/download$/).reply(() => blobOk(new Blob(['demo'], { type: 'application/pdf' })));

  // Dashboard
  mock.onGet(/\/dashboard\/stats$/).reply(() => ok({ totalUsers: db.users.length, activeUsers: db.users.length, pendingApprovals: (db.documents.filter((d) => d.status === 'under_review').length), openIssues: 0, docTypeCounts: Object.entries(db.documents.reduce((acc: any, d: any) => ((acc[d.document_type] = (acc[d.document_type] || 0) + 1), acc), {})).map(([type, count]) => ({ type, count })) }));
  mock.onGet(/\/dashboard\/recent-activity$/).reply(() => ok({ activities: db.documents.slice(0, 5).map((d, i) => ({ id: i + 1, action: 'Document Updated', title: d.title, timestamp: new Date(Date.now() - i * 3600 * 1000).toISOString() })) }));

  // HACCP
  mock.onGet(/\/haccp\/products$/).reply(() => ok({ items: db.haccp.products, assigned_only: false }));
  mock.onGet(/\/haccp\/products\/\d+$/).reply((config) => {
    const id = Number((config.url || '').split('/')[3]);
    const product = db.haccp.products.find((p) => p.id === id);
    const flows = db.haccp.flows.filter((f) => f.product_id === id);
    const hazards = db.haccp.hazards.filter((h) => h.product_id === id);
    const ccps = db.haccp.ccps.filter((c) => c.product_id === id);
    return product
      ? ok({
          ...product,
          process_flows: flows,
          hazards,
          ccps,
          oprps: [],
        })
      : [404, { detail: 'Not found' }];
  });
  mock.onPost(/\/haccp\/products$/).reply((config) => {
    const body = JSON.parse(config.data || '{}');
    const id = Math.max(0, ...db.haccp.products.map((p) => p.id)) + 1;
    const { contact_surface_ids = [], ...rest } = body;
    const contact_surfaces = db.haccp.contactSurfaces.filter((surface) => contact_surface_ids.includes(surface.id));
    const product = {
      id,
      ccp_count: 0,
      created_by: 'qa_manager',
      created_at: new Date().toISOString(),
      haccp_plan_approved: false,
      haccp_plan_version: '1.0',
      contact_surfaces,
      ...rest,
    };
    db.haccp.products.unshift(product);
    return ok(product);
  });
  mock.onPut(/\/haccp\/products\/\d+$/).reply((config) => {
    const id = Number((config.url || '').split('/')[3]);
    const idx = db.haccp.products.findIndex((p) => p.id === id);
    const patch = JSON.parse(config.data || '{}');
    if (idx >= 0) {
      const { contact_surface_ids, ...rest } = patch;
      let contact_surfaces = db.haccp.products[idx].contact_surfaces || [];
      if (Array.isArray(contact_surface_ids)) {
        contact_surfaces = db.haccp.contactSurfaces.filter((surface) => contact_surface_ids.includes(surface.id));
      }
      db.haccp.products[idx] = { ...db.haccp.products[idx], ...rest, contact_surfaces };
    }
    return ok(db.haccp.products[idx]);
  });
  mock.onDelete(/\/haccp\/products\/\d+$/).reply((config) => {
    const id = Number((config.url || '').split('/')[3]);
    db.haccp.products = db.haccp.products.filter((p) => p.id !== id);
    db.haccp.flows = db.haccp.flows.filter((f) => f.product_id !== id);
    db.haccp.hazards = db.haccp.hazards.filter((h) => h.product_id !== id);
    db.haccp.ccps = db.haccp.ccps.filter((c) => c.product_id !== id);
    return ok({ message: 'deleted' });
  });
  // process flows
  mock.onPost(/\/haccp\/products\/\d+\/process-flows$/).reply((config) => {
    const productId = Number((config.url || '').split('/')[3]);
    const body = JSON.parse(config.data || '{}');
    const id = Math.max(0, ...db.haccp.flows.map((f) => f.id)) + 1;
    const flow = { id, product_id: productId, ...body };
    db.haccp.flows.push(flow);
    return ok(flow);
  });
  mock.onPut(/\/haccp\/process-flows\/\d+$/).reply((config) => {
    const id = Number((config.url || '').split('/')[3]);
    const idx = db.haccp.flows.findIndex((f) => f.id === id);
    const patch = JSON.parse(config.data || '{}');
    if (idx >= 0) db.haccp.flows[idx] = { ...db.haccp.flows[idx], ...patch };
    return ok(db.haccp.flows[idx]);
  });
  mock.onDelete(/\/haccp\/process-flows\/\d+$/).reply((config) => {
    const id = Number((config.url || '').split('/')[3]);
    db.haccp.flows = db.haccp.flows.filter((f) => f.id !== id);
    return ok({ message: 'deleted' });
  });
  // hazards
  mock.onPost(/\/haccp\/products\/\d+\/hazards$/).reply((config) => {
    const productId = Number((config.url || '').split('/')[3]);
    const body = JSON.parse(config.data || '{}');
    const id = Math.max(0, ...db.haccp.hazards.map((h) => h.id)) + 1;
    const hazard = { id, product_id: productId, risk_level: 'medium', risk_score: 6, ...body };
    db.haccp.hazards.push(hazard);
    return ok(hazard);
  });
  mock.onPut(/\/haccp\/hazards\/\d+$/).reply((config) => {
    const id = Number((config.url || '').split('/')[3]);
    const idx = db.haccp.hazards.findIndex((h) => h.id === id);
    const patch = JSON.parse(config.data || '{}');
    if (idx >= 0) db.haccp.hazards[idx] = { ...db.haccp.hazards[idx], ...patch };
    return ok(db.haccp.hazards[idx]);
  });
  mock.onDelete(/\/haccp\/hazards\/\d+$/).reply((config) => {
    const id = Number((config.url || '').split('/')[3]);
    db.haccp.hazards = db.haccp.hazards.filter((h) => h.id !== id);
    return ok({ message: 'deleted' });
  });
  // ccps
  mock.onPost(/\/haccp\/products\/\d+\/ccps$/).reply((config) => {
    const productId = Number((config.url || '').split('/')[3]);
    const body = JSON.parse(config.data || '{}');
    const id = Math.max(0, ...db.haccp.ccps.map((c) => c.id)) + 1;
    const ccp = { id, product_id: productId, status: 'active', ...body };
    db.haccp.ccps.push(ccp);
    return ok(ccp);
  });
  mock.onPut(/\/haccp\/ccps\/\d+$/).reply((config) => {
    const id = Number((config.url || '').split('/')[3]);
    const idx = db.haccp.ccps.findIndex((c) => c.id === id);
    const patch = JSON.parse(config.data || '{}');
    if (idx >= 0) db.haccp.ccps[idx] = { ...db.haccp.ccps[idx], ...patch };
    return ok(db.haccp.ccps[idx]);
  });
  mock.onDelete(/\/haccp\/ccps\/\d+$/).reply((config) => {
    const id = Number((config.url || '').split('/')[3]);
    db.haccp.ccps = db.haccp.ccps.filter((c) => c.id !== id);
    return ok({ message: 'deleted' });
  });
  mock.onGet(/\/haccp\/dashboard$/).reply(() => ok(db.haccp.dashboard));
  mock.onGet(/\/haccp\/contact-surfaces(\?.*)?$/).reply((config) => {
    const params = parseQuery(config.url || '');
    let items = [...db.haccp.contactSurfaces];
    if (params.q) {
      const term = String(params.q).toLowerCase();
      items = items.filter((surface) => surface.name.toLowerCase().includes(term));
    }
    return ok({ items, count: items.length });
  });
  mock.onPost(/\/haccp\/contact-surfaces$/).reply((config) => {
    const body = JSON.parse(config.data || '{}');
    const id = Math.max(0, ...db.haccp.contactSurfaces.map((s) => s.id)) + 1;
    const surface = { id, created_by: 1, created_at: new Date().toISOString(), ...body };
    db.haccp.contactSurfaces.push(surface);
    return ok(surface);
  });

  // Suppliers
  mock.onGet(/\/suppliers\/dashboard\/stats$/).reply(() => ok(db.suppliers.dashboard));
  mock.onGet(/\/suppliers\/?(\?.*)?$/).reply((config) => {
    const params = parseQuery(config.url || '');
    let items = [...db.suppliers.suppliers];
    if (params.search) items = items.filter((s) => s.name.toLowerCase().includes(String(params.search).toLowerCase()));
    return ok(paginate(items, Number(params.page || 1), Number(params.size || 10)));
  });
  mock.onGet(/\/suppliers\/materials(\?.*)?$/).reply(() => ok(paginate(db.suppliers.materials, 1, 10)));
  mock.onGet(/\/suppliers\/evaluations(\?.*)?$/).reply(() => ok(paginate(db.suppliers.evaluations, 1, 10)));
  mock.onGet(/\/suppliers\/deliveries(\?.*)?$/).reply(() => ok(paginate(db.suppliers.deliveries, 1, 10)));

  // Audits
  mock.onGet(/\/audits(\?.*)?$/).reply(() => ok({ items: db.audits.audits }));
  mock.onPost(/\/audits$/).reply((config) => {
    const body = JSON.parse(config.data || '{}');
    const id = Math.max(0, ...db.audits.audits.map((a) => a.id)) + 1;
    const row = { id, ...body };
    db.audits.audits.unshift(row);
    return ok(row);
  });
  mock.onPut(/\/audits\/\d+$/).reply((config) => {
    const id = Number((config.url || '').split('/')[2]);
    const idx = db.audits.audits.findIndex((a) => a.id === id);
    const patch = JSON.parse(config.data || '{}');
    if (idx >= 0) db.audits.audits[idx] = { ...db.audits.audits[idx], ...patch };
    return ok(db.audits.audits[idx]);
  });
  mock.onDelete(/\/audits\/\d+$/).reply((config) => {
    const id = Number((config.url || '').split('/')[2]);
    db.audits.audits = db.audits.audits.filter((a) => a.id !== id);
    return ok({ message: 'deleted' });
  });
  mock.onGet(/\/audits\/stats$/).reply(() => ok(db.audits.stats));
  mock.onGet(/\/audits\/\d+\/attachments$/).reply(() => ok([]));
  mock.onDelete(/\/audits\/checklist\/attachments\/\d+$/).reply(ok.bind(null, { message: 'deleted' } as any));
  mock.onDelete(/\/audits\/attachments\/\d+$/).reply(ok.bind(null, { message: 'deleted' } as any));
  mock.onPost(/\/audits\/export$/).reply(() => blobOk(new Blob(['audits'], { type: 'application/pdf' })));
  mock.onGet(/\/audits\/\d+\/report$/).reply(() => blobOk(new Blob(['report'], { type: 'application/pdf' })));

  // Notifications
  mock.onGet(/\/notifications(\?.*)?$/).reply(() => ok({ items: db.notifications }));
  mock.onGet(/\/notifications\/unread/).reply(() => ok([]));
  mock.onPut(/\/notifications\/\d+\/read$/).reply(ok.bind(null, { message: 'ok' } as any));
  mock.onPut(/\/notifications\/read-all$/).reply(ok.bind(null, { message: 'ok' } as any));
  mock.onDelete(/\/notifications\/\d+$/).reply(ok.bind(null, { message: 'ok' } as any));
  mock.onDelete(/\/notifications\/clear-read$/).reply(ok.bind(null, { message: 'ok' } as any));

  // Settings
  mock.onGet(/\/settings$/).reply(200, { success: true, data: [{ key: 'timezone', value: 'UTC' }] });
  mock.onPut(/\/settings\/.+$/).reply(200, { success: true, data: { updated: true } });
  mock.onPost(/\/settings\/initialize$/).reply(200, { success: true, data: { initialized: true } });
  mock.onPost(/\/settings\/reset\/.+$/).reply(200, { success: true, data: { reset: true } });
  mock.onGet(/\/settings\/export\/json$/).reply(200, { success: true, data: { settings: [] } });
  mock.onPost(/\/settings\/import\/json$/).reply(200, { success: true, data: { imported: true } });
  mock.onGet(/\/settings\/system-info$/).reply(200, { success: true, data: { version: 'demo', uptime: '99.99%' } });
  mock.onGet(/\/settings\/backup-status$/).reply(200, { success: true, data: { last_backup: new Date().toISOString(), status: 'ok' } });

  // Search
  mock.onGet(/\/search\/smart$/).reply((config) => {
    const params = parseQuery(config.url || '');
    const q = (params.q || '').toString().toLowerCase();
    const results = [
      ...db.documents.filter((d) => d.title.toLowerCase().includes(q)).slice(0, 3).map((doc) => ({ id: `doc-${doc.id}`, title: doc.title, description: 'Document', category: 'Documents', path: `/documents/${doc.id}`, priority: 8 })),
      ...db.haccp.products.filter((p) => p.name.toLowerCase().includes(q)).slice(0, 3).map((p) => ({ id: `prod-${p.id}`, title: p.name, description: 'HACCP Product', category: 'HACCP', path: `/haccp/products/${p.id}`, priority: 9 })),
      ...db.suppliers.suppliers.filter((s) => s.name.toLowerCase().includes(q)).slice(0, 3).map((s) => ({ id: `sup-${s.id}`, title: s.name, description: 'Supplier', category: 'Suppliers', path: `/suppliers`, priority: 7 })),
    ];
    return [200, { success: true, data: { results } }];
  });

  // Traceability minimal
  mock.onGet(/\/traceability\/dashboard\/enhanced$/).reply(200, { success: true, data: { batches_today: 2, recalls_open: 0 } });

  // Complaints minimal
  mock.onGet(/\/complaints(\/.+)?$/).reply((config) => {
    const path = config.url || '';
    if (/\/complaints\/$/.test(path) || /\/complaints\?$/.test(path) || /\/complaints$/.test(path)) {
      return [200, { success: true, data: { items: [] } }];
    }
    return [200, { success: true, data: {} }];
  });
}

export type { AxiosMockAdapter };








