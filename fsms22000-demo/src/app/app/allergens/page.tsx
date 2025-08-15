"use client";
import DataTable from "@/components/DataTable";
import CrudForm from "@/components/CrudForm";
import { useCrudCreate, useCrudDelete, useCrudList } from "@/lib/hooks";

type Allergen = { id: string; productId: string };

export default function AllergensPage() {
  const list = useCrudList<Allergen>("allergens", { limit: 100 });
  const create = useCrudCreate<Partial<Allergen>>("allergens");
  const del = useCrudDelete("allergens");

  return (
    <div className="grid gap-6">
      <h1 className="text-2xl font-semibold">Allergen & Label Control</h1>
      <div className="grid md:grid-cols-3 gap-4">
        <div className="md:col-span-2">
          <DataTable columns={[{ key: "productId", header: "Product" }]} rows={list.data?.items || []} onDelete={(r) => del.mutate(r.id)} />
        </div>
        <div className="rounded border bg-white p-4">
          <div className="font-medium mb-2">New Allergen Assessment</div>
          <CrudForm defaultValues={{}} fields={[{ name: "productId", label: "Product" }]} onSubmit={async (d: Partial<Allergen>) => create.mutate(d)} />
        </div>
      </div>
    </div>
  );
}


