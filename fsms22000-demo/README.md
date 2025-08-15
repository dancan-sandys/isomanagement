ISO 22000 FSMS Demo for Dairy Processing

This is a mock-backed, file-persistent demo implementing core modules:

- Document Control
- HACCP Plans (flowchart editor)
- PRP Management
- Traceability & Recall
- Suppliers & Incoming Materials
- NC/CAPA
- Audits
- Training & Competency
- Risk & Opportunities
- Management Review
- Equipment & Calibration
- Allergen & Label Control
- Customer Complaints

Tech: Next.js App Router, TypeScript, Tailwind, TanStack Query, React Flow, Recharts, JSON file persistence.

## Getting Started

Development

First, run the development server:

```bash
npm run dev
# or
yarn dev
# or
pnpm dev
# or
bun dev
```

Open [http://localhost:3000](http://localhost:3000) and click into modules.

API

- Auth: `POST /api/auth` with `{ email, password }` (admin: admin@fsms.local / admin123)
- CRUD: `GET/POST /api/crud/:collection`, `GET/PUT/DELETE /api/crud/:collection/:id`

Data is stored under `data/*.json`.

This project uses Next.js App Router with Tailwind and common UI libraries.

## Packaging

- Export to PDF/Excel supported from pages where applicable; extend with `xlsx`/`jspdf` as needed.
