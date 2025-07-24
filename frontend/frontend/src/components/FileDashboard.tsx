import { useState, useEffect } from 'react';
import FileUploader from './FileUploader';

const API_BASE_URL = 'http://localhost:8000/api/v1/file';

interface FileData {
  id: string;
  path: string;
  download_url: string;
}

interface FileDashboardProps {
  appointment: string;
  onLogout: () => void;
}

export default function FileDashboard({ appointment, onLogout }: FileDashboardProps) {
  const [files, setFiles] = useState<FileData[]>([]);

  const fetchFiles = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/appointment/${appointment}`);
      const result = await response.json();
      if (result.success) {
        setFiles(result.data);
      }
    } catch (error) {
      console.error('Failed to fetch files:', error);
    }
  };

  const handleUploadSuccess = (newFile: FileData) => {
    setFiles((prevFiles) => [...prevFiles, newFile]);
  };

  const handleDelete = async (fileId: string) => {
    try {
      await fetch(`${API_BASE_URL}/${fileId}`, { method: 'DELETE' });
      setFiles((prevFiles) => prevFiles.filter((file) => file.id !== fileId));
    } catch (error) {
      console.error('Failed to delete file:', error);
    }
  };

  useEffect(() => {
    fetchFiles();
  }, [appointment]);

  return (
    <div className="container mx-auto p-8">
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-3xl font-bold">Appointment: {appointment}</h1>
        <button onClick={onLogout} className="px-4 py-2 font-semibold text-white bg-red-600 rounded-md hover:bg-red-700">
          Logout
        </button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
        <div>
          <h2 className="text-2xl font-semibold mb-4">Upload New File</h2>
          <FileUploader appointment={appointment} onUploadSuccess={handleUploadSuccess} />
        </div>
        <div>
          <h2 className="text-2xl font-semibold mb-4">Existing Files</h2>
          <div className="space-y-3">
            {files.length > 0 ? (
              files.map((file) => (
                <div key={file.id} className="flex items-center justify-between p-3 bg-gray-100 rounded-md">
                  <a href={file.download_url} target="_blank" rel="noopener noreferrer" className="text-blue-600 hover:underline truncate">
                    {file.path.split('/').pop()}
                  </a>
                  <button onClick={() => handleDelete(file.id)} className="text-red-500 hover:text-red-700">
                    Remove
                  </button>
                </div>
              ))
            ) : (
              <p className="text-gray-500">No files found for this appointment.</p>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
