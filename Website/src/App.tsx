import { useState } from 'react';
import { Header } from './components/Header';
import { Hero } from './components/Hero';
import { Features } from './components/Features';
import { HowItWorks } from './components/HowItWorks';
import { UploadSection } from './components/UploadSection';
import { ResultsDisplay } from './components/ResultsDisplay';
import { FAQ } from './components/FAQ';
import { Contact } from './components/Contact';
import { Footer } from './components/Footer';
import { useLocation } from './hooks/useLocation';

export interface AnalysisResult {
  id: string;
  originalImage: string;
  vesselMap: string;
  binaryVesselMap: string;
  grade: number; // 0-4
  severity: string; // "No DR", "Grade 1", "Grade 2", "Grade 3", "Grade 4"
  confidence: number;
  processingTime: number;
  stage1Result?: string;
  stage2Result?: string;
  stage3Result?: string;
}

export default function App() {
  const [results, setResults] = useState<AnalysisResult[]>([]);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const { location } = useLocation();

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
          return {
            id: `result-${Date.now()}-${index}`,
            originalImage: `data:image/png;base64,${result.original_image}`,
            vesselMap: `data:image/png;base64,${result.vessel_map}`,
            binaryVesselMap: `data:image/png;base64,${result.binary_vessel_map}`,
            grade: result.classification.grade,
            severity: result.classification.severity,
            confidence: result.classification.confidence * 100,
            processingTime: result.processing_time,
            stage1Result: result.classification.stage1_result,
            stage2Result: result.classification.stage2_result,
            stage3Result: result.classification.stage3_result
          };
        });

        setResults(analysisResults);
      } else {
        console.error('Analysis failed:', data.error);
        alert(`Analysis failed: ${data.error || 'Unknown error'}. Please try again.`);
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
      <Header />
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
        <ResultsDisplay results={results} onReset={handleReset} userLocation={location} />
      )}
    </div>
  );
}