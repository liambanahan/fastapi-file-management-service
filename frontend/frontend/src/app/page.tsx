"use client";

import { useState, useEffect } from 'react';
import FileDashboard from '../components/FileDashboard';
import { Appointment, FileData } from '../types';

const APPOINTMENTS_API_URL = 'http://localhost:8000/api/v1/appointments';
const FILES_API_URL = 'http://localhost:8000/api/v1/file/all';

export default function Home() {
  const [appointments, setAppointments] = useState<Appointment[]>([]);
  const [allFiles, setAllFiles] = useState<FileData[]>([]);
  const [selectedAppointment, setSelectedAppointment] = useState<Appointment | null>(null);
  const [newAppointmentName, setNewAppointmentName] = useState('');

  const fetchAppointments = async () => {
    try {
      const response = await fetch(APPOINTMENTS_API_URL);
      const result = await response.json();
      if (result.success) {
        setAppointments(result.data);
      }
    } catch (error) {
      console.error('Failed to fetch appointments:', error);
    }
  };

  const fetchAllFiles = async () => {
    try {
      const response = await fetch(FILES_API_URL);
      const result = await response.json();
      if (result.success) {
        setAllFiles(result.data);
      }
    } catch (error) {
      console.error('Failed to fetch all files:', error);
    }
  };

  useEffect(() => {
    fetchAppointments();
    fetchAllFiles();
  }, []);
  
  const handleCreateAppointment = async () => {
    if (!newAppointmentName.trim()) return;
    try {
      const response = await fetch(APPOINTMENTS_API_URL, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ name: newAppointmentName }),
      });
      const result = await response.json();
      if (result.success) {
        setAppointments([...appointments, result.data]);
        setNewAppointmentName(''); // Clear input
      }
    } catch (error) {
      console.error('Failed to create appointment:', error);
    }
  };

  const handleBack = () => {
    setSelectedAppointment(null);
    fetchAppointments();
    fetchAllFiles();
  };

  if (selectedAppointment) {
    return <FileDashboard appointment={selectedAppointment} onBack={handleBack} />;
  }

  return (
    <main className="min-h-screen bg-gray-100 dark:bg-gray-900 text-gray-900 dark:text-gray-100">
      <div className="container mx-auto p-4 sm:p-6 lg:p-8">
        <header className="text-center mb-12">
          <h1 className="text-4xl sm:text-5xl font-extrabold text-gray-800 dark:text-white">
            File Management Dashboard
          </h1>
          <p className="text-lg text-gray-500 dark:text-gray-400 mt-2">
            Organize your appointments and files with ease.
          </p>
        </header>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          
          {/* Left Column: Appointments */}
          <div className="bg-white dark:bg-gray-800 rounded-xl shadow-lg p-6">
            <h2 className="text-2xl font-bold text-gray-800 dark:text-white mb-6">Appointments</h2>
            <div className="space-y-4">
              {appointments.length > 0 ? (
                appointments.map((appt) => (
                  <div
                    key={appt.id}
                    onClick={() => setSelectedAppointment(appt)}
                    className="p-4 bg-gray-50 dark:bg-gray-700 border-l-4 border-transparent hover:border-blue-500 rounded-lg cursor-pointer transition-all duration-200 ease-in-out transform hover:scale-105"
                  >
                    <p className="font-semibold text-lg text-gray-800 dark:text-white">{appt.name}</p>
                    <p className="text-sm text-gray-500 dark:text-gray-400">{new Date(appt.date).toLocaleDateString()}</p>
                  </div>
                ))
              ) : (
                <p className="text-center text-gray-500 dark:text-gray-400 py-8">No appointments found.</p>
              )}
            </div>
            <div className="pt-6 border-t border-gray-200 dark:border-gray-700 mt-6">
              <h3 className="text-xl font-semibold text-gray-700 dark:text-gray-300 mb-4">Create New Appointment</h3>
              <div className="flex space-x-3">
                <input
                  type="text"
                  value={newAppointmentName}
                  onChange={(e) => setNewAppointmentName(e.target.value)}
                  placeholder="Enter appointment name"
                  className="flex-grow px-4 py-2 text-gray-800 dark:text-gray-200 bg-gray-100 dark:bg-gray-600 border border-gray-300 dark:border-gray-500 rounded-md focus:border-blue-500 focus:ring-blue-500 focus:outline-none focus:ring focus:ring-opacity-40"
                />
                <button
                  onClick={handleCreateAppointment}
                  className="px-6 py-2 font-semibold text-white bg-blue-600 rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-opacity-50 transition-colors"
                >
                  Add
                </button>
              </div>
            </div>
          </div>

          {/* Right Column: All Files */}
          <div className="bg-white dark:bg-gray-800 rounded-xl shadow-lg p-6">
            <h2 className="text-2xl font-bold text-gray-800 dark:text-white mb-6">All Files</h2>
            <div className="space-y-3">
              {allFiles.length > 0 ? (
                allFiles.map((file) => (
                  <div key={file.id} className="flex items-center justify-between p-3 bg-gray-50 dark:bg-gray-700 rounded-lg border border-gray-200 dark:border-gray-600">
                    <div className="flex flex-col min-w-0 flex-1">
                      <span className="font-medium truncate text-gray-700 dark:text-gray-300" title={file.filename}>{file.filename}</span>
                      {file.appointment_name && (
                        <span className="text-sm text-gray-500 dark:text-gray-400 truncate" title={`From appointment: ${file.appointment_name}`}>
                          From: {file.appointment_name}
                        </span>
                      )}
                    </div>
                    <a href={file.download_url} target="_blank" rel="noopener noreferrer" className="text-blue-600 hover:text-blue-500 dark:text-blue-400 dark:hover:text-blue-300 font-semibold text-sm transition-colors ml-3">
                      Download
                    </a>
                  </div>
                ))
              ) : (
                <p className="text-center text-gray-500 dark:text-gray-400 py-8">No files uploaded yet.</p>
              )}
            </div>
          </div>

        </div>
      </div>
    </main>
  );
}