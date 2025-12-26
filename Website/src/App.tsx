import { useState } from 'react';
import { Hero } from './components/Hero';
import { Features } from './components/Features';
import { HowItWorks } from './components/HowItWorks';
import { UploadSection } from './components/UploadSection';
import { ResultsDisplay } from './components/ResultsDisplay';
import { FAQ } from './components/FAQ';
import { Contact } from './components/Contact';
import { Footer } from './components/Footer';

export interface AnalysisResult {
  id: string;
  originalImage: string;
  vesselMap: string;
  diagnosis: 'DR' | 'NODR' | 'Glaucoma';
  drStage?: 'Mild' | 'Moderate' | 'Severe' | 'Proliferative';
  confidence: number;
}

export default function App() {
  const [results, setResults] = useState<AnalysisResult[]>([]);
  const [isAnalyzing, setIsAnalyzing] = useState(false);

  const handleAnalysis = async (uploadedImages: File[]) => {
    setIsAnalyzing(true);

    try {
      const formData = new FormData();
      uploadedImages.forEach(file => formData.append('images', file));

      const response = await fetch('http://localhost:5000/api/predict', {
        method: 'POST',
        body: formData
      });

      const data = await response.json();

      if (data.success) {
        const analysisResults: AnalysisResult[] = data.results.map((result: any, index: number) => {
          // Map backend response to frontend format
          const hasGlaucoma = false; // Backend only does DR classification
          const diagnosis: 'DR' | 'NODR' | 'Glaucoma' = result.classification.has_dr ? 'DR' : 'NODR';

          // Map severity grades to DR stages
          let drStage: 'Mild' | 'Moderate' | 'Severe' | 'Proliferative' | undefined;
          if (diagnosis === 'DR') {
            const grade = result.classification.grade;
            if (grade === 1) drStage = 'Mild';
            else if (grade === 2) drStage = 'Moderate';
            else if (grade === 3) drStage = 'Severe';
            else if (grade === 4) drStage = 'Proliferative';
          }

          return {
            id: `result-${Date.now()}-${index}`,
            originalImage: `data:image/png;base64,${result.original_image}`,
            vesselMap: `data:image/png;base64,${result.vessel_map}`,
            diagnosis,
            drStage,
            confidence: result.classification.confidence * 100
          };
        });

        setResults(analysisResults);
      } else {
        console.error('Analysis failed:', data.error);
        alert('Analysis failed. Please try again.');
      }
    } catch (error) {
      console.error('Error calling backend:', error);
      alert('Error connecting to backend server. Make sure it is running on http://localhost:5000');
    } finally {
      setIsAnalyzing(false);
    }
  };

  const handleReset = () => {
    setResults([]);
  };

  return (
    <div className="min-h-screen bg-white">
      {results.length === 0 ? (
        <>
          <Hero />
          <Features />
          <HowItWorks />
          <UploadSection onAnalysis={handleAnalysis} isAnalyzing={isAnalyzing} />
          <FAQ />
          <Contact />
          <Footer />
        </>
      ) : (
        <ResultsDisplay results={results} onReset={handleReset} />
      )}
    </div>
  );
}