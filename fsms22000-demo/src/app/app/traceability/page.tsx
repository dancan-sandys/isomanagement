"use client";
import DataTable from "@/components/DataTable";
import CrudForm from "@/components/CrudForm";
import { useCrudCreate, useCrudList } from "@/lib/hooks";

type Batch = { id: string; type: string; code: string; productName?: string };

export default function TraceabilityPage() {
  const list = useCrudList<Batch>("batches", { limit: 100 });
  const create = useCrudCreate<Partial<Batch>>("batches");

  return (
    <div className="grid gap-6">
      <h1 className="text-2xl font-semibold">Traceability & Recall</h1>
      <div className="grid md:grid-cols-3 gap-4">
        <div className="md:col-span-2">
          <DataTable
            columns={[{ key: "type", header: "Type" }, { key: "code", header: "Batch Code" }, { key: "productName", header: "Product" }]}
            rows={list.data?.items || []}
          />
        </div>
        <div className="rounded border bg-white p-4">
          <div className="font-medium mb-2">Register Batch</div>
          <CrudForm
            defaultValues={{ type: "finalProduct" }}
            fields={[{ name: "type", label: "Type" }, { name: "code", label: "Code" }, { name: "productName", label: "Product" }]}
            onSubmit={async (d: Partial<Batch>) => create.mutate(d)}
          />
        </div>
      </div>
    </div>
  );
}


