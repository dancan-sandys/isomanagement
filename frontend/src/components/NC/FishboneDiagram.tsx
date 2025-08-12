import React from 'react';

type FishboneCategories = Record<string, string[]>;

interface FishboneDiagramProps {
  problem: string;
  categories: FishboneCategories;
}

// Simple SVG Fishbone (Ishikawa) diagram renderer.
// Renders a horizontal spine with category bones and factor labels.
const FishboneDiagram: React.FC<FishboneDiagramProps> = ({ problem, categories }) => {
  const width = 900;
  const height = 320;
  const spineY = height / 2;
  const spineStartX = 60;
  const spineEndX = width - 60;

  const categoryNames = Object.keys(categories || {});
  const topCats = categoryNames.filter((_, idx) => idx % 2 === 0);
  const bottomCats = categoryNames.filter((_, idx) => idx % 2 === 1);

  const boneLength = 160;
  const boneGap = Math.max(80, Math.min(120, (spineEndX - spineStartX - 200) / Math.max(1, Math.max(topCats.length, bottomCats.length))));

  const renderCategory = (name: string, index: number, side: 'top' | 'bottom') => {
    const x = spineStartX + 120 + index * boneGap;
    const y1 = spineY;
    const dy = 70;
    const y2 = side === 'top' ? y1 - dy : y1 + dy;

    const factors = categories[name] || [];
    return (
      <g key={`${name}-${side}`}>
        {/* main bone */}
        <line x1={x} y1={y1} x2={x + boneLength} y2={y2} stroke="#555" strokeWidth={2} />
        {/* category label */}
        <text x={x + boneLength + 6} y={y2} fontSize={12} fill="#222" dominantBaseline="middle">{name}</text>
        {/* factor ticks */}
        {factors.map((f, i) => {
          const t = (i + 1) / (factors.length + 1);
          const fx = x + t * boneLength;
          const fy = y1 + t * (y2 - y1);
          const tickLen = 10;
          const nx = side === 'top' ? fx - tickLen : fx - tickLen;
          const ny = side === 'top' ? fy - tickLen : fy + tickLen;
          return (
            <g key={`${name}-f-${i}`}>
              <line x1={fx} y1={fy} x2={nx} y2={ny} stroke="#777" strokeWidth={1.5} />
              <text x={nx - 4} y={side === 'top' ? ny - 4 : ny + 12} fontSize={11} fill="#333">{f}</text>
            </g>
          );
        })}
      </g>
    );
  };

  return (
    <svg width="100%" viewBox={`0 0 ${width} ${height}`} role="img" aria-label="Ishikawa Fishbone Diagram">
      {/* Spine */}
      <line x1={spineStartX} y1={spineY} x2={spineEndX} y2={spineY} stroke="#333" strokeWidth={3} />
      {/* Problem box at right */}
      <rect x={spineEndX - 120} y={spineY - 24} width={120} height={48} fill="#f5f5f5" stroke="#666" />
      <text x={spineEndX - 60} y={spineY} textAnchor="middle" dominantBaseline="middle" fontSize={12} fill="#111" style={{ fontWeight: 600 }}>{problem}</text>
      {/* Categories */}
      {topCats.map((c, i) => renderCategory(c, i, 'top'))}
      {bottomCats.map((c, i) => renderCategory(c, i, 'bottom'))}
    </svg>
  );
};

export default FishboneDiagram;

