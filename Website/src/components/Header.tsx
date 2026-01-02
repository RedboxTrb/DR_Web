import { Eye } from 'lucide-react';

export function Header() {
  return (
    <header className="sticky top-0 z-50 bg-white border-b border-gray-100">
      <div className="max-w-7xl mx-auto px-6 py-4">
        <div className="flex items-center gap-3">
          <div className="w-8 h-8 bg-gradient-to-br from-blue-600 to-blue-700 rounded-lg flex items-center justify-center">
            <Eye className="w-5 h-5 text-white" strokeWidth={1.5} />
          </div>
          <h1 className="text-xl font-light tracking-tight text-gray-900">
            ChakshuRakshak<span className="font-normal">AI-DR</span>
          </h1>
        </div>
      </div>
    </header>
  );
}
