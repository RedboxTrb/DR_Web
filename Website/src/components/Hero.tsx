import { Eye, ArrowRight } from 'lucide-react';

export function Hero() {
  return (
    <section className="relative bg-white py-20 px-6">
      <div className="max-w-7xl mx-auto">
        <div className="grid md:grid-cols-2 gap-12 items-center">
          <div>
            <div className="inline-flex items-center gap-2 px-3 py-1 bg-blue-50 text-blue-600 rounded-full mb-6 border border-blue-100">
              <span className="w-1.5 h-1.5 bg-blue-600 rounded-full"></span>
              <span className="text-sm">Automated Diagnosis</span>
            </div>
            
            <h1 className="text-5xl mb-6 text-gray-900">
              Analyze retinal images with precision
            </h1>
            
            <p className="text-gray-600 mb-8 leading-relaxed">
              Upload retinal fundus images and get instant automated analysis including vessel mapping,
              diabetic retinopathy detection, and glaucoma screening with advanced neural network models.
            </p>
            
            <div className="flex gap-4">
              <button 
                onClick={() => document.getElementById('upload-section')?.scrollIntoView({ behavior: 'smooth' })}
                className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors flex items-center gap-2"
              >
                Get Started
                <ArrowRight className="w-4 h-4" />
              </button>
              <button 
                onClick={() => document.getElementById('how-it-works')?.scrollIntoView({ behavior: 'smooth' })}
                className="px-6 py-3 border border-gray-300 rounded-lg hover:border-gray-400 hover:bg-gray-50 transition-colors"
              >
                Learn More
              </button>
            </div>
          </div>
          
          <div className="relative">
            <div className="bg-gray-50 rounded-2xl p-12 flex items-center justify-center aspect-square border border-gray-200">
              <div className="text-center">
                <div className="w-24 h-24 bg-blue-600 rounded-xl mx-auto mb-4 flex items-center justify-center">
                  <Eye className="w-12 h-12 text-white" />
                </div>
                <p className="text-gray-500">Retinal Image Preview</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}