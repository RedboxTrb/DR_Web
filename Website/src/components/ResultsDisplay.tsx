import { AnalysisResult } from '../App';
import { CheckCircle, AlertCircle, XCircle, ArrowLeft, Download, Share2, Info, Clock } from 'lucide-react';

interface ResultsDisplayProps {
  results: AnalysisResult[];
  onReset: () => void;
}

const GRADE_INFO = {
  0: {
    title: 'No Diabetic Retinopathy',
    description: 'No signs of diabetic retinopathy detected. Retina appears healthy.',
    color: 'green',
    risk: 'None',
    recommendation: 'Continue annual eye screenings to monitor eye health.'
  },
  1: {
    title: 'Mild DR (Grade 1)',
    description: 'Early stage diabetic retinopathy with microaneurysms.',
    color: 'yellow',
    risk: 'Low',
    recommendation: 'Follow-up in 6-12 months. Maintain good blood sugar control.'
  },
  2: {
    title: 'Moderate DR (Grade 2)',
    description: 'More extensive retinal changes including hemorrhages and exudates.',
    color: 'orange',
    risk: 'Medium',
    recommendation: 'Follow-up in 3-6 months. Consult ophthalmologist for treatment plan.'
  },
  3: {
    title: 'Severe DR (Grade 3)',
    description: 'Advanced diabetic retinopathy with significant vascular changes.',
    color: 'red',
    risk: 'High',
    recommendation: 'Immediate ophthalmologist consultation. Treatment may be necessary.'
  },
  4: {
    title: 'Proliferative DR (Grade 4)',
    description: 'Most advanced stage with new blood vessel growth and high risk of vision loss.',
    color: 'red',
    risk: 'Very High',
    recommendation: 'URGENT: Immediate specialist referral. Treatment required to prevent vision loss.'
  }
};

export function ResultsDisplay({ results, onReset }: ResultsDisplayProps) {
  const getGradeColor = (grade: number) => {
    const colorMap: Record<string, string> = {
      'green': 'text-green-600 bg-green-50 border-green-200',
      'yellow': 'text-yellow-600 bg-yellow-50 border-yellow-200',
      'orange': 'text-orange-600 bg-orange-50 border-orange-200',
      'red': 'text-red-600 bg-red-50 border-red-200'
    };
    return colorMap[GRADE_INFO[grade as keyof typeof GRADE_INFO]?.color] || colorMap['green'];
  };

  const getGradeBarColor = (grade: number) => {
    const colorMap: Record<string, string> = {
      'green': 'bg-green-600',
      'yellow': 'bg-yellow-600',
      'orange': 'bg-orange-600',
      'red': 'bg-red-600'
    };
    return colorMap[GRADE_INFO[grade as keyof typeof GRADE_INFO]?.color] || colorMap['green'];
  };

  const getGradeIcon = (grade: number) => {
    if (grade === 0) return CheckCircle;
    if (grade <= 2) return AlertCircle;
    return XCircle;
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
            const Icon = getGradeIcon(result.grade);
            const gradeInfo = GRADE_INFO[result.grade as keyof typeof GRADE_INFO];

            return (
              <div key={result.id} className="bg-white rounded-xl shadow-sm overflow-hidden border border-gray-200">
                <div className="grid md:grid-cols-2 gap-6 p-6">
                  {/* Original Image */}
                  <div>
                    <div className="flex items-center justify-between mb-3">
                      <h3 className="text-gray-900 font-semibold">Original Image</h3>
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
                      <h3 className="text-gray-900 font-semibold">Vessel Map</h3>
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
                  <div className="grid md:grid-cols-3 gap-6">
                    {/* Main Diagnosis */}
                    <div className="md:col-span-2">
                      <h3 className="mb-4 text-gray-900 font-semibold text-lg">Diagnosis</h3>
                      <div className={`flex items-start gap-4 p-5 rounded-lg border ${getGradeColor(result.grade)}`}>
                        <Icon className="w-7 h-7 flex-shrink-0 mt-1" />
                        <div className="flex-1">
                          <div className="mb-3">
                            <p className="text-lg font-semibold mb-1">{gradeInfo.title}</p>
                            <p className="text-sm opacity-90">{gradeInfo.description}</p>
                          </div>

                          <div className="mb-3">
                            <div className="flex items-center justify-between text-sm mb-1">
                              <span>Confidence</span>
                              <span className="font-semibold">{result.confidence.toFixed(1)}%</span>
                            </div>
                            <div className="h-2 bg-white rounded-full overflow-hidden">
                              <div
                                className={`h-full ${getGradeBarColor(result.grade)}`}
                                style={{ width: `${result.confidence}%` }}
                              ></div>
                            </div>
                          </div>

                          {/* Processing details */}
                          <div className="flex items-center gap-2 text-xs opacity-75">
                            <Clock className="w-3 h-3" />
                            <span>Processed in {result.processingTime.toFixed(2)}s</span>
                          </div>
                        </div>
                      </div>

                      {/* Cascade Decision Path */}
                      {(result.stage1Result || result.stage2Result || result.stage3Result) && (
                        <div className="mt-4 p-4 bg-white border border-gray-200 rounded-lg">
                          <h4 className="text-sm font-semibold text-gray-900 mb-3 flex items-center gap-2">
                            <Info className="w-4 h-4" />
                            AI Decision Path
                          </h4>
                          <div className="space-y-2 text-sm">
                            {result.stage1Result && (
                              <div className="flex items-center gap-2">
                                <span className="px-2 py-0.5 bg-blue-100 text-blue-800 rounded text-xs font-medium">Stage 1</span>
                                <span className="text-gray-700">{result.stage1Result}</span>
                              </div>
                            )}
                            {result.stage2Result && (
                              <div className="flex items-center gap-2">
                                <span className="px-2 py-0.5 bg-purple-100 text-purple-800 rounded text-xs font-medium">Stage 2</span>
                                <span className="text-gray-700">{result.stage2Result}</span>
                              </div>
                            )}
                            {result.stage3Result && (
                              <div className="flex items-center gap-2">
                                <span className="px-2 py-0.5 bg-indigo-100 text-indigo-800 rounded text-xs font-medium">Stage 3</span>
                                <span className="text-gray-700">{result.stage3Result}</span>
                              </div>
                            )}
                          </div>
                        </div>
                      )}
                    </div>

                    {/* Clinical Information */}
                    <div>
                      <h3 className="mb-4 text-gray-900 font-semibold text-lg">Clinical Info</h3>
                      <div className="space-y-3">
                        <div className="p-4 bg-white rounded-lg border border-gray-200">
                          <div className="text-xs text-gray-500 mb-1">Grade</div>
                          <div className="text-2xl font-bold text-gray-900">Grade {result.grade}</div>
                        </div>

                        <div className="p-4 bg-white rounded-lg border border-gray-200">
                          <div className="text-xs text-gray-500 mb-1">Risk Level</div>
                          <div className={`text-lg font-semibold ${
                            gradeInfo.risk === 'None' ? 'text-green-600' :
                            gradeInfo.risk === 'Low' ? 'text-yellow-600' :
                            gradeInfo.risk === 'Medium' ? 'text-orange-600' :
                            'text-red-600'
                          }`}>
                            {gradeInfo.risk}
                          </div>
                        </div>

                        <div className="p-4 bg-blue-50 rounded-lg border border-blue-200">
                          <div className="text-xs text-blue-800 font-medium mb-2 flex items-center gap-1">
                            <Info className="w-3 h-3" />
                            Recommendation
                          </div>
                          <div className="text-sm text-blue-900">
                            {gradeInfo.recommendation}
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>

                  {/* Disclaimer */}
                  <div className="mt-6 p-4 bg-yellow-50 border border-yellow-200 rounded-lg">
                    <p className="text-xs text-yellow-900">
                      <strong>Medical Disclaimer:</strong> This AI analysis is for screening purposes only and should not replace professional medical diagnosis.
                      Please consult a qualified ophthalmologist for definitive diagnosis and treatment recommendations.
                    </p>
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
