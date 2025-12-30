import { ChevronDown } from 'lucide-react';
import { useState } from 'react';

export function FAQ() {
  const [openIndex, setOpenIndex] = useState<number | null>(null);

  const faqs = [
    {
      question: 'What image formats are supported?',
      answer: 'Our system supports common image formats including JPG, PNG, and TIFF. For best results, use high-resolution retinal fundus images captured with standard fundus cameras.'
    },
    {
      question: 'How accurate are the models?',
      answer: 'Our models have been trained on large datasets and achieve high accuracy rates. However, these results should be used as a screening tool and confirmed by qualified ophthalmologists for clinical decisions.'
    },
    {
      question: 'What is the difference between DR stages?',
      answer: 'Diabetic Retinopathy is classified into stages: Mild (microaneurysms only), Moderate (more extensive vascular abnormalities), Severe (extensive hemorrhages and microaneurysms), and Proliferative (new blood vessel growth).'
    },
    {
      question: 'Can I process multiple images at once?',
      answer: 'Yes! You can upload and analyze multiple retinal images in a single batch. Each image will be processed independently and results will be displayed for all images.'
    },
    {
      question: 'How is patient data protected?',
      answer: 'All uploaded images are processed securely. We recommend removing any patient identifying information from images before upload. Images are not stored permanently on our servers.'
    }
  ];

  return (
    <section className="py-20 px-6 bg-white">
      <div className="max-w-3xl mx-auto">
        <div className="text-center mb-12">
          <h2 className="text-4xl mb-4 text-gray-900">Questions</h2>
          <p className="text-gray-600">Frequently asked questions about our retinal analysis platform</p>
        </div>

        <div className="space-y-3">
          {faqs.map((faq, index) => (
            <div key={index} className="border border-gray-200 rounded-lg overflow-hidden hover:border-gray-300 transition-colors">
              <button
                onClick={() => setOpenIndex(openIndex === index ? null : index)}
                className="w-full flex items-center justify-between p-5 text-left hover:bg-gray-50 transition-colors"
              >
                <span className="text-gray-900">{faq.question}</span>
                <ChevronDown 
                  className={`w-5 h-5 text-gray-400 transition-transform ${
                    openIndex === index ? 'rotate-180' : ''
                  }`} 
                />
              </button>
              {openIndex === index && (
                <div className="px-5 pb-5 text-gray-600 bg-gray-50 border-t border-gray-100">
                  {faq.answer}
                </div>
              )}
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}