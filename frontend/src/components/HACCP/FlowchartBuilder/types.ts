// HACCP Flowchart Builder Types
export interface HACCPProcessStep {
  id: string;
  type: HACCPNodeType;
  label: string;
  position: { x: number; y: number };
  data: HACCPNodeData;
}

export interface HACCPFlowConnection {
  id: string;
  source: string;
  target: string;
  label?: string;
  type?: 'straight' | 'smoothstep' | 'step';
}

export enum HACCPNodeType {
  // Start/End nodes
  START = 'start',
  END = 'end',
  
  // Receiving processes
  RAW_MATERIAL_RECEIVING = 'raw_material_receiving',
  INSPECTION = 'inspection',
  
  // Storage processes
  COLD_STORAGE = 'cold_storage',
  DRY_STORAGE = 'dry_storage',
  FREEZER_STORAGE = 'freezer_storage',
  
  // Processing steps
  PASTEURIZATION = 'pasteurization',
  FERMENTATION = 'fermentation',
  HOMOGENIZATION = 'homogenization',
  SEPARATION = 'separation',
  STANDARDIZATION = 'standardization',
  COOLING = 'cooling',
  HEATING = 'heating',
  MIXING = 'mixing',
  FILTRATION = 'filtration',
  CONCENTRATION = 'concentration',
  
  // Packaging processes
  FILLING = 'filling',
  SEALING = 'sealing',
  LABELING = 'labeling',
  CODING = 'coding',
  
  // Quality control
  QUALITY_CHECK = 'quality_check',
  TESTING = 'testing',
  
  // Final processes
  FINAL_PACKAGING = 'final_packaging',
  SHIPPING = 'shipping',
  
  // Decision points
  DECISION = 'decision',
  
  // Rework/Waste
  REWORK = 'rework',
  WASTE = 'waste',
  
  // Custom process
  CUSTOM = 'custom'
}

export interface HACCPNodeData {
  // Basic information
  stepNumber?: number;
  description?: string;
  equipment?: string;
  
  // Process parameters
  temperature?: {
    min?: number;
    max?: number;
    target?: number;
    unit: 'C' | 'F';
  };
  
  time?: {
    duration?: number;
    unit: 'seconds' | 'minutes' | 'hours';
  };
  
  ph?: {
    min?: number;
    max?: number;
    target?: number;
  };
  
  waterActivity?: {
    min?: number;
    max?: number;
    target?: number;
  };
  
  // Hazard information
  hazards?: Array<{
    id: string;
    type: 'biological' | 'chemical' | 'physical' | 'allergen';
    description: string;
    likelihood: number; // 1-5
    severity: number; // 1-5
    riskLevel: 'low' | 'medium' | 'high' | 'critical';
    controlMeasures?: string;
    isCCP?: boolean;
  }>;
  
  // CCP information (if applicable)
  ccp?: {
    number: string;
    criticalLimits: {
      parameter: string;
      min?: number;
      max?: number;
      unit?: string;
    }[];
    monitoringFrequency: string;
    monitoringMethod: string;
    responsiblePerson?: string;
    correctiveActions: string;
    verificationMethod: string;
  };
  
  // Flow control
  isRequired?: boolean;
  alternatives?: string[];
  
  // Custom data for specific node types
  customData?: Record<string, any>;
}

export interface HACCPFlowchart {
  id?: string;
  productId: string;
  productName: string;
  version: string;
  title: string;
  description?: string;
  nodes: HACCPProcessStep[];
  edges: HACCPFlowConnection[];
  metadata: {
    createdBy?: string;
    createdAt?: string;
    updatedBy?: string;
    updatedAt?: string;
    approvedBy?: string;
    approvedAt?: string;
    status: 'draft' | 'review' | 'approved' | 'obsolete';
  };
}

// Predefined process templates for different dairy products
export interface ProductTemplate {
  id: string;
  name: string;
  description: string;
  category: 'milk' | 'yogurt' | 'cheese' | 'butter' | 'ice_cream' | 'custom';
  defaultNodes: HACCPProcessStep[];
  defaultEdges: HACCPFlowConnection[];
}

// Node palette categories for the drag-and-drop interface
export interface NodePaletteCategory {
  id: string;
  name: string;
  icon: string;
  nodes: Array<{
    type: HACCPNodeType;
    label: string;
    icon: string;
    description: string;
    defaultData: Partial<HACCPNodeData>;
  }>;
}
