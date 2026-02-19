import React from 'react';

type FishboneCategories = Record<string, string[]>;

interface FishboneDiagramProps {
  problem: string;
  categories: FishboneCategories;
}

// Refined SVG Fishbone (Ishikawa) diagram renderer with improved aesthetics
const FishboneDiagram: React.FC<FishboneDiagramProps> = ({ problem, categories }) => {
  const width = 960;
  const height = 360;
  const spineY = height / 2;
  const spineStartX = 70;
  const spineEndX = width - 140; // leave space for problem box

  const categoryNames = Object.keys(categories || {});
  const topCats = categoryNames.filter((_, idx) => idx % 2 === 0);
  const bottomCats = categoryNames.filter((_, idx) => idx % 2 === 1);

  const maxRows = Math.max(1, Math.max(topCats.length, bottomCats.length));
  const boneGap = Math.max(80, Math.min(140, (spineEndX - spineStartX - 140) / maxRows));
  const boneLength = Math.min(200, Math.max(140, boneGap + 20));

  const wrapText = (text: string, maxChars: number): string[] => {
    if (!text) return [''];
    const words = text.split(' ');
    const lines: string[] = [];
    let line = '';
    words.forEach((w) => {
      if ((line + ' ' + w).trim().length <= maxChars) {
        line = (line + ' ' + w).trim();
      } else {
        if (line) lines.push(line);
        line = w;
      }
    });
    if (line) lines.push(line);
    return lines.slice(0, 3); // cap to avoid overflow
  };

  const categoryColor = (idx: number) => {
    const palette = ['#4C6FFF', '#00BFA6', '#FFB020', '#FF5A5F', '#8C54FF', '#5AB67A'];
    return palette[idx % palette.length];
  };

  const renderCategory = (name: string, index: number, side: 'top' | 'bottom') => {
    const x = spineStartX + 100 + index * boneGap;
    const y1 = spineY;
    const dy = 82;
    const y2 = side === 'top' ? y1 - dy : y1 + dy;
    const color = categoryColor(index);
    const factors = categories[name] || [];

    return (
      <g key={`${name}-${side}`}>
        {/* main bone with subtle arrow */}
        <line x1={x} y1={y1} x2={x + boneLength} y2={y2} stroke={color} strokeWidth={2} />
        <polygon points={`${x + boneLength},${y2} ${x + boneLength - 8},${y2 - (side === 'top' ? -6 : 6)} ${x + boneLength - 8},${y2 - (side === 'top' ? 6 : -6)}`} fill={color} />
        {/* category pill */}
        <rect x={x + boneLength + 6} y={y2 - 12} rx={10} ry={10} width={Math.max(60, name.length * 7 + 16)} height={24} fill={color} opacity={0.12} stroke={color} />
        <text x={x + boneLength + 14} y={y2} fontSize={12} fill={color} dominantBaseline="middle" style={{ fontWeight: 600 }}>{name}</text>
        {/* factor ticks and labels */}
        {factors.map((f, i) => {
          const t = (i + 1) / (factors.length + 1);
          const fx = x + t * boneLength;
          const fy = y1 + t * (y2 - y1);
          const tickLen = 12;
          const nx = fx - tickLen;
          const ny = side === 'top' ? fy - tickLen : fy + tickLen;
          const lines = wrapText(f, 16);
          const baseY = side === 'top' ? ny - 2 - (lines.length - 1) * 12 : ny + 10;
          return (
            <g key={`${name}-f-${i}`}>
              <line x1={fx} y1={fy} x2={nx} y2={ny} stroke="#6B7280" strokeWidth={1.2} />
              {lines.map((ln, li) => (
                <text key={li} x={nx - 4} y={baseY + li * 12} fontSize={11} fill="#374151">{ln}</text>
              ))}
            </g>
          );
        })}
      </g>
    );
  };

  return (
    <svg width="100%" viewBox={`0 0 ${width} ${height}`} role="img" aria-label="Ishikawa Fishbone Diagram">
      <defs>
        <linearGradient id="spineGrad" x1="0" y1="0" x2="1" y2="0">
          <stop offset="0%" stopColor="#1F2937" />
          <stop offset="100%" stopColor="#4B5563" />
        </linearGradient>
        <filter id="shadow" x="-20%" y="-20%" width="140%" height="140%">
          <feDropShadow dx="0" dy="1" stdDeviation="2" floodColor="#000" floodOpacity="0.15" />
        </filter>
      </defs>
      {/* Spine */}
      <line x1={spineStartX} y1={spineY} x2={spineEndX} y2={spineY} stroke="url(#spineGrad)" strokeWidth={3} />
      {/* Problem box with subtle shadow */}
      <g filter="url(#shadow)">
        <rect x={spineEndX} y={spineY - 28} width={140} height={56} rx={8} ry={8} fill="#F3F4F6" stroke="#9CA3AF" />
        <text x={spineEndX + 70} y={spineY} textAnchor="middle" dominantBaseline="middle" fontSize={13} fill="#111827" style={{ fontWeight: 700 }}>{problem}</text>
      </g>
      {/* Categories */}
      {topCats.map((c, i) => renderCategory(c, i, 'top'))}
      {bottomCats.map((c, i) => renderCategory(c, i, 'bottom'))}
    </svg>
  );
};

export default FishboneDiagram;

