import React, { useState, useEffect, useRef } from 'react';
import { 
  Upload, 
  Leaf, 
  Sprout, 
  AlertCircle, 
  CheckCircle2, 
  Droplets, 
  Sun, 
  Wind, 
  Activity, 
  ChevronRight, 
  Thermometer, 
  ScanLine,
  ArrowRight
} from 'lucide-react';

import plant from './assets/image.png';

// --- API Service ---
const analyzePlantImage = async (file) => {
  const formData = new FormData();
  formData.append('file', file);

  try {
    const response = await fetch('http://localhost:8000/predict', {
      method: 'POST',
      body: formData,
    });

    if (!response.ok) {
      let detail = `HTTP error! status: ${response.status}`;
      try {
        const body = await response.json();
        if (body?.detail) detail = body.detail;
      } catch { /* ignore non-JSON errors */ }
      throw new Error(detail);
    }

    const data = await response.json();
    return data;
  } catch (error) {
    console.error('Error analyzing image:', error);
    throw error;
  }
};

// --- Components ---

const Header = () => (
  <nav className="fixed top-0 left-0 right-0 z-50 bg-white/80 backdrop-blur-md border-b border-emerald-100 h-16 flex items-center justify-between px-6 lg:px-12 transition-all">
    <div className="flex items-center gap-2 cursor-pointer">
      <div className="bg-emerald-600 p-2 rounded-lg text-white">
        <Leaf size={24} fill="currentColor" />
      </div>
      <span className="text-2xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-emerald-700 to-teal-500">
        LeafX
      </span>
    </div>
    <div className="hidden md:flex gap-8 text-gray-600 font-medium">
      <a href="#" className="hover:text-emerald-600 transition-colors">How it Works</a>
      <a href="#" className="hover:text-emerald-600 transition-colors">Our Database</a>
      <a href="#" className="hover:text-emerald-600 transition-colors">Community</a>
    </div>
    <button className="bg-emerald-600 hover:bg-emerald-700 text-white px-6 py-2 rounded-full font-medium transition-all shadow-lg shadow-emerald-200">
      Sign In
    </button>
  </nav>
);

const Hero = ({ onStart }) => (
  <div className="relative min-h-screen flex items-center justify-center pt-16 overflow-hidden">
    {/* Abstract Background Blobs */}
    <div className="absolute top-0 left-0 w-full h-full overflow-hidden -z-10">
      <div className="absolute top-[-10%] left-[-10%] w-[50%] h-[50%] bg-emerald-300/30 rounded-full blur-[120px] animate-pulse" />
      <div className="absolute bottom-[-10%] right-[-10%] w-[50%] h-[50%] bg-teal-300/30 rounded-full blur-[120px] animate-pulse" style={{ animationDelay: '2s' }} />
    </div>

    <div className="container mx-auto px-6 grid lg:grid-cols-2 gap-12 items-center">
      <div className="space-y-8 animate-fade-in-up">
        <div className="inline-flex items-center gap-2 px-4 py-2 bg-emerald-50 text-emerald-700 rounded-full border border-emerald-100 text-sm font-semibold">
          <Sprout size={16} />
          <span>AI-Powered Agriculture V2.0</span>
        </div>
        <h1 className="text-5xl lg:text-7xl font-extrabold text-gray-900 leading-tight">
          Diagnose Crops with <br />
          <span className="text-transparent bg-clip-text bg-gradient-to-r from-emerald-600 to-teal-500">
            Computer Vision
          </span>
        </h1>
        <p className="text-xl text-gray-600 max-w-lg leading-relaxed">
          Upload a photo of a plant leaf. Our MobileNetV2 model recognises 38 healthy and diseased leaf conditions across 14 crops and recommends treatment instantly.
        </p>
        <div className="flex flex-col sm:flex-row gap-4">
          <button 
            onClick={onStart}
            className="group flex items-center justify-center gap-2 bg-emerald-600 hover:bg-emerald-700 text-white text-lg px-8 py-4 rounded-xl font-bold transition-all shadow-xl shadow-emerald-200 hover:-translate-y-1"
          >
            Start Diagnosis
            <ArrowRight className="group-hover:translate-x-1 transition-transform" />
          </button>
          <button className="flex items-center justify-center gap-2 bg-white hover:bg-gray-50 text-gray-700 border border-gray-200 text-lg px-8 py-4 rounded-xl font-bold transition-all hover:-translate-y-1">
            View Demo
          </button>
        </div>
        
        <div className="pt-8 flex items-center gap-8 text-gray-400 text-sm font-medium">
          <div className="flex items-center gap-2">
            <CheckCircle2 size={18} className="text-emerald-500" /> 38 Conditions
          </div>
          <div className="flex items-center gap-2">
            <CheckCircle2 size={18} className="text-emerald-500" /> Instant Results
          </div>
          <div className="flex items-center gap-2">
            <CheckCircle2 size={18} className="text-emerald-500" /> Free Tier
          </div>
        </div>
      </div>

      <div className="relative hidden lg:block">
        <div className="relative z-10 bg-white p-6 rounded-3xl shadow-2xl border border-gray-100 transform rotate-2 hover:rotate-0 transition-transform duration-500">
          <img 
            src={plant} 
            alt="Healthy Plant" 
            className="w-full h-80 object-cover rounded-2xl"
          />
          <div className="absolute top-10 right-10 bg-white/90 backdrop-blur rounded-xl p-4 shadow-lg flex items-center gap-4 animate-bounce-slow">
            <div className="w-12 h-12 bg-green-100 rounded-full flex items-center justify-center text-green-600">
              <Activity />
            </div>
            <div>
              <p className="text-xs text-gray-500 uppercase font-bold tracking-wider">Health Status</p>
              <p className="text-lg font-bold text-gray-900">Optimal</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
);

const UploadArea = ({ onFileSelect, error }) => {
  const [isDragging, setIsDragging] = useState(false);
  const inputRef = useRef(null);

  const handleDrag = (e) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setIsDragging(true);
    } else if (e.type === 'dragleave') {
      setIsDragging(false);
    }
  };

  const handleDrop = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(false);
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      onFileSelect(e.dataTransfer.files[0]);
    }
  };

  return (
    <div className="min-h-screen flex flex-col items-center justify-center px-4 pt-16 bg-gray-50">
      <div className="w-full max-w-3xl text-center space-y-4 mb-8">
        <h2 className="text-4xl font-bold text-gray-900">Upload Plant Image</h2>
        <p className="text-gray-500">Upload a clear, close-up photo of a single <strong>leaf</strong> (not the fruit). JPG, PNG or WEBP, max 10MB.</p>
        <p className="text-gray-400 text-sm">Supports 14 crops: Apple, Blueberry, Cherry, Corn, Grape, Orange, Peach, Bell Pepper, Potato, Raspberry, Soybean, Squash, Strawberry, Tomato.</p>
        {error && (
          <div className="mx-auto max-w-2xl flex items-start gap-3 p-4 bg-red-50 border border-red-200 rounded-xl text-left text-red-700">
            <AlertCircle className="shrink-0 mt-0.5" size={20} />
            <span>Analysis failed: {error}</span>
          </div>
        )}
      </div>

      <div 
        className={`
          w-full max-w-2xl aspect-[16/9] rounded-3xl border-4 border-dashed transition-all duration-300 flex flex-col items-center justify-center cursor-pointer relative overflow-hidden bg-white
          ${isDragging ? 'border-emerald-500 bg-emerald-50 scale-105' : 'border-gray-300 hover:border-emerald-400 hover:bg-gray-50'}
        `}
        onDragEnter={handleDrag}
        onDragLeave={handleDrag}
        onDragOver={handleDrag}
        onDrop={handleDrop}
        onClick={() => inputRef.current?.click()}
      >
        <input 
          type="file" 
          ref={inputRef}
          className="hidden" 
          accept="image/*"
          onChange={(e) => e.target.files?.[0] && onFileSelect(e.target.files[0])} 
        />
        
        <div className="z-10 flex flex-col items-center gap-6 p-8">
          <div className={`p-6 rounded-full ${isDragging ? 'bg-emerald-200' : 'bg-gray-100'} transition-colors`}>
            <Upload size={48} className={isDragging ? 'text-emerald-700' : 'text-gray-400'} />
          </div>
          <div className="space-y-2">
            <p className="text-2xl font-semibold text-gray-700">
              {isDragging ? 'Drop it here!' : 'Drag & Drop your image'}
            </p>
            <p className="text-gray-400">or click to browse from device</p>
          </div>
        </div>
      </div>
    </div>
  );
};

const ScanningView = ({ image }) => {
  return (
    <div className="min-h-screen bg-gray-900 flex flex-col items-center justify-center p-6 relative overflow-hidden">
      <div className="w-full max-w-lg relative rounded-2xl overflow-hidden shadow-2xl border border-gray-700">
        <img src={URL.createObjectURL(image)} alt="Analyzing" className="w-full h-auto opacity-60" />
        
        {/* Scanning Overlay */}
        <div className="absolute inset-0 bg-gradient-to-b from-emerald-500/20 to-transparent animate-scan z-10 border-b-2 border-emerald-400 shadow-[0_0_20px_rgba(52,211,153,0.5)]"></div>
        
        {/* Grid Overlay */}
        <div className="absolute inset-0 bg-[url('https://grainy-gradients.vercel.app/noise.svg')] opacity-20"></div>
        <div className="absolute inset-0 grid grid-cols-4 grid-rows-4 gap-px">
           {Array.from({ length: 16 }).map((_, i) => (
             <div key={i} className="border border-emerald-500/10" />
           ))}
        </div>

        {/* HUD Elements */}
        <div className="absolute top-4 left-4 text-emerald-400 font-mono text-xs flex items-center gap-2">
           <Activity size={14} className="animate-pulse" />
           PROCESSING...
        </div>
        <div className="absolute bottom-4 right-4 text-emerald-400 font-mono text-xs">
           AI MODEL V2.4
        </div>
      </div>
      
      <div className="mt-8 space-y-4 text-center max-w-md">
        <h3 className="text-2xl font-bold text-white animate-pulse">Analyzing Crop Health...</h3>
        <p className="text-gray-400 text-sm">Identifying pathogens, checking leaf texture, and calculating chlorophyll density.</p>
        
        <div className="w-full bg-gray-800 h-2 rounded-full overflow-hidden">
          <div className="h-full bg-emerald-500 animate-progress origin-left"></div>
        </div>
      </div>
    </div>
  );
};

const ResultsDashboard = ({ data, image, onReset }) => {
  const [activeTab, setActiveTab] = useState('diagnosis');

  return (
    <div className="min-h-screen bg-gray-50 pt-20 pb-12 px-4">
      <div className="container mx-auto max-w-6xl">
        
        {/* Header Summary */}
        <div className="flex flex-col lg:flex-row gap-8 mb-10">
          <div className="w-full lg:w-1/3">
             <div className="relative rounded-2xl overflow-hidden shadow-xl group">
                <img 
                  src={URL.createObjectURL(image)} 
                  alt="Analyzed Plant" 
                  className="w-full h-80 object-cover transform group-hover:scale-110 transition-transform duration-500" 
                />
                <div className="absolute bottom-0 left-0 right-0 bg-gradient-to-t from-black/80 to-transparent p-6">
                  <p className="text-emerald-400 font-medium text-sm mb-1 uppercase tracking-wider">Detected Species</p>
                  <h3 className="text-white text-2xl font-bold">{data.plantType}</h3>
                </div>
             </div>
          </div>

          <div className="w-full lg:w-2/3 grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className={`p-6 rounded-2xl text-white flex flex-col justify-between ${data.healthScore > 80 ? 'bg-emerald-500' : data.healthScore > 40 ? 'bg-amber-500' : 'bg-red-500'}`}>
               <div className="flex justify-between items-start">
                 <div>
                   <p className="opacity-90 font-medium">Overall Health</p>
                   <h2 className="text-4xl font-bold mt-1">{data.healthScore}%</h2>
                 </div>
                 <Activity size={32} className="opacity-50" />
               </div>
               <p className="mt-4 font-medium opacity-90 flex items-center gap-2">
                 Status: {data.status}
               </p>
            </div>

            <div className="bg-white p-6 rounded-2xl shadow-sm border border-gray-100 flex flex-col justify-between">
               <div>
                 <p className="text-gray-500 font-medium text-sm uppercase">Main Diagnosis</p>
                 <h2 className="text-2xl font-bold text-gray-900 mt-1">{data.diagnosis.condition}</h2>
               </div>
               <div className="mt-4">
                 <div className="flex justify-between text-sm mb-2">
                    <span className="text-gray-600">Confidence</span>
                    <span className="font-bold text-emerald-600">{(data.diagnosis.probability * 100).toFixed(0)}%</span>
                 </div>
                 <div className="w-full bg-gray-100 h-2 rounded-full overflow-hidden">
                   <div className="h-full bg-emerald-500" style={{ width: `${data.diagnosis.probability * 100}%` }}></div>
                 </div>
               </div>
            </div>
          </div>
        </div>

        {/* Dashboard Content */}
        <div className="bg-white rounded-3xl shadow-xl border border-gray-100 overflow-hidden">
          <div className="flex border-b border-gray-100">
            {['diagnosis', 'treatment', 'nutrition'].map((tab) => (
              <button
                key={tab}
                onClick={() => setActiveTab(tab)}
                className={`flex-1 py-5 font-medium text-sm uppercase tracking-wider transition-colors relative
                  ${activeTab === tab ? 'text-emerald-600 bg-emerald-50/50' : 'text-gray-500 hover:text-gray-800'}
                `}
              >
                {tab}
                {activeTab === tab && <div className="absolute bottom-0 left-0 w-full h-1 bg-emerald-500" />}
              </button>
            ))}
          </div>

          <div className="p-8 min-h-[400px]">
            {activeTab === 'diagnosis' && (
              <div className="space-y-6 animate-fade-in">
                {data.lowConfidence && (
                  <div className="flex items-start gap-3 p-4 bg-amber-50 rounded-xl border border-amber-200 text-amber-800">
                    <AlertCircle className="shrink-0 mt-0.5" size={20} />
                    <p>The model is not very confident about this image. For best results, upload a clear photo of a single leaf on a plain background.</p>
                  </div>
                )}
                {data.diagnosis.isHealthy ? (
                  <div className="flex items-start gap-4 p-4 bg-emerald-50 rounded-xl border border-emerald-100">
                    <CheckCircle2 className="text-emerald-500 shrink-0 mt-1" />
                    <div>
                      <h4 className="font-bold text-emerald-900 text-lg">No Disease Detected</h4>
                      <p className="text-emerald-700 mt-1 leading-relaxed">{data.diagnosis.description}</p>
                    </div>
                  </div>
                ) : (
                  <div className="flex items-start gap-4 p-4 bg-red-50 rounded-xl border border-red-100">
                    <AlertCircle className="text-red-500 shrink-0 mt-1" />
                    <div>
                      <h4 className="font-bold text-red-900 text-lg">{data.diagnosis.label} Detected</h4>
                      <p className="text-red-700 mt-1 leading-relaxed">{data.diagnosis.description}</p>
                    </div>
                  </div>
                )}
                
                <div className="grid md:grid-cols-3 gap-6 mt-8">
                   <div className="p-4 bg-gray-50 rounded-xl border border-gray-100 text-center">
                      <Thermometer className="mx-auto text-gray-400 mb-2" />
                      <p className="text-sm text-gray-500">Severity</p>
                      <p className="font-bold text-lg text-amber-600">{data.diagnosis.severity}</p>
                   </div>
                   <div className="p-4 bg-gray-50 rounded-xl border border-gray-100 text-center">
                      <ScanLine className="mx-auto text-gray-400 mb-2" />
                      <p className="text-sm text-gray-500">Cause</p>
                      <p className="font-bold text-lg text-gray-800 capitalize">{data.diagnosis.isHealthy ? 'None' : data.diagnosis.type}</p>
                   </div>
                   <div className="p-4 bg-gray-50 rounded-xl border border-gray-100 text-center">
                      <Wind className="mx-auto text-gray-400 mb-2" />
                      <p className="text-sm text-gray-500">Spread Risk</p>
                      <p className={`font-bold text-lg ${data.diagnosis.spreadRisk === 'High' ? 'text-red-600' : data.diagnosis.spreadRisk === 'None' ? 'text-emerald-600' : 'text-amber-600'}`}>{data.diagnosis.spreadRisk}</p>
                   </div>
                </div>

                {data.topPredictions?.length > 0 && (
                  <div className="mt-8">
                    <h4 className="font-bold text-gray-900 mb-4">Top Predictions</h4>
                    <div className="space-y-3">
                      {data.topPredictions.map((p) => (
                        <div key={p.label}>
                          <div className="flex justify-between text-sm mb-1">
                            <span className="text-gray-700">{p.label}</span>
                            <span className="font-semibold text-gray-900">{(p.probability * 100).toFixed(1)}%</span>
                          </div>
                          <div className="w-full bg-gray-100 h-2 rounded-full overflow-hidden">
                            <div className="h-full bg-emerald-500" style={{ width: `${p.probability * 100}%` }}></div>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            )}

            {activeTab === 'treatment' && (
              <div className="space-y-6 animate-fade-in">
                <h3 className="text-xl font-bold text-gray-900 mb-4">Recommended Actions</h3>
                
                <div className="grid md:grid-cols-2 gap-6">
                  {/* Water Card */}
                  <div className="bg-blue-50 p-6 rounded-2xl border border-blue-100 relative overflow-hidden">
                    <Droplets className="absolute top-[-20px] right-[-20px] text-blue-200 w-32 h-32" />
                    <div className="relative z-10">
                      <h4 className="font-bold text-blue-900 text-lg flex items-center gap-2">
                        <Droplets size={20} /> Irrigation Adjustment
                      </h4>
                      <p className="mt-2 text-blue-800 font-medium">Current: {data.requirements.water.current}</p>
                      <p className="mt-4 text-sm text-blue-700 bg-white/60 p-3 rounded-lg backdrop-blur-sm">
                        {data.requirements.water.advice}
                      </p>
                    </div>
                  </div>

                  {/* Sun Card */}
                  <div className="bg-orange-50 p-6 rounded-2xl border border-orange-100 relative overflow-hidden">
                    <Sun className="absolute top-[-20px] right-[-20px] text-orange-200 w-32 h-32" />
                    <div className="relative z-10">
                      <h4 className="font-bold text-orange-900 text-lg flex items-center gap-2">
                        <Sun size={20} /> Light Exposure
                      </h4>
                      <p className="mt-2 text-orange-800 font-medium">Status: {data.requirements.sunlight.current}</p>
                      <p className="mt-4 text-sm text-orange-700 bg-white/60 p-3 rounded-lg backdrop-blur-sm">
                        {data.requirements.sunlight.advice}
                      </p>
                    </div>
                  </div>
                </div>

                <div className="bg-gray-50 p-6 rounded-xl border border-gray-200 mt-6">
                  <h4 className="font-bold text-gray-900 mb-2">Treatment</h4>
                  <p className="text-gray-600 leading-relaxed">{data.diagnosis.treatment}</p>
                  <h4 className="font-bold text-gray-900 mt-5 mb-2">Prevention</h4>
                  <p className="text-gray-600 leading-relaxed">{data.diagnosis.prevention}</p>
                </div>
              </div>
            )}

            {activeTab === 'nutrition' && (
              <div className="animate-fade-in">
                <div className="flex justify-between items-center mb-6">
                  <h3 className="text-xl font-bold text-gray-900">NPK Guidance</h3>
                  <span className="text-sm bg-emerald-100 text-emerald-800 px-3 py-1 rounded-full font-medium">General guidance for this condition</span>
                </div>

                <div className="space-y-6">
                   {/* Nitrogen */}
                   <div>
                     <div className="flex justify-between mb-2">
                       <span className="font-medium text-gray-700">Nitrogen (N)</span>
                       <span className="text-red-500 font-bold">{data.requirements.fertilizer.n.level}</span>
                     </div>
                     <div className="h-4 bg-gray-100 rounded-full overflow-hidden relative">
                       {/* Target Marker */}
                       <div className="absolute top-0 bottom-0 w-1 bg-black z-10 opacity-20" style={{ left: `${data.requirements.fertilizer.n.recommended}%` }}></div>
                       {/* Actual Bar */}
                       <div className="h-full bg-red-400 rounded-full" style={{ width: `${data.requirements.fertilizer.n.value}%` }}></div>
                     </div>
                     <p className="text-xs text-gray-400 mt-1 text-right">Target: {data.requirements.fertilizer.n.recommended} ppm</p>
                   </div>

                   {/* Phosphorus */}
                   <div>
                     <div className="flex justify-between mb-2">
                       <span className="font-medium text-gray-700">Phosphorus (P)</span>
                       <span className="text-emerald-500 font-bold">{data.requirements.fertilizer.p.level}</span>
                     </div>
                     <div className="h-4 bg-gray-100 rounded-full overflow-hidden relative">
                        <div className="absolute top-0 bottom-0 w-1 bg-black z-10 opacity-20" style={{ left: `${data.requirements.fertilizer.p.recommended}%` }}></div>
                        <div className="h-full bg-emerald-500 rounded-full" style={{ width: `${data.requirements.fertilizer.p.value}%` }}></div>
                     </div>
                     <p className="text-xs text-gray-400 mt-1 text-right">Target: {data.requirements.fertilizer.p.recommended} ppm</p>
                   </div>

                   {/* Potassium */}
                   <div>
                     <div className="flex justify-between mb-2">
                       <span className="font-medium text-gray-700">Potassium (K)</span>
                       <span className="text-amber-500 font-bold">{data.requirements.fertilizer.k.level}</span>
                     </div>
                     <div className="h-4 bg-gray-100 rounded-full overflow-hidden relative">
                        <div className="absolute top-0 bottom-0 w-1 bg-black z-10 opacity-20" style={{ left: `${data.requirements.fertilizer.k.recommended}%` }}></div>
                        <div className="h-full bg-amber-400 rounded-full" style={{ width: `${data.requirements.fertilizer.k.value}%` }}></div>
                     </div>
                     <p className="text-xs text-gray-400 mt-1 text-right">Target: {data.requirements.fertilizer.k.recommended} ppm</p>
                   </div>
                </div>

                <div className="mt-8 p-5 bg-gradient-to-r from-emerald-600 to-teal-600 rounded-xl text-white shadow-lg">
                  <h4 className="font-bold flex items-center gap-2 mb-2">
                    <Sprout size={20} /> Recommended Fertilizer Mix
                  </h4>
                  <p className="opacity-90">{data.requirements.fertilizer.recommendation}</p>
                </div>
              </div>
            )}
          </div>
        </div>

        <div className="mt-8 flex justify-center">
          <button 
            onClick={onReset}
            className="flex items-center gap-2 text-gray-500 hover:text-emerald-600 font-medium transition-colors px-6 py-3 rounded-full hover:bg-white"
          >
            <ArrowRight className="rotate-180" size={18} />
            Scan Another Plant
          </button>
        </div>

      </div>
    </div>
  );
};


// --- Main App Component ---
export default function App() {
  const [view, setView] = useState('landing'); // landing, upload, scanning, results
  const [selectedImage, setSelectedImage] = useState(null);
  const [analysisData, setAnalysisData] = useState(null);
  const [error, setError] = useState(null);

  const handleStart = () => setView('upload');

  const handleFileSelect = async (file) => {
    setSelectedImage(file);
    setError(null);
    setView('scanning');

    try {
      const data = await analyzePlantImage(file);
      setAnalysisData(data);
      setView('results');
    } catch (err) {
      setError(err.message || 'Could not reach the server at http://localhost:8000');
      setSelectedImage(null);
      setView('upload');
    }
  };

  const handleReset = () => {
    setSelectedImage(null);
    setAnalysisData(null);
    setError(null);
    setView('upload');
  };

  return (
    <div className="font-sans text-gray-900 bg-white min-h-screen selection:bg-emerald-200 selection:text-emerald-900">
      <Header />
      
      <main>
        {view === 'landing' && <Hero onStart={handleStart} />}
        
        {view === 'upload' && (
          <div className="animate-fade-in">
             <UploadArea onFileSelect={handleFileSelect} error={error} />
          </div>
        )}

        {view === 'scanning' && selectedImage && (
          <ScanningView image={selectedImage} />
        )}

        {view === 'results' && analysisData && selectedImage && (
          <ResultsDashboard 
            data={analysisData} 
            image={selectedImage} 
            onReset={handleReset} 
          />
        )}
      </main>

      {/* Global CSS for custom animations that Tailwind doesn't include by default */}
      <style>{`
        @keyframes scan {
          0% { top: 0%; opacity: 0; }
          10% { opacity: 1; }
          90% { opacity: 1; }
          100% { top: 100%; opacity: 0; }
        }
        .animate-scan {
          animation: scan 2.5s cubic-bezier(0.4, 0, 0.2, 1) infinite;
        }
        @keyframes fade-in-up {
          from { opacity: 0; transform: translateY(20px); }
          to { opacity: 1; transform: translateY(0); }
        }
        .animate-fade-in-up {
          animation: fade-in-up 0.8s ease-out forwards;
        }
        @keyframes progress {
          from { transform: scaleX(0); }
          to { transform: scaleX(1); }
        }
        .animate-progress {
          animation: progress 3.5s ease-out forwards;
        }
      `}</style>
    </div>
  );
}