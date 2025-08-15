"use client";
import DataTable from "@/components/DataTable";
import CrudForm from "@/components/CrudForm";
import { useCrudCreate, useCrudDelete, useCrudList } from "@/lib/hooks";

type MR = { id: string; date: string; attendees: string[] };

export default function ManagementReviewPage() {
  const list = useCrudList<MR>("managementReviews", { limit: 100 });
  const create = useCrudCreate<Partial<MR>>("managementReviews");
  const del = useCrudDelete("managementReviews");

  return (
    <div className="grid gap-6">
      <h1 className="text-2xl font-semibold">Management Review</h1>
      <div className="grid md:grid-cols-3 gap-4">
        <div className="md:col-span-2">
          <DataTable
            columns={[
              { key: "date", header: "Date" },
              { key: "attendees", header: "Attendees", render: (r: MR) => (r.attendees || []).join(", ") },
            ]}
            rows={list.data?.items || []}
            onDelete={(r) => del.mutate(r.id)}
          />
        </div>
        <div className="rounded border bg-white p-4">
          <div className="font-medium mb-2">Schedule Review</div>
          <CrudForm
            defaultValues={{ date: new Date().toISOString().slice(0, 10) }}
            fields={[
              { name: "date", label: "Date", type: "date" },
              { name: "attendees", label: "Attendees (comma separated)" },
            ]}
            onSubmit={async (d: Partial<MR>) =>
              create.mutate({
                ...d,
                attendees: String((d as Partial<MR> & { attendees?: string }).attendees || "")
                  .split(",")
                  .map((s) => s.trim())
                  .filter(Boolean),
              })
            }
          />
        </div>
      </div>
    </div>
  );
}


