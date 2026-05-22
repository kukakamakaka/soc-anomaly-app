'use client';
import { ResponsiveContainer, PieChart, Pie, Cell, Tooltip } from 'recharts';

interface Slice { name: string; value: number; hex: string }

function CustomTooltip({ active, payload }: { active?: boolean; payload?: { name: string; value: number }[] }) {
  if (!active || !payload?.length) return null;
  return (
    <div className="bg-[#0d1b2e] border border-white/10 rounded-xl px-3 py-2 shadow-xl text-xs">
      <p className="text-white font-bold uppercase">{payload[0]?.name}</p>
      <p className="text-slate-400 font-mono">{payload[0]?.value} events</p>
    </div>
  );
}

export default function SeverityChart({ data }: { data: Slice[] }) {
  if (!data.length) return (
    <div className="h-36 flex items-center justify-center text-slate-600 text-xs">No data</div>
  );
  return (
    <>
      <ResponsiveContainer width="100%" height={140}>
        <PieChart>
          <Pie data={data} dataKey="value" nameKey="name"
            cx="50%" cy="50%" innerRadius={40} outerRadius={64}
            paddingAngle={3} stroke="none">
            {data.map(e => <Cell key={e.name} fill={e.hex} />)}
          </Pie>
          <Tooltip content={<CustomTooltip />} />
        </PieChart>
      </ResponsiveContainer>
      <div className="grid grid-cols-2 gap-1.5 mt-2">
        {data.map(({ name, value, hex }) => (
          <div key={name} className="flex items-center gap-1.5">
            <span className="w-2 h-2 rounded-full shrink-0" style={{ background: hex }} />
            <span className="text-[10px] text-slate-500 capitalize">{name}</span>
            <span className="text-[10px] font-bold text-slate-300 ml-auto font-mono">{value}</span>
          </div>
        ))}
      </div>
    </>
  );
}
