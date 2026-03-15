import React, { useState } from 'react';
import { X, Check, Store, Loader2, ArrowRight, Image as ImageIcon } from 'lucide-react';
import api from '../../api';
import ImageUpload from '../ui/ImageUpload';

interface CreateOutletModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSuccess: () => void;
}

const CreateOutletModal = ({ isOpen, onClose, onSuccess }: CreateOutletModalProps) => {
  const [step, setStep] = useState(1);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  
  const [name, setName] = useState('');
  const [coverImage, setCoverImage] = useState<File | null>(null);
  const [sliderImages, setSliderImages] = useState<File[]>([]);

  if (!isOpen) return null;

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (step === 1) {
      setStep(2);
      return;
    }

    setLoading(true);
    setError('');

    const formData = new FormData();
    formData.append('name', name);
    if (coverImage) {
      formData.append('cover_image', coverImage);
    }
    sliderImages.forEach((file) => {
      formData.append('mid_page_slider', file);
    });

    try {
      await api.post('/protected/restaurant/outlet', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });
      onSuccess();
      onClose();
      // Reset
      setStep(1);
      setName('');
      setCoverImage(null);
      setSliderImages([]);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to create outlet. Ensure all fields are valid.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 z-[100] flex items-center justify-center p-4 bg-slate-900/40 backdrop-blur-sm animate-in fade-in duration-300">
      <div className="w-full max-w-2xl bg-white rounded-[2.5rem] shadow-2xl border border-slate-200 overflow-hidden animate-in zoom-in-95 duration-300">
        
        {/* Header */}
        <div className="px-8 py-6 border-b border-slate-100 flex items-center justify-between bg-slate-50/50">
          <div>
            <h2 className="text-2xl font-brand font-bold text-slate-900">Deploy New Outlet</h2>
            <p className="text-slate-500 text-sm mt-1">Step {step} of 2: {step === 1 ? 'Metadata' : 'Visual Identity'}</p>
          </div>
          <button onClick={onClose} className="p-2 hover:bg-white hover:shadow-md rounded-xl text-slate-400 transition-all">
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Progress Bar */}
        <div className="h-1.5 w-full bg-slate-100 flex">
          <div className={`h-full bg-orange-500 transition-all duration-500 ${step === 1 ? 'w-1/2' : 'w-full'}`} />
        </div>

        <form onSubmit={handleSubmit} className="p-8">
          {error && (
            <div className="mb-6 p-4 bg-rose-50 text-rose-600 rounded-2xl text-sm border border-rose-100 flex items-center gap-3">
              <div className="w-2 h-2 rounded-full bg-rose-500" />
              {error}
            </div>
          )}

          {step === 1 ? (
            <div className="space-y-6">
              <div className="space-y-2">
                <label className="text-[10px] font-black text-slate-400 uppercase tracking-widest ml-1">Outlet Name</label>
                <div className="relative">
                  <Store className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-slate-300" />
                  <input 
                    type="text"
                    required
                    value={name}
                    onChange={(e) => setName(e.target.value)}
                    placeholder="e.g. Main Street Kitchen"
                    className="w-full pl-12 pr-4 py-4 rounded-2xl border border-slate-200 bg-slate-50/30 focus:outline-none focus:ring-4 focus:ring-orange-500/10 transition-all font-medium"
                  />
                </div>
                <p className="text-[10px] text-slate-400 ml-1">This will also generate your public URL slug.</p>
              </div>

              <div className="p-6 bg-orange-50/50 rounded-[2rem] border border-orange-100/50">
                 <h4 className="text-sm font-bold text-orange-800 mb-2">Location Strategy</h4>
                 <p className="text-xs text-orange-600/80 leading-relaxed">
                    Choose a distinct name for each location. This name will be the primary identifier for customers in the digital storefront.
                 </p>
              </div>

              <button 
                type="submit"
                className="w-full py-4 bg-slate-900 text-white rounded-2xl font-bold flex items-center justify-center gap-2 orange-glow tactile"
              >
                Continue to Visuals
                <ArrowRight className="w-5 h-5" />
              </button>
            </div>
          ) : (
            <div className="space-y-8">
              <ImageUpload 
                label="Primary Cover Image" 
                onFilesSelected={(files) => setCoverImage(files[0])} 
              />

              <ImageUpload 
                label="Atmosphere Slider (Multiple)" 
                multiple 
                maxFiles={10}
                onFilesSelected={(files) => setSliderImages(prev => [...prev, ...files])} 
              />

              <div className="flex gap-3 pt-4">
                <button 
                  type="button"
                  onClick={() => setStep(1)}
                  className="flex-1 py-4 glass text-slate-600 rounded-2xl font-bold border border-slate-200 tactile"
                >
                  Back
                </button>
                <button 
                  type="submit"
                  disabled={loading}
                  className="flex-[2] py-4 bg-orange-500 text-white rounded-2xl font-bold flex items-center justify-center gap-2 orange-glow tactile disabled:opacity-50"
                >
                  {loading ? <Loader2 className="w-5 h-5 animate-spin" /> : (
                    <>
                      Deploy Outlet
                      <Check className="w-5 h-5" />
                    </>
                  )}
                </button>
              </div>
            </div>
          )}
        </form>
      </div>
    </div>
  );
};

export default CreateOutletModal;
