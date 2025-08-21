import React, { useMemo, useRef, useState } from 'react';
import { Box, Stack, Typography, Paper } from '@mui/material';

type AuditItem = {
  id: number;
  title: string;
  start_date?: string | Date | null;
  end_date?: string | Date | null;
  auditee_department?: string | null;
  lead_auditor_id?: number | null;
  auditor_id?: number | null;
};

export interface AuditGanttProps {
  audits: AuditItem[];
  onUpdateDates?: (auditId: number, startISO?: string, endISO?: string) => Promise<void> | void;
}

function toDate(d?: string | Date | null): Date | null {
  if (!d) return null;
  if (d instanceof Date) return d;
  const s = String(d);
  if (!s) return null;
  const parsed = new Date(s);
  return isNaN(parsed.getTime()) ? null : parsed;
}

function formatISO(date: Date | null): string | undefined {
  if (!date) return undefined;
  const y = date.getUTCFullYear();
  const m = String(date.getUTCMonth() + 1).padStart(2, '0');
  const d = String(date.getUTCDate()).padStart(2, '0');
  return `${y}-${m}-${d}`;
}

export const AuditGantt: React.FC<AuditGanttProps> = ({ audits, onUpdateDates }) => {
  const parsed = useMemo(() => audits.map(a => ({
    ...a,
    _start: toDate(a.start_date) || null,
    _end: toDate(a.end_date) || null,
  })), [audits]);

  const [dragState, setDragState] = useState<{
    auditId: number;
    mode: 'left' | 'right' | null;
    startX: number;
    origStart: Date | null;
    origEnd: Date | null;
  } | null>(null);

  // Compute timeline range
  const { start, end, totalDays } = useMemo(() => {
    let minD: Date | null = null;
    let maxD: Date | null = null;
    parsed.forEach(a => {
      if (a._start && (!minD || a._start < minD)) minD = a._start;
      if (a._end && (!maxD || a._end > maxD)) maxD = a._end;
    });
    const today = new Date();
    if (!minD) minD = new Date(Date.UTC(today.getUTCFullYear(), today.getUTCMonth(), 1));
    if (!maxD) maxD = new Date(Date.UTC(today.getUTCFullYear(), today.getUTCMonth() + 1, 0));
    // pad a bit
    const paddedStart = new Date(Date.UTC(minD.getUTCFullYear(), minD.getUTCMonth(), minD.getUTCDate() - 3));
    const paddedEnd = new Date(Date.UTC(maxD.getUTCFullYear(), maxD.getUTCMonth(), maxD.getUTCDate() + 3));
    const days = Math.max(1, Math.ceil((paddedEnd.getTime() - paddedStart.getTime()) / (1000 * 60 * 60 * 24)));
    return { start: paddedStart, end: paddedEnd, totalDays: days };
  }, [parsed]);

  const containerRef = useRef<HTMLDivElement>(null);

  const dayToX = (date: Date) => {
    const diff = Math.max(0, Math.min(totalDays, Math.floor((date.getTime() - start.getTime()) / (1000 * 60 * 60 * 24))));
    return (diff / totalDays) * 100; // percent
  };

  const pxToDaysDelta = (px: number) => {
    const el = containerRef.current;
    if (!el) return 0;
    const width = el.clientWidth || 1;
    const percent = px / width;
    return Math.round(percent * totalDays);
  };

  const onMouseMove = (e: React.MouseEvent) => {
    if (!dragState) return;
    e.preventDefault();
    // visual feedback handled by re-render using temporary state? For simplicity, we will commit on mouse up only
  };

  const onMouseUp = async (e: React.MouseEvent) => {
    if (!dragState) return;
    const el = containerRef.current;
    if (!el) { setDragState(null); return; }
    const rect = el.getBoundingClientRect();
    const deltaPx = e.clientX - dragState.startX;
    const deltaDays = pxToDaysDelta(deltaPx);
    let newStart = dragState.origStart ? new Date(dragState.origStart) : null;
    let newEnd = dragState.origEnd ? new Date(dragState.origEnd) : null;
    if (dragState.mode === 'left' && newStart) {
      newStart.setUTCDate(newStart.getUTCDate() + deltaDays);
      // keep start <= end
      if (newEnd && newStart > newEnd) newStart = newEnd;
    }
    if (dragState.mode === 'right' && newEnd) {
      newEnd.setUTCDate(newEnd.getUTCDate() + deltaDays);
      if (newStart && newEnd < newStart) newEnd = newStart;
    }
    setDragState(null);
    if (onUpdateDates) {
      await onUpdateDates(dragState.auditId, formatISO(newStart), formatISO(newEnd));
    }
  };

  const rows = parsed.map(a => {
    const s = a._start || start;
    const e = a._end || start;
    const left = dayToX(s);
    const right = dayToX(e);
    const width = Math.max(0.8, right - left);
    return { a, left, width };
  });

  // header days (sparse - every ~7 days)
  const headerMarks = useMemo(() => {
    const marks: Array<{ x: number; label: string }> = [];
    for (let i = 0; i <= totalDays; i += Math.max(1, Math.floor(totalDays / 6))) {
      const d = new Date(start.getTime());
      d.setUTCDate(d.getUTCDate() + i);
      marks.push({ x: (i / totalDays) * 100, label: `${d.getUTCMonth() + 1}/${d.getUTCDate()}` });
    }
    return marks;
  }, [start, totalDays]);

  return (
    <Box>
      <Stack spacing={1}>
        <Box ref={containerRef} onMouseMove={onMouseMove} onMouseUp={onMouseUp} sx={{ position: 'relative', border: '1px solid #ddd', borderRadius: 1, p: 1, height: 320, overflow: 'hidden', bgcolor: 'background.paper' }}>
          {/* Header timeline */}
          <Box sx={{ position: 'absolute', top: 4, left: 0, right: 0, height: 20 }}>
            {headerMarks.map(m => (
              <Box key={m.x} sx={{ position: 'absolute', left: `${m.x}%`, top: 0, height: '100%', transform: 'translateX(-50%)', color: 'text.secondary', fontSize: 11 }}>{m.label}</Box>
            ))}
          </Box>
          {/* Bars */}
          <Box sx={{ position: 'absolute', top: 28, left: 0, right: 0, bottom: 0 }}>
            {rows.map(({ a, left, width }, idx) => (
              <Box key={a.id} sx={{ position: 'absolute', top: idx * 28, left: 8, right: 8, height: 24 }}>
                {/* Label */}
                <Typography variant="caption" sx={{ position: 'absolute', left: 0, top: 4, width: 220, whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>{a.title}</Typography>
                {/* Bar */}
                <Box sx={{ position: 'absolute', left: `calc(${left}% + 240px)`, width: `calc(${width}% - 10px)`, height: 16, bgcolor: 'primary.main', borderRadius: 1 }}>
                  {/* Left handle */}
                  <Box onMouseDown={(e) => setDragState({ auditId: a.id, mode: 'left', startX: e.clientX, origStart: toDate(a.start_date), origEnd: toDate(a.end_date) })} sx={{ position: 'absolute', left: 0, top: 0, width: 8, height: '100%', bgcolor: 'primary.dark', cursor: 'ew-resize' }} />
                  {/* Right handle */}
                  <Box onMouseDown={(e) => setDragState({ auditId: a.id, mode: 'right', startX: e.clientX, origStart: toDate(a.start_date), origEnd: toDate(a.end_date) })} sx={{ position: 'absolute', right: 0, top: 0, width: 8, height: '100%', bgcolor: 'primary.dark', cursor: 'ew-resize' }} />
                </Box>
              </Box>
            ))}
          </Box>
        </Box>
      </Stack>
    </Box>
  );
};

export default AuditGantt;

