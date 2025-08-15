"use client";
import ReactFlow, { Background, Controls, MiniMap, addEdge, Connection, Edge, Node, OnNodesChange, OnEdgesChange } from "reactflow";
import "reactflow/dist/style.css";
import { useState, useCallback } from "react";
import { useCrudCreate, useCrudList } from "@/lib/hooks";
import CrudForm from "@/components/CrudForm";

type Plan = { productName: string; flowNodes: Node[]; flowEdges: Edge[] };

export default function HACCPPage() {
  const [nodes, setNodes] = useState<Node[]>([
    { id: "start", data: { label: "Start" }, position: { x: 0, y: 0 } },
  ]);
  const [edges, setEdges] = useState<Edge[]>([]);
  const onConnect = useCallback((params: Edge | Connection) => setEdges((eds) => addEdge(params, eds)), []);

  const onNodesChange: OnNodesChange = () => setNodes((nds) => nds);
  const onEdgesChange: OnEdgesChange = () => setEdges((eds) => eds);

  const plans = useCrudList<Plan & { id: string }>("haccpPlans", { limit: 50 });
  const create = useCrudCreate<Plan>("haccpPlans");

  return (
    <div className="grid gap-6">
      <div>
        <h1 className="text-2xl font-semibold">HACCP Plans</h1>
        <p className="text-slate-600">Build flowcharts and define hazards, CCPs, and controls.</p>
      </div>
      <div className="grid md:grid-cols-3 gap-4">
        <div className="rounded border bg-white h-[420px] md:col-span-2">
          <ReactFlow nodes={nodes} edges={edges} onNodesChange={onNodesChange} onEdgesChange={onEdgesChange} onConnect={onConnect} fitView>
            <MiniMap />
            <Controls />
            <Background />
          </ReactFlow>
        </div>
        <div className="rounded border bg-white p-4">
          <div className="font-medium mb-2">Save Plan</div>
          <CrudForm<Plan>
            defaultValues={{ productName: "Milk", flowNodes: nodes, flowEdges: edges }}
            fields={[{ name: "productName", label: "Product" }]}
            onSubmit={async (d) => {
              await create.mutateAsync({ ...d, flowNodes: nodes, flowEdges: edges });
            }}
          />
          <div className="mt-4">
            <div className="font-medium mb-1 text-sm">Saved Plans</div>
            <ul className="text-sm space-y-1">
              {(plans.data?.items || []).map((p) => (
                <li key={p.id}>{p.productName}</li>
              ))}
            </ul>
          </div>
        </div>
      </div>
    </div>
  );
}


