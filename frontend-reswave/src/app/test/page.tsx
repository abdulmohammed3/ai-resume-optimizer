'use client';

import TestOptimizer from '@/components/TestOptimizer';

export default function TestPage() {
  return (
    <div className="min-h-screen bg-gray-50">
      <div className="py-8">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <TestOptimizer />
        </div>
      </div>
    </div>
  );
}