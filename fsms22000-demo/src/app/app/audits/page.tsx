"use client";
import DataTable from "@/components/DataTable";
import CrudForm from "@/components/CrudForm";
import { useCrudCreate, useCrudDelete, useCrudList } from "@/lib/hooks";

type Audit = { id: string; type: string; date: string };

export default function AuditsPage() {
  const list = useCrudList<Audit>("audits", { limit: 100 });
  const create = useCrudCreate<Partial<Audit>>("audits");
  const del = useCrudDelete("audits");

  return (
    <div className="grid gap-6">
      <h1 className="text-2xl font-semibold">Audits</h1>
      <div className="grid md:grid-cols-3 gap-4">
        <div className="md:col-span-2">
          <DataTable columns={[{ key: "type", header: "Type" }, { key: "date", header: "Date" }]} rows={list.data?.items || []} onDelete={(r) => del.mutate(r.id)} />
        </div>
        <div className="rounded border bg-white p-4">
          <div className="font-medium mb-2">Plan Audit</div>
          <CrudForm defaultValues={{ type: "internal", date: new Date().toISOString().slice(0, 10) }} fields={[{ name: "type", label: "Type" }, { name: "date", label: "Date", type: "date" }]} onSubmit={async (d: Partial<Audit>) => create.mutate(d)} />
        </div>
      </div>
    </div>
  );
}


