"use client";
import DataTable from "@/components/DataTable";
import CrudForm from "@/components/CrudForm";
import { useCrudCreate, useCrudDelete, useCrudList } from "@/lib/hooks";

type Equipment = { id: string; name: string; type: string; serial: string; location: string };

export default function EquipmentPage() {
  const list = useCrudList<Equipment>("equipments", { limit: 100 });
  const create = useCrudCreate<Partial<Equipment>>("equipments");
  const del = useCrudDelete("equipments");

  return (
    <div className="grid gap-6">
      <h1 className="text-2xl font-semibold">Equipment & Calibration</h1>
      <div className="grid md:grid-cols-3 gap-4">
        <div className="md:col-span-2">
          <DataTable columns={[{ key: "name", header: "Name" }, { key: "type", header: "Type" }, { key: "serial", header: "Serial" }, { key: "location", header: "Location" }]} rows={list.data?.items || []} onDelete={(r) => del.mutate(r.id)} />
        </div>
        <div className="rounded border bg-white p-4">
          <div className="font-medium mb-2">Add Equipment</div>
          <CrudForm defaultValues={{}} fields={[{ name: "name", label: "Name" }, { name: "type", label: "Type" }, { name: "serial", label: "Serial" }, { name: "location", label: "Location" }]} onSubmit={async (d: Partial<Equipment>) => create.mutate(d)} />
        </div>
      </div>
    </div>
  );
}


