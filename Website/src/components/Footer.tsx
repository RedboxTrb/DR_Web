export function Footer() {
  return (
    <footer className="bg-white border-t border-gray-200 py-8 px-6">
      <div className="max-w-7xl mx-auto">
        <div className="flex flex-wrap justify-center gap-8 text-sm text-gray-600 mb-4">
          <a href="#" className="hover:text-blue-600 transition-colors">Privacy</a>
          <a href="#" className="hover:text-blue-600 transition-colors">Accessibility</a>
          <a href="#" className="hover:text-blue-600 transition-colors">Terms</a>
        </div>
        <p className="text-center text-gray-500 text-sm">
          © 2025 Retinal Analysis Platform. All rights reserved.
        </p>
      </div>
    </footer>
  );
}