'use client';
import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { isAuthenticated } from '@/lib/auth';
import Sidebar from '@/components/Sidebar';

export default function PlatformLayout({ children }: { children: React.ReactNode }) {
  const router = useRouter();
  // Track mount so we never branch on `typeof window` during render
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    setMounted(true);
    if (!isAuthenticated()) router.replace('/login');
  }, [router]);

  // Before mount: render a blank screen that matches the SSR output exactly
  if (!mounted) {
    return (
      <div className="flex h-screen overflow-hidden bg-[#010b18]">
        <div className="glow-orb-1" />
        <div className="glow-orb-2" />
        <div className="glow-orb-3" />
      </div>
    );
  }

  // After mount: if not authenticated the redirect is already in flight
  if (!isAuthenticated()) return null;

  return (
    <div className="flex h-screen overflow-hidden bg-[#010b18]">
      <div className="glow-orb-1" />
      <div className="glow-orb-2" />
      <div className="glow-orb-3" />

      <Sidebar />

      <main className="flex-1 overflow-y-auto overflow-x-hidden relative">
        {children}
      </main>
    </div>
  );
}
