
export interface Coin {
  id: string;
  country: string;
  year: string;
  mintMark?: string;
  denomination: string;
  quantity: number;
  series?: string;      // Program/Series
  theme?: string;       // Theme/Subject
  condition: string;
  surfaceQuality?: string; // Surface & Strike Quality
  certification?: {
    service: string;      // Grading Service
    serialNumber: string; // Grading Certification Number
    grade: string;        // Used for internal logic/sorting
  };
  purchaseCost?: number;  // Cost
  datePurchased?: string; // Purchase Date
  retailer?: string;      // Retailer/Website
  retailerItemNo?: string; 
  retailerInvoiceNo?: string;
  metalContent?: string;  // Metal Content
  meltValue?: number;     // Melt Value
  personalNotes?: string; 
  personalRefNo?: string; // Personal Reference #
  storageLocation?: string; // Storage Location
  varietyLegacy?: string; // Variety (Legacy)
  notesLegacy?: string;   // Notes (Legacy)
  
  // Internal/AI/Metadata fields
  dateAdded: string;
  currency: string;
  estimatedValueMin?: number;
  estimatedValueMax?: number;
  faceValueUSD?: number;
  valuationDate?: string;
  valuationNotes?: string;
  sources?: Source[];
  analysis?: string;
  lastInventoried?: string;
  inventoryStatus?: 'ACCOUNTED' | 'MISSING' | 'UNCHECKED';
  inventoryNotes?: string;
  // Tech Specs (Numista style)
  weight?: number;
  diameter?: number;
  thickness?: number;
  purity?: string;
  design?: string;
}

export interface WishlistItem {
  id: string;
  year?: string;
  country: string;
  denomination: string;
  series?: string;
  design?: string;
  targetCondition?: string; 
  maxPrice?: number; 
  notes?: string;
  priority: 'High' | 'Medium' | 'Low';
}

export interface Source {
  title: string;
  uri: string;
}

export enum AppView {
  DASHBOARD = 'DASHBOARD',
  COLLECTION = 'COLLECTION',
  ADD_COINS = 'ADD_COINS',
  INVENTORY = 'INVENTORY',
  WISHLIST = 'WISHLIST'
}

export interface SortConfig {
  key: keyof Coin | 'grade';
  direction: 'asc' | 'desc';
}
