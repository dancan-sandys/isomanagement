import Link from "next/link";

export default function Home() {
  const modules = [
    { href: "/app/dashboard", label: "Dashboard" },
    { href: "/app/documents", label: "Document Control" },
    { href: "/app/haccp", label: "HACCP Plans" },
    { href: "/app/prp", label: "PRP Management" },
    { href: "/app/traceability", label: "Traceability & Recall" },
    { href: "/app/suppliers", label: "Suppliers & Incoming" },
    { href: "/app/nc-capa", label: "NC/CAPA" },
    { href: "/app/audits", label: "Audits" },
    { href: "/app/training", label: "Training & Competency" },
    { href: "/app/risks", label: "Risk & Opportunities" },
    { href: "/app/management-review", label: "Management Review" },
    { href: "/app/equipment", label: "Equipment & Calibration" },
    { href: "/app/allergens", label: "Allergen & Label Control" },
    { href: "/app/complaints", label: "Complaints" },
  ];
  return (
    <div className="space-y-6">
      <h1 className="text-3xl font-semibold">ISO 22000 FSMS for Dairy Processing</h1>
      <p className="text-slate-600">Demo workspace. Explore modules:</p>
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
        {modules.map((m) => (
          <Link key={m.href} href={m.href} className="rounded border bg-white p-4 hover:shadow">
            <div className="font-medium">{m.label}</div>
            <div className="text-sm text-slate-500">{m.href}</div>
          </Link>
        ))}
      </div>
    </div>
  );
}
