"use client";
import DataTable from "@/components/DataTable";
import CrudForm from "@/components/CrudForm";
import { useCrudCreate, useCrudDelete, useCrudList } from "@/lib/hooks";

type PRP = { id: string; name: string; frequency: string };

export default function PRPPage() {
  const list = useCrudList<PRP>("prps", { limit: 100 });
  const create = useCrudCreate<Partial<PRP>>("prps");
  const del = useCrudDelete("prps");

  return (
    <div className="grid gap-6">
      <h1 className="text-2xl font-semibold">PRP Management</h1>
      <div className="grid md:grid-cols-3 gap-4">
        <div className="md:col-span-2">
          <DataTable columns={[{ key: "name", header: "Name" }, { key: "frequency", header: "Frequency" }]} rows={list.data?.items || []} onDelete={(r) => del.mutate(r.id)} />
        </div>
        <div className="rounded border bg-white p-4">
          <div className="font-medium mb-2">New PRP</div>
          <CrudForm
            defaultValues={{ frequency: "daily" }}
            fields={[{ name: "name", label: "Name" }, { name: "frequency", label: "Frequency" }]}
            onSubmit={async (d: Partial<PRP>) => create.mutate(d)}
          />
        </div>
      </div>
    </div>
  );
}


