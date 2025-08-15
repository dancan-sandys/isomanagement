"use client";
import { useForm } from "react-hook-form";

export default function CrudForm<T extends Record<string, unknown>>({
  defaultValues,
  fields,
  onSubmit,
  submitText = "Save",
}: {
  defaultValues: Partial<T>;
  fields: Array<{ name: keyof T | string; label: string; type?: string; options?: string[] }>;
  onSubmit: (data: T) => void | Promise<void>;
  submitText?: string;
}) {
  const { register, handleSubmit, reset } = useForm<T>({ defaultValues: defaultValues as T });

  return (
    <form
      className="space-y-3"
      onSubmit={handleSubmit(async (d) => {
        await onSubmit(d as T);
        reset();
      })}
    >
      {fields.map((f) => (
        <div key={String(f.name)} className="grid gap-1">
          <label className="text-sm text-slate-600">{f.label}</label>
          {f.type === "select" ? (
            <select className="rounded border px-3 py-2" {...register(f.name as keyof T)}>
              {(f.options || []).map((opt) => (
                <option key={opt} value={opt}>
                  {opt}
                </option>
              ))}
            </select>
          ) : (
            <input className="rounded border px-3 py-2" type={f.type || "text"} {...register(f.name as keyof T)} />
          )}
        </div>
      ))}
      <button className="rounded border bg-slate-900 text-white px-3 py-2" type="submit">
        {submitText}
      </button>
    </form>
  );
}


