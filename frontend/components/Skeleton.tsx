/** Reusable skeleton primitives for loading states */
export function SkeletonBox({ className = '' }: { className?: string }) {
  return (
    <div className={`bg-white/[0.05] animate-pulse rounded-xl ${className}`} />
  );
}

export function DashboardSkeleton() {
  return (
    <div className="p-6 space-y-6 max-w-[1400px]">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="space-y-2">
          <SkeletonBox className="h-6 w-52" />
          <SkeletonBox className="h-3 w-36" />
        </div>
        <div className="flex gap-2">
          <SkeletonBox className="h-9 w-24 rounded-xl" />
          <SkeletonBox className="h-9 w-36 rounded-xl" />
        </div>
      </div>

      {/* Stat cards */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        {[...Array(4)].map((_, i) => (
          <SkeletonBox key={i} className="h-28 rounded-2xl" />
        ))}
      </div>

      {/* Charts row */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-5">
        <SkeletonBox className="lg:col-span-2 h-56 rounded-2xl" />
        <SkeletonBox className="h-56 rounded-2xl" />
      </div>

      {/* Bottom row */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-5">
        <SkeletonBox className="lg:col-span-2 h-72 rounded-2xl" />
        <div className="space-y-4">
          <SkeletonBox className="h-40 rounded-2xl" />
          <SkeletonBox className="h-28 rounded-2xl" />
        </div>
      </div>
    </div>
  );
}

export function EventsSkeleton() {
  return (
    <div className="p-6 space-y-5 max-w-[1400px]">
      <div className="flex items-center justify-between">
        <SkeletonBox className="h-6 w-48" />
        <SkeletonBox className="h-9 w-24 rounded-xl" />
      </div>
      <div className="flex gap-3">
        {[...Array(4)].map((_, i) => <SkeletonBox key={i} className="h-8 w-28 rounded-xl" />)}
      </div>
      <div className="flex gap-3">
        <SkeletonBox className="h-10 flex-1 rounded-xl" />
        <SkeletonBox className="h-10 w-36 rounded-xl" />
        <SkeletonBox className="h-10 w-36 rounded-xl" />
      </div>
      <SkeletonBox className="h-[480px] rounded-2xl" />
    </div>
  );
}

export function AnalyticsSkeleton() {
  return (
    <div className="p-6 space-y-6 max-w-[1400px]">
      <div className="flex items-center justify-between">
        <SkeletonBox className="h-6 w-48" />
        <SkeletonBox className="h-9 w-36 rounded-xl" />
      </div>
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        {[...Array(4)].map((_, i) => <SkeletonBox key={i} className="h-24 rounded-2xl" />)}
      </div>
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <SkeletonBox className="h-72 rounded-2xl" />
        <SkeletonBox className="h-72 rounded-2xl" />
      </div>
      <SkeletonBox className="h-48 rounded-2xl" />
    </div>
  );
}

export function GenericSkeleton() {
  return (
    <div className="p-6 space-y-4 max-w-[1100px]">
      <SkeletonBox className="h-6 w-56 mb-2" />
      <SkeletonBox className="h-40 rounded-2xl" />
      <SkeletonBox className="h-64 rounded-2xl" />
      <SkeletonBox className="h-48 rounded-2xl" />
    </div>
  );
}
