"use client";
import DataTable from "@/components/DataTable";
import CrudForm from "@/components/CrudForm";
import { useCrudCreate, useCrudDelete, useCrudList } from "@/lib/hooks";

type NC = { id: string; source: string; description: string; status: string; assignee?: string };

export default function NcCapaPage() {
  const list = useCrudList<NC>("ncCapa", { limit: 100 });
  const create = useCrudCreate<Partial<NC>>("ncCapa");
  const del = useCrudDelete("ncCapa");

  return (
    <div className="grid gap-6">
      <h1 className="text-2xl font-semibold">Non-Conformities & CAPA</h1>
      <div className="grid md:grid-cols-3 gap-4">
        <div className="md:col-span-2">
          <DataTable
            columns={[
              { key: "source", header: "Source" },
              { key: "description", header: "Description" },
              { key: "status", header: "Status" },
              { key: "assignee", header: "Assignee" },
            ]}
            rows={list.data?.items || []}
            onDelete={(r) => del.mutate(r.id)}
          />
        </div>
        <div className="rounded border bg-white p-4">
          <div className="font-medium mb-2">Log NC</div>
          <CrudForm
            defaultValues={{ source: "PRP", status: "Open" }}
            fields={[
              { name: "source", label: "Source" },
              { name: "description", label: "Description" },
              { name: "status", label: "Status" },
              { name: "assignee", label: "Assignee" },
            ]}
            onSubmit={async (d: Partial<NC>) => create.mutate(d)}
          />
        </div>
      </div>
    </div>
  );
}


