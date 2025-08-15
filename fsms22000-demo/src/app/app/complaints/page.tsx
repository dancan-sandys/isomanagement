"use client";
import DataTable from "@/components/DataTable";
import CrudForm from "@/components/CrudForm";
import { useCrudCreate, useCrudDelete, useCrudList } from "@/lib/hooks";

type Complaint = { id: string; productId: string; type: string; description: string; status: string };

export default function ComplaintsPage() {
  const list = useCrudList<Complaint>("complaints", { limit: 100 });
  const create = useCrudCreate<Partial<Complaint>>("complaints");
  const del = useCrudDelete("complaints");

  return (
    <div className="grid gap-6">
      <h1 className="text-2xl font-semibold">Customer Complaints</h1>
      <div className="grid md:grid-cols-3 gap-4">
        <div className="md:col-span-2">
          <DataTable
            columns={[
              { key: "productId", header: "Product" },
              { key: "type", header: "Type" },
              { key: "description", header: "Description" },
              { key: "status", header: "Status" },
            ]}
            rows={list.data?.items || []}
            onDelete={(r) => del.mutate(r.id)}
          />
        </div>
        <div className="rounded border bg-white p-4">
          <div className="font-medium mb-2">Log Complaint</div>
          <CrudForm
            defaultValues={{ status: "Open" }}
            fields={[
              { name: "productId", label: "Product" },
              { name: "type", label: "Type" },
              { name: "description", label: "Description" },
              { name: "status", label: "Status" },
            ]}
            onSubmit={async (d: Partial<Complaint>) => create.mutate(d)}
          />
        </div>
      </div>
    </div>
  );
}


