export interface Appointment {
  id: string;
  name: string;
  date: string; // ISO date string
  files: FileData[];
}

export interface FileData {
  id: string;
  filename: string;
  content_type: string;
  size: number;
  download_url: string;
} 