import { Network, Scan, Activity } from 'lucide-react';

export function Features() {
  const features = [
    {
      icon: Network,
      title: 'Vessel map generation',
      description: 'Advanced segmentation model extracts retinal blood vessel patterns for detailed analysis'
    },
    {
      icon: Scan,
      title: 'Disease classification',
      description: 'Accurate detection of Diabetic Retinopathy, Normal retina, and Glaucoma using state-of-the-art CNNs'
    },
    {
      icon: Activity,
      title: 'DR stage analysis',
      description: 'Automated grading of Diabetic Retinopathy severity from Mild to Proliferative stages'
    }
  ];

  return (
    <section className="py-20 px-6 bg-gray-50">
      <div className="max-w-7xl mx-auto">
        <h2 className="text-center text-4xl mb-4 text-gray-900">Three tools in one</h2>
        <p className="text-center text-gray-600 mb-16 max-w-2xl mx-auto">
          Comprehensive retinal analysis powered by multiple specialized neural network models
        </p>
        
        <div className="grid md:grid-cols-3 gap-8">
          {features.map((feature, index) => (
            <div key={index} className="bg-white rounded-xl p-8 hover:shadow-lg transition-shadow border border-gray-200">
              <div className="w-12 h-12 bg-blue-600 rounded-lg flex items-center justify-center mb-4">
                <feature.icon className="w-6 h-6 text-white" />
              </div>
              <h3 className="text-xl mb-3 text-gray-900">{feature.title}</h3>
              <p className="text-gray-600 leading-relaxed">{feature.description}</p>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}