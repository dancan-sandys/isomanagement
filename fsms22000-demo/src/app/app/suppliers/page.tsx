"use client";
import DataTable from "@/components/DataTable";
import CrudForm from "@/components/CrudForm";
import { useCrudCreate, useCrudDelete, useCrudList } from "@/lib/hooks";

type Supplier = { id: string; name: string; score: number };

export default function SuppliersPage() {
  const list = useCrudList<Supplier>("suppliers", { limit: 100, sortBy: "name" });
  const create = useCrudCreate<Partial<Supplier>>("suppliers");
  const del = useCrudDelete("suppliers");

  return (
    <div className="grid gap-6">
      <h1 className="text-2xl font-semibold">Suppliers</h1>
      <div className="grid md:grid-cols-3 gap-4">
        <div className="md:col-span-2">
          <DataTable
            columns={[
              { key: "name", header: "Supplier" },
              { key: "score", header: "Score" },
            ]}
            rows={list.data?.items || []}
            onDelete={(r) => del.mutate(r.id)}
          />
        </div>
        <div className="rounded border bg-white p-4">
          <div className="font-medium mb-2">New Supplier</div>
          <CrudForm
            defaultValues={{ score: 80 }}
            fields={[
              { name: "name", label: "Name" },
              { name: "score", label: "Score", type: "number" },
            ]}
            onSubmit={async (d: Partial<Supplier>) => create.mutate(d)}
          />
        </div>
      </div>
    </div>
  );
}


