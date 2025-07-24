"use client";

import { useState } from 'react';
import FileDashboard from '../components/FileDashboard';

// Hardcoded list of valid appointments
const VALID_APPOINTMENTS = ['subash', 'appointment2', 'appointment3'];

export default function Home() {
  const [appointment, setAppointment] = useState<string>('');
  const [loggedInAppointment, setLoggedInAppointment] = useState<string | null>(null);
  const [error, setError] = useState<string>('');

  const handleLogin = () => {
    if (VALID_APPOINTMENTS.includes(appointment)) {
      setLoggedInAppointment(appointment);
      setError('');
    } else {
      setError('Not an appointment');
      // Hide the error message after 3 seconds
      setTimeout(() => setError(''), 3000);
    }
  };

  const handleLogout = () => {
    setLoggedInAppointment(null);
    setAppointment('');
  };

  if (loggedInAppointment) {
    return <FileDashboard appointment={loggedInAppointment} onLogout={handleLogout} />;
  }

  return (
    <main className="flex min-h-screen flex-col items-center justify-center p-24 bg-gray-50">
      <div className="w-full max-w-md p-8 space-y-6 bg-white rounded-lg shadow-md">
        <h1 className="text-2xl font-bold text-center text-gray-800">Enter Appointment Name</h1>
        <div className="relative">
          <input
            type="text"
            value={appointment}
            onChange={(e) => setAppointment(e.target.value)}
            onKeyPress={(e) => e.key === 'Enter' && handleLogin()}
            placeholder="e.g., appointment1"
            className="w-full px-4 py-2 text-gray-700 bg-gray-100 border rounded-md focus:border-blue-500 focus:ring-blue-500 focus:outline-none focus:ring focus:ring-opacity-40"
          />
          {error && <p className="absolute text-sm text-red-600 -bottom-6 left-0">{error}</p>}
        </div>
        <button
          onClick={handleLogin}
          className="w-full px-4 py-2 font-semibold text-white bg-blue-600 rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-opacity-50"
        >
          Enter
        </button>
      </div>
    </main>
  );
}