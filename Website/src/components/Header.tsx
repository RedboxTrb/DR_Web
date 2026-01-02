import { Eye } from 'lucide-react';

export function Header() {
  return (
    <header className="w-full bg-white border-b border-gray-200 shadow-sm">
      <div className="max-w-7xl mx-auto px-6 py-3 flex items-center gap-3">
        <div className="w-7 h-7 bg-gradient-to-br from-blue-600 to-blue-700 rounded-md flex items-center justify-center">
          <Eye className="w-4 h-4 text-white" strokeWidth={2} />
        </div>
        <h1 className="text-lg font-light tracking-tight text-gray-900">
          ChakshuRakshak<span className="font-medium">AI-DR</span>
        </h1>
      </div>
    </header>
  );
}
