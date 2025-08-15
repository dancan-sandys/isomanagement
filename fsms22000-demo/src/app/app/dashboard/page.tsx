"use client";
import { useCrudList } from "@/lib/hooks";
import { PieChart, Pie, Cell, ResponsiveContainer, LineChart, CartesianGrid, XAxis, YAxis, Tooltip, Legend, Line } from "recharts";

type Doc = { id: string; title?: string; version?: string } & Record<string, unknown>;

type NC = { id: string; status: string } & Record<string, unknown>;

type Complaint = { id: string; createdAt?: string } & Record<string, unknown>;

export default function DashboardPage() {
  const docs = useCrudList<Doc>("documents", { limit: 5 });
  const nc = useCrudList<NC>("ncCapa", { limit: 100 });
  const complaints = useCrudList<Complaint>("complaints", { limit: 100 });

  const statusCounts = (nc.data?.items || []).reduce<Record<string, number>>((acc, n) => {
    acc[n.status] = (acc[n.status] || 0) + 1;
    return acc;
  }, {});

  const pieData = Object.entries(statusCounts).map(([name, value]) => ({ name, value }));
  const colors = ["#0ea5e9", "#22c55e", "#ef4444", "#f59e0b"]; 

  const complaintsMonthly = (complaints.data?.items || []).map((c) => ({ month: (c.createdAt || "").slice(0, 7), count: 1 }))
    .reduce<Record<string, number>>((acc, r) => {
      acc[r.month] = (acc[r.month] || 0) + 1; return acc;
    }, {} as Record<string, number>);
  const lineData = Object.entries(complaintsMonthly).map(([month, count]) => ({ month, count }));

  return (
    <div className="grid gap-6">
      <h1 className="text-2xl font-semibold">FSMS Overview</h1>
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
        <div className="rounded border bg-white p-4">
          <div className="font-medium mb-2">NC/CAPA Status</div>
          <div className="h-60">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie data={pieData} dataKey="value" nameKey="name" outerRadius={90}>
                  {pieData.map((_, idx) => (
                    <Cell key={idx} fill={colors[idx % colors.length]} />
                  ))}
                </Pie>
                <Legend />
              </PieChart>
            </ResponsiveContainer>
          </div>
        </div>
        <div className="rounded border bg-white p-4">
          <div className="font-medium mb-2">Complaints per Month</div>
          <div className="h-60">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={lineData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="month" />
                <YAxis allowDecimals={false} />
                <Tooltip />
                <Line dataKey="count" stroke="#0ea5e9" />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </div>
        <div className="rounded border bg-white p-4">
          <div className="font-medium mb-2">Documents (latest)</div>
          <ul className="text-sm space-y-1">
            {(docs.data?.items || []).map((d) => (
              <li key={d.id} className="flex justify-between">
                <span>{d.title}</span>
                <span className="text-slate-500">{d.version}</span>
              </li>
            ))}
          </ul>
        </div>
      </div>
    </div>
  );
}


