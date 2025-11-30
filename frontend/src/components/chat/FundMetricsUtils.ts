export const getSharpeContext = (value?: number) => {
  if (value === undefined || value === null) return { label: 'N/A', color: 'text-slate-500', bg: 'bg-slate-500' };
  if (value >= 2.0) return { label: 'Excellent', color: 'text-emerald-400', bg: 'bg-emerald-500' };
  if (value >= 1.0) return { label: 'Good', color: 'text-blue-400', bg: 'bg-blue-500' };
  return { label: 'Average', color: 'text-amber-400', bg: 'bg-amber-500' };
};

export const getVolatilityContext = (value?: number) => {
  if (value === undefined || value === null) return { label: 'N/A', color: 'text-slate-500' };
  if (value < 10) return { label: 'Low Risk', color: 'text-emerald-400' };
  if (value < 15) return { label: 'Moderate', color: 'text-amber-400' };
  return { label: 'High Volatility', color: 'text-rose-400' };
};

export const getReturnColor = (value?: number) => {
  if (value === undefined || value === null) return 'text-slate-400';
  if (value > 15) return 'text-emerald-400';
  if (value > 10) return 'text-blue-400';
  if (value > 0) return 'text-amber-400';
  return 'text-rose-400';
};

