"use client";
import DataTable from "@/components/DataTable";
import CrudForm from "@/components/CrudForm";
import { useCrudCreate, useCrudDelete, useCrudList } from "@/lib/hooks";

type Risk = { id: string; title: string; category: string; severity: number; likelihood: number; detectability: number; status: string };

export default function RisksPage() {
  const list = useCrudList<Risk>("risks", { limit: 100 });
  const create = useCrudCreate<Partial<Risk>>("risks");
  const del = useCrudDelete("risks");

  return (
    <div className="grid gap-6">
      <h1 className="text-2xl font-semibold">Risk & Opportunity Register</h1>
      <div className="grid md:grid-cols-3 gap-4">
        <div className="md:col-span-2">
          <DataTable
            columns={[
              { key: "title", header: "Title" },
              { key: "category", header: "Category" },
              { key: "severity", header: "S" },
              { key: "likelihood", header: "L" },
              { key: "detectability", header: "D" },
              { key: "status", header: "Status" },
            ]}
            rows={list.data?.items || []}
            onDelete={(r) => del.mutate(r.id)}
          />
        </div>
        <div className="rounded border bg-white p-4">
          <div className="font-medium mb-2">New Risk</div>
          <CrudForm
            defaultValues={{ category: "foodSafety", severity: 3, likelihood: 3, detectability: 3, status: "Open" }}
            fields={[
              { name: "title", label: "Title" },
              { name: "category", label: "Category" },
              { name: "severity", label: "Severity", type: "number" },
              { name: "likelihood", label: "Likelihood", type: "number" },
              { name: "detectability", label: "Detectability", type: "number" },
              { name: "status", label: "Status" },
            ]}
            onSubmit={async (d: Partial<Risk>) => create.mutate(d)}
          />
        </div>
      </div>
    </div>
  );
}


