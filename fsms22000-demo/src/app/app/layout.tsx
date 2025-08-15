export default function AppLayout({ children }: { children: React.ReactNode }) {
  const nav = [
    { href: "/app/dashboard", label: "Dashboard" },
    { href: "/app/documents", label: "Documents" },
    { href: "/app/haccp", label: "HACCP" },
    { href: "/app/prp", label: "PRP" },
    { href: "/app/traceability", label: "Traceability" },
    { href: "/app/suppliers", label: "Suppliers" },
    { href: "/app/nc-capa", label: "NC/CAPA" },
    { href: "/app/audits", label: "Audits" },
    { href: "/app/training", label: "Training" },
    { href: "/app/risks", label: "Risks" },
    { href: "/app/management-review", label: "Mgmt Review" },
    { href: "/app/equipment", label: "Equipment" },
    { href: "/app/allergens", label: "Allergens" },
    { href: "/app/complaints", label: "Complaints" },
  ];
  return (
    <div className="grid gap-6">
      <header className="flex items-center justify-between">
        <div className="text-xl font-semibold">FSMS Demo</div>
      </header>
      <nav className="flex flex-wrap gap-2">
        {nav.map((n) => (
          <a key={n.href} className="rounded border bg-white px-3 py-1 text-sm" href={n.href}>
            {n.label}
          </a>
        ))}
      </nav>
      <main>{children}</main>
    </div>
  );
}


