"use client";
import DataTable from "@/components/DataTable";
import CrudForm from "@/components/CrudForm";
import { useCrudCreate, useCrudDelete, useCrudList } from "@/lib/hooks";

type Doc = { id: string; title: string; department: string; type: string; version: string; status: string };

export default function DocumentsPage() {
  const list = useCrudList<Doc>("documents", { limit: 100, sortBy: "updatedAt", sortDir: "desc" });
  const create = useCrudCreate<Partial<Doc>>("documents");
  const del = useCrudDelete("documents");

  return (
    <div className="grid gap-6">
      <div>
        <h1 className="text-2xl font-semibold">Document Control</h1>
        <p className="text-slate-600">Upload, track, and approve documents.</p>
      </div>

      <div className="grid md:grid-cols-3 gap-4">
        <div className="md:col-span-2">
          <DataTable
            columns={[
              { key: "title", header: "Title" },
              { key: "department", header: "Department" },
              { key: "type", header: "Type" },
              { key: "version", header: "Version" },
              { key: "status", header: "Status" },
            ]}
            rows={list.data?.items || []}
            onDelete={(r) => del.mutate(r.id)}
          />
        </div>
        <div className="rounded border bg-white p-4">
          <div className="font-medium mb-2">New Document</div>
          <CrudForm
            defaultValues={{ type: "SOP", department: "QA", version: "1.0", status: "Draft" }}
            fields={[
              { name: "title", label: "Title" },
              { name: "department", label: "Department" },
              { name: "type", label: "Type" },
              { name: "version", label: "Version" },
              { name: "status", label: "Status" },
            ]}
            onSubmit={async (d: Partial<Doc>) => create.mutate(d)}
          />
        </div>
      </div>
    </div>
  );
}


