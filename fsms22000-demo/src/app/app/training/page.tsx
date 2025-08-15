"use client";
import DataTable from "@/components/DataTable";
import CrudForm from "@/components/CrudForm";
import { useCrudCreate, useCrudDelete, useCrudList } from "@/lib/hooks";

type Training = { id: string; role: string; title: string };

export default function TrainingPage() {
  const list = useCrudList<Training>("trainings", { limit: 100 });
  const create = useCrudCreate<Partial<Training>>("trainings");
  const del = useCrudDelete("trainings");

  return (
    <div className="grid gap-6">
      <h1 className="text-2xl font-semibold">Training & Competency</h1>
      <div className="grid md:grid-cols-3 gap-4">
        <div className="md:col-span-2">
          <DataTable columns={[{ key: "role", header: "Role" }, { key: "title", header: "Training" }]} rows={list.data?.items || []} onDelete={(r) => del.mutate(r.id)} />
        </div>
        <div className="rounded border bg-white p-4">
          <div className="font-medium mb-2">Add Training</div>
          <CrudForm defaultValues={{ role: "Operator" }} fields={[{ name: "role", label: "Role" }, { name: "title", label: "Title" }]} onSubmit={async (d: Partial<Training>) => create.mutate(d)} />
        </div>
      </div>
    </div>
  );
}


