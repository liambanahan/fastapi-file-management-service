'use client';

import { useState, ChangeEvent, useRef } from 'react';

// Define the structure of the API responses
interface UploadInitResponse {
  data: {
    chunk_size: number;
    upload_id: string;
  };
}

interface UploadCompleteResponse {
  data: {
    id: string;
    path: string;
    download_url: string;
  };
}

interface FileUploaderProps {
  appointment: string;
  onUploadSuccess: (newFile: UploadCompleteResponse['data']) => void;
}

const API_BASE_URL = 'http://localhost:8000/api/v1/file';

export default function FileUploader({ appointment, onUploadSuccess }: FileUploaderProps) {
  const [file, setFile] = useState<File | null>(null);
  const [progress, setProgress] = useState(0);
  const [status, setStatus] = useState('Please select a file to upload.');
  const [uploadedFile, setUploadedFile] = useState<UploadCompleteResponse['data'] | null>(null);
  const [isUploading, setIsUploading] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleFileChange = (e: ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      setFile(e.target.files[0]);
      setStatus(`Selected file: ${e.target.files[0].name}`);
      setProgress(0);
      setUploadedFile(null);
    }
  };

  const handleUpload = async () => {
    if (!file) {
      setStatus('Please select a file first.');
      return;
    }

    setIsUploading(true);
    setUploadedFile(null);
    setProgress(0);

    try {
      // 1. Initialize Upload
      setStatus('Initializing upload...');
      const initResponse = await fetch(`${API_BASE_URL}/upload/init/`, { method: 'POST' });
      if (!initResponse.ok) throw new Error('Failed to initialize upload.');
      const initJson: UploadInitResponse = await initResponse.json();
      const { chunk_size, upload_id } = initJson.data;

      // 2. Upload Chunks
      const totalChunks = Math.ceil(file.size / chunk_size);
      for (let i = 0; i < totalChunks; i++) {
        const start = i * chunk_size;
        const end = Math.min(start + chunk_size, file.size);
        const chunk = file.slice(start, end);

        const formData = new FormData();
        formData.append('chunk_size', chunk.size.toString());
        formData.append('upload_id', upload_id);
        formData.append('chunk_index', i.toString());
        formData.append('file', chunk, file.name);
        
        setStatus(`Uploading chunk ${i + 1} of ${totalChunks}...`);
        
        const chunkResponse = await fetch(`${API_BASE_URL}/upload/chunk/`, {
          method: 'POST',
          body: formData,
        });

        if (!chunkResponse.ok) {
           const errorData = await chunkResponse.json();
           throw new Error(`Failed to upload chunk ${i + 1}: ${errorData.message || 'Unknown error'}`);
        }
        
        setProgress(Math.round(((i + 1) / totalChunks) * 100));
      }

      // 3. Complete Upload
      setStatus('Completing upload...');
      const completeFormData = new FormData();
      const fileExtension = file.name.split('.').pop() || '';
      completeFormData.append('upload_id', upload_id);
      completeFormData.append('total_chunks', totalChunks.toString());
      completeFormData.append('total_size', file.size.toString());
      completeFormData.append('file_extension', fileExtension);
      completeFormData.append('content_type', file.type);
      completeFormData.append('appointment', appointment); // Add this line
      
      const completeResponse = await fetch(`${API_BASE_URL}/upload/complete/`, {
        method: 'POST',
        body: completeFormData,
      });

      if (!completeResponse.ok) throw new Error('Failed to complete upload.');

      const completeJson: UploadCompleteResponse = await completeResponse.json();
      setUploadedFile(completeJson.data);
      setStatus('Upload successful! Your file is being processed.');
      onUploadSuccess(completeJson.data); // Call the callback with the new file data

    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'An unknown error occurred.';
      setStatus(`Error: ${errorMessage}`);
      setProgress(0);
    } finally {
      setIsUploading(false);
    }
  };

  const triggerFileSelect = () => fileInputRef.current?.click();

  return (
    <div className="bg-white p-8 rounded-lg shadow-md border border-gray-200">
      <input
        type="file"
        ref={fileInputRef}
        onChange={handleFileChange}
        className="hidden"
        disabled={isUploading}
      />

      <div 
        className="border-2 border-dashed border-gray-300 rounded-lg p-8 text-center cursor-pointer hover:border-blue-500 transition-colors"
        onClick={triggerFileSelect}
      >
        <p className="text-gray-500">{status}</p>
      </div>

      <div className="mt-6">
        <button
          onClick={handleUpload}
          disabled={!file || isUploading}
          className="w-full bg-blue-600 text-white font-bold py-3 px-4 rounded-lg hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed transition-colors"
        >
          {isUploading ? 'Uploading...' : 'Upload File'}
        </button>
      </div>

      {isUploading && (
        <div className="mt-4 w-full bg-gray-200 rounded-full h-2.5">
          <div
            className="bg-blue-600 h-2.5 rounded-full transition-all duration-300"
            style={{ width: `${progress}%` }}
          ></div>
        </div>
      )}

      {uploadedFile && (
        <div className="mt-6 p-4 bg-green-50 border border-green-200 rounded-lg text-center">
          <p className="font-semibold text-green-800">Processing Complete!</p>
          <p className="text-sm text-gray-600 mt-1">File ID: {uploadedFile.id}</p>
          <a
            href={uploadedFile.download_url}
            target="_blank"
            rel="noopener noreferrer"
            className="mt-2 inline-block text-blue-600 hover:underline"
          >
            Download File
          </a>
        </div>
      )}
    </div>
  );
}