import React, { useState, useRef } from 'react';
import { Upload, X, Image as ImageIcon, Plus } from 'lucide-react';

interface ImageUploadProps {
  label: string;
  multiple?: boolean;
  onFilesSelected: (files: File[]) => void;
  maxFiles?: number;
}

const ImageUpload = ({ label, multiple = false, onFilesSelected, maxFiles = 5 }: ImageUploadProps) => {
  const [previews, setPreviews] = useState<string[]>([]);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const selectedFiles = Array.from(e.target.files || []);
    if (selectedFiles.length === 0) return;

    // Limit files if needed
    const filesToProcess = multiple 
      ? selectedFiles.slice(0, maxFiles - previews.length) 
      : selectedFiles.slice(0, 1);

    const newPreviews = filesToProcess.map(file => URL.createObjectURL(file));
    
    if (multiple) {
      setPreviews(prev => [...prev, ...newPreviews]);
      onFilesSelected(filesToProcess);
    } else {
      setPreviews(newPreviews);
      onFilesSelected(filesToProcess);
    }
  };

  const removeImage = (index: number) => {
    setPreviews(prev => {
      const updated = [...prev];
      URL.revokeObjectURL(updated[index]);
      updated.splice(index, 1);
      return updated;
    });
    // In a real scenario, we'd also need to notify the parent to remove the file from its array
    // For simplicity here, we'll assume the parent handles the full state on submit or via another callback
  };

  return (
    <div className="space-y-3">
      <label className="text-[10px] font-black text-slate-400 uppercase tracking-widest ml-1">{label}</label>
      
      <div className="flex flex-wrap gap-4">
        {previews.map((src, idx) => (
          <div key={idx} className="relative w-32 h-32 rounded-2xl overflow-hidden border border-slate-200 group">
            <img src={src} alt="Preview" className="w-full h-full object-cover" />
            <button 
              type="button"
              onClick={() => removeImage(idx)}
              className="absolute top-2 right-2 p-1.5 bg-rose-500 text-white rounded-lg opacity-0 group-hover:opacity-100 transition-opacity shadow-lg"
            >
              <X className="w-3 h-3" />
            </button>
          </div>
        ))}

        {(multiple ? previews.length < maxFiles : previews.length === 0) && (
          <button
            type="button"
            onClick={() => fileInputRef.current?.click()}
            className="w-32 h-32 rounded-2xl border-2 border-dashed border-slate-200 bg-slate-50 flex flex-col items-center justify-center gap-2 text-slate-400 hover:border-orange-500/50 hover:bg-orange-500/5 transition-all group"
          >
            <div className="p-3 rounded-xl bg-white shadow-sm group-hover:scale-110 transition-transform">
               {multiple ? <Plus className="w-5 h-5" /> : <Upload className="w-5 h-5" />}
            </div>
            <span className="text-[10px] font-bold uppercase tracking-tighter">
               {multiple ? 'Add More' : 'Upload'}
            </span>
          </button>
        )}
      </div>

      <input 
        type="file" 
        ref={fileInputRef}
        onChange={handleFileChange}
        multiple={multiple}
        accept="image/*"
        className="hidden"
      />
    </div>
  );
};

export default ImageUpload;
