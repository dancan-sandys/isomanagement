"use client";
import React from "react";

type Column<T> = {
  key: keyof T | string;
  header: string;
  render?: (row: T) => React.ReactNode;
};

export default function DataTable<T extends { id: string }>({
  columns,
  rows,
  onEdit,
  onDelete,
}: {
  columns: Column<T>[];
  rows: T[];
  onEdit?: (row: T) => void;
  onDelete?: (row: T) => void;
}) {
  return (
    <div className="overflow-x-auto rounded border bg-white">
      <table className="min-w-full text-sm">
        <thead>
          <tr className="bg-slate-100 text-left">
            {columns.map((c) => (
              <th key={String(c.key)} className="px-3 py-2 font-medium">
                {c.header}
              </th>
            ))}
            {(onEdit || onDelete) && <th className="px-3 py-2" />}
          </tr>
        </thead>
        <tbody>
          {rows.map((r) => (
            <tr key={r.id} className="border-t">
              {columns.map((c) => (
                <td key={String(c.key)} className="px-3 py-2">
                  {c.render ? c.render(r) : String((r as unknown as Record<string, unknown>)[c.key as string] ?? "")}
                </td>
              ))}
              {(onEdit || onDelete) && (
                <td className="px-3 py-2 text-right space-x-2">
                  {onEdit && (
                    <button className="rounded border px-2 py-1" onClick={() => onEdit(r)}>
                      Edit
                    </button>
                  )}
                  {onDelete && (
                    <button className="rounded border px-2 py-1 text-red-600" onClick={() => onDelete(r)}>
                      Delete
                    </button>
                  )}
                </td>
              )}
            </tr>
          ))}
          {rows.length === 0 && (
            <tr>
              <td className="px-3 py-10 text-center text-slate-500" colSpan={columns.length + 1}>
                No data
              </td>
            </tr>
          )}
        </tbody>
      </table>
    </div>
  );
}


