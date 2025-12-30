import { useState, useRef } from 'react';
import { Upload, X, Image as ImageIcon } from 'lucide-react';

interface UploadSectionProps {
  onAnalysis: (files: File[]) => void;
  isAnalyzing: boolean;
}

export function UploadSection({ onAnalysis, isAnalyzing }: UploadSectionProps) {
  const [selectedFiles, setSelectedFiles] = useState<File[]>([]);
  const [dragActive, setDragActive] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleDrag = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setDragActive(true);
    } else if (e.type === 'dragleave') {
      setDragActive(false);
    }
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);

    const files = Array.from(e.dataTransfer.files).filter(file => 
      file.type.startsWith('image/')
    );
    setSelectedFiles(prev => [...prev, ...files]);
  };

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files) {
      const files = Array.from(e.target.files);
      setSelectedFiles(prev => [...prev, ...files]);
    }
  };

  const removeFile = (index: number) => {
    setSelectedFiles(prev => prev.filter((_, i) => i !== index));
  };

  const handleAnalyze = () => {
    if (selectedFiles.length > 0) {
      onAnalysis(selectedFiles);
    }
  };

  return (
    <section id="upload-section" className="py-20 px-6 bg-gray-50">
      <div className="max-w-4xl mx-auto">
        <div className="text-center mb-8">
          <h2 className="text-4xl mb-4 text-gray-900">Start your analysis</h2>
          <p className="text-gray-600 max-w-2xl mx-auto">
            Upload one or multiple retinal fundus images to begin automated analysis
          </p>
        </div>

        <div className="bg-white rounded-xl p-8 shadow-sm border border-gray-200">
          <div
            className={`border-2 border-dashed rounded-lg p-12 mb-6 transition-all ${
              dragActive 
                ? 'border-blue-500 bg-blue-50' 
                : 'border-gray-300 bg-gray-50'
            }`}
            onDragEnter={handleDrag}
            onDragLeave={handleDrag}
            onDragOver={handleDrag}
            onDrop={handleDrop}
          >
            <Upload className="w-12 h-12 text-gray-400 mx-auto mb-4" />
            <p className="text-center mb-2 text-gray-700">Drag and drop retinal images here</p>
            <p className="text-center text-gray-500 text-sm mb-4">or</p>
            <div className="text-center">
              <button
                onClick={() => fileInputRef.current?.click()}
                className="px-6 py-2.5 bg-blue-600 text-white hover:bg-blue-700 rounded-lg transition-colors inline-flex items-center gap-2"
              >
                <Upload className="w-4 h-4" />
                Browse Files
              </button>
            </div>
            <input
              ref={fileInputRef}
              type="file"
              multiple
              accept="image/*"
              onChange={handleFileSelect}
              className="hidden"
            />
          </div>

          {selectedFiles.length > 0 && (
            <div className="mb-6">
              <h3 className="text-left mb-3 text-gray-900">{selectedFiles.length} image{selectedFiles.length > 1 ? 's' : ''} selected</h3>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                {selectedFiles.map((file, index) => (
                  <div key={index} className="relative bg-gray-50 rounded-lg p-3 group border border-gray-200">
                    <button
                      onClick={() => removeFile(index)}
                      className="absolute -top-2 -right-2 w-6 h-6 bg-red-500 rounded-full flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity"
                    >
                      <X className="w-4 h-4 text-white" />
                    </button>
                    <ImageIcon className="w-8 h-8 mx-auto mb-2 text-gray-400" />
                    <p className="text-xs text-gray-700 truncate">{file.name}</p>
                    <p className="text-xs text-gray-500">{(file.size / 1024).toFixed(1)} KB</p>
                  </div>
                ))}
              </div>
            </div>
          )}

          <button
            onClick={handleAnalyze}
            disabled={selectedFiles.length === 0 || isAnalyzing}
            className="w-full py-3.5 bg-blue-600 hover:bg-blue-700 disabled:bg-gray-300 disabled:cursor-not-allowed text-white rounded-lg transition-colors"
          >
            {isAnalyzing ? (
              <span className="flex items-center justify-center gap-2">
                <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
                Analyzing...
              </span>
            ) : (
              `Analyze ${selectedFiles.length} Image${selectedFiles.length !== 1 ? 's' : ''}`
            )}
          </button>
        </div>
      </div>
    </section>
  );
}