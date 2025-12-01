export interface WeatherLog {
  id: number;
  timestamp: string;
  city: string;
  temperature: number;
  humidity: number;
  pressure: number;
  wind_speed: number;
  condition: string;
  raw: any;
  created_at: string;
}
export interface WeatherListResponse {
  count: number;
  next: string | null;
  previous: string | null;  
  results: WeatherLog[];
}
export interface WeatherInsight {
  id: number;
  generated_at: string;
  text: string;
  city?: string;
}
export interface WeatherInsightsResponse {
  days: number;
  city: string | null;
  count: number;
  insights: string;
  next: string | null;
  previous: string | null;
  data: WeatherInsight[];
}
export interface WeatherTemperatureChartProps {
  data: {
    time: string;
    temperature: number;
    rain_probability: number;
  }[];
  isLoading?: boolean;
}
export interface WeatherTableProps {
  logs: WeatherLog[];
  isLoading: boolean;
  page: number;
  pageSize: number;
  totalCount: number;
  onPrevPage: () => void;
  onNextPage: () => void;
  selectedId?: number | null;
  onSelectLog?: (log: WeatherLog) => void;
}
export interface WeatherSummaryCardsProps {
  log: WeatherLog | null;
}
export interface WeatherInsightsCardProps {
  insights: string;
  isLoading: boolean;
}
export interface WeatherFilterBarProps {
  days: number;
  isLoading: boolean;
  isExporting: boolean;
  onDaysChange: (days: number) => void;
  onExportCsv: () => void;
  onExportXlsx: () => void;
}
