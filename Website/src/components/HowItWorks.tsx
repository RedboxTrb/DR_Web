import { Upload, Cpu, FileCheck } from 'lucide-react';

export function HowItWorks() {
  const steps = [
    {
      icon: Upload,
      title: 'Upload images',
      description: 'Upload one or multiple retinal fundus images in common formats (JPG, PNG)'
    },
    {
      icon: Cpu,
      title: 'Image processing',
      description: 'Our models generate vessel maps and analyze for DR, normal retina, or glaucoma indicators'
    },
    {
      icon: FileCheck,
      title: 'Receive results',
      description: 'Get detailed reports with vessel maps, diagnoses, and DR staging if applicable'
    }
  ];

  return (
    <section id="how-it-works" className="py-20 px-6 bg-white">
      <div className="max-w-7xl mx-auto">
        <h2 className="text-center text-4xl mb-4 text-gray-900">Three steps to diagnosis</h2>
        <p className="text-center text-gray-600 mb-16 max-w-2xl mx-auto">
          Simple workflow for comprehensive retinal analysis
        </p>
        
        <div className="grid md:grid-cols-3 gap-8 relative">
          {/* Connection line */}
          <div className="hidden md:block absolute top-20 left-1/4 right-1/4 h-0.5 bg-gray-200"></div>
          
          {steps.map((step, index) => (
            <div key={index} className="relative">
              <div className="bg-white rounded-xl p-8 border border-gray-200 hover:border-blue-600 transition-colors">
                <div className="absolute -top-4 left-1/2 -translate-x-1/2 w-8 h-8 bg-blue-600 text-white rounded-full flex items-center justify-center z-10">
                  {index + 1}
                </div>
                <div className="w-full aspect-square bg-gray-50 rounded-lg flex items-center justify-center mb-6 mt-4 border border-gray-200">
                  <step.icon className="w-16 h-16 text-gray-400" />
                </div>
                <h3 className="text-xl mb-3 text-gray-900">{step.title}</h3>
                <p className="text-gray-600 leading-relaxed">{step.description}</p>
              </div>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}