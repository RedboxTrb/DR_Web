import { AnalysisResult } from '../App';
import { CheckCircle, AlertCircle, XCircle, ArrowLeft, Download, Share2 } from 'lucide-react';

interface ResultsDisplayProps {
  results: AnalysisResult[];
  onReset: () => void;
}

export function ResultsDisplay({ results, onReset }: ResultsDisplayProps) {
  const getDiagnosisColor = (diagnosis: string) => {
    switch (diagnosis) {
      case 'NODR': return 'text-green-600 bg-green-50 border-green-200';
      case 'DR': return 'text-red-600 bg-red-50 border-red-200';
      case 'Glaucoma': return 'text-orange-600 bg-orange-50 border-orange-200';
      default: return 'text-gray-600 bg-gray-50 border-gray-200';
    }
  };

  const getDiagnosisBarColor = (diagnosis: string) => {
    switch (diagnosis) {
      case 'NODR': return 'bg-green-600';
      case 'DR': return 'bg-red-600';
      case 'Glaucoma': return 'bg-orange-600';
      default: return 'bg-gray-600';
    }
  };

  const getDiagnosisIcon = (diagnosis: string) => {
    switch (diagnosis) {
      case 'NODR': return CheckCircle;
      case 'DR': return XCircle;
      case 'Glaucoma': return AlertCircle;
      default: return AlertCircle;
    }
  };

  const getDiagnosisLabel = (diagnosis: string) => {
    switch (diagnosis) {
      case 'NODR': return 'No Diabetic Retinopathy';
      case 'DR': return 'Diabetic Retinopathy Detected';
      case 'Glaucoma': return 'Glaucoma Detected';
      default: return diagnosis;
    }
  };

  return (
    <section className="py-12 px-6 bg-gray-50 min-h-screen">
      <div className="max-w-7xl mx-auto">
        <div className="flex items-center justify-between mb-8 bg-white rounded-xl p-6 shadow-sm border border-gray-200">
          <div>
            <h2 className="text-4xl mb-2 text-gray-900">Analysis Results</h2>
            <p className="text-gray-600">{results.length} image{results.length > 1 ? 's' : ''} processed successfully</p>
          </div>
          <div className="flex gap-3">
            <button className="flex items-center gap-2 px-4 py-2 border border-gray-300 hover:bg-gray-50 rounded-lg transition-colors">
              <Download className="w-4 h-4" />
              Export
            </button>
            <button className="flex items-center gap-2 px-4 py-2 border border-gray-300 hover:bg-gray-50 rounded-lg transition-colors">
              <Share2 className="w-4 h-4" />
              Share
            </button>
            <button
              onClick={onReset}
              className="flex items-center gap-2 px-6 py-2 bg-blue-600 text-white hover:bg-blue-700 rounded-lg transition-colors"
            >
              <ArrowLeft className="w-4 h-4" />
              New Analysis
            </button>
          </div>
        </div>

        <div className="space-y-6">
          {results.map((result, index) => {
            const Icon = getDiagnosisIcon(result.diagnosis);
            
            return (
              <div key={result.id} className="bg-white rounded-xl shadow-sm overflow-hidden border border-gray-200">
                <div className="grid md:grid-cols-2 gap-6 p-6">
                  {/* Original Image */}
                  <div>
                    <div className="flex items-center justify-between mb-3">
                      <h3 className="text-gray-900">Original Image</h3>
                      <span className="px-3 py-1 bg-gray-100 text-gray-700 rounded-full text-sm">#{index + 1}</span>
                    </div>
                    <div className="bg-gray-50 rounded-lg overflow-hidden aspect-square border border-gray-200">
                      <img 
                        src={result.originalImage} 
                        alt="Original retinal scan" 
                        className="w-full h-full object-cover"
                      />
                    </div>
                  </div>

                  {/* Vessel Map */}
                  <div>
                    <div className="flex items-center justify-between mb-3">
                      <h3 className="text-gray-900">Vessel Map</h3>
                      <span className="px-3 py-1 bg-blue-50 text-blue-700 rounded-full text-sm border border-blue-200">
                        AI Generated
                      </span>
                    </div>
                    <div className="bg-gray-50 rounded-lg overflow-hidden aspect-square border border-gray-200">
                      <img 
                        src={result.vesselMap} 
                        alt="Vessel map" 
                        className="w-full h-full object-cover"
                      />
                    </div>
                  </div>
                </div>

                {/* Diagnosis Section */}
                <div className="border-t border-gray-200 p-6 bg-gray-50">
                  <div className="grid md:grid-cols-2 gap-6">
                    <div>
                      <h3 className="mb-4 text-gray-900">Diagnosis</h3>
                      <div className={`flex items-center gap-3 p-4 rounded-lg border ${getDiagnosisColor(result.diagnosis)}`}>
                        <Icon className="w-6 h-6 flex-shrink-0" />
                        <div className="flex-1">
                          <p className="mb-2">{getDiagnosisLabel(result.diagnosis)}</p>
                          <div className="flex items-center gap-2">
                            <div className="flex-1 h-2 bg-white rounded-full overflow-hidden">
                              <div 
                                className={`h-full ${getDiagnosisBarColor(result.diagnosis)}`}
                                style={{ width: `${result.confidence}%` }}
                              ></div>
                            </div>
                            <span className="text-sm">{result.confidence.toFixed(1)}%</span>
                          </div>
                        </div>
                      </div>

                      {result.drStage && (
                        <div className="mt-4 p-4 bg-red-50 border border-red-200 rounded-lg">
                          <h4 className="text-red-900 mb-1">DR Stage Classification</h4>
                          <p className="text-red-700">{result.drStage} Diabetic Retinopathy</p>
                        </div>
                      )}
                    </div>

                    <div>
                      <h3 className="mb-4 text-gray-900">Clinical Indicators</h3>
                      <div className="space-y-2 text-sm">
                        <div className="flex justify-between p-3 bg-white rounded-lg border border-gray-200">
                          <span className="text-gray-700">Vessel Tortuosity</span>
                          <span className={`px-2 py-0.5 rounded-full text-xs ${result.diagnosis === 'DR' ? 'bg-red-100 text-red-800' : 'bg-green-100 text-green-800'}`}>
                            {result.diagnosis === 'DR' ? 'Elevated' : 'Normal'}
                          </span>
                        </div>
                        <div className="flex justify-between p-3 bg-white rounded-lg border border-gray-200">
                          <span className="text-gray-700">Microaneurysms</span>
                          <span className={`px-2 py-0.5 rounded-full text-xs ${result.diagnosis === 'DR' ? 'bg-red-100 text-red-800' : 'bg-green-100 text-green-800'}`}>
                            {result.diagnosis === 'DR' ? 'Detected' : 'Not Detected'}
                          </span>
                        </div>
                        <div className="flex justify-between p-3 bg-white rounded-lg border border-gray-200">
                          <span className="text-gray-700">Optic Disc Changes</span>
                          <span className={`px-2 py-0.5 rounded-full text-xs ${result.diagnosis === 'Glaucoma' ? 'bg-orange-100 text-orange-800' : 'bg-green-100 text-green-800'}`}>
                            {result.diagnosis === 'Glaucoma' ? 'Abnormal' : 'Normal'}
                          </span>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      </div>
    </section>
  );
}