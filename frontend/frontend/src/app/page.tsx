import FileUploader from '../components/FileUploader';

export default function Home() {
  return (
    <main className="flex min-h-screen flex-col items-center justify-center p-24 bg-gray-50">
      <div className="w-full max-w-2xl">
        <header className="text-center mb-8">
          <h1 className="text-4xl font-bold text-gray-800">File Uploader</h1>
          <p className="text-gray-600 mt-2">
            Upload large files with ease using chunking and background processing.
          </p>
        </header>
        <FileUploader />
      </div>
    </main>
  );
}