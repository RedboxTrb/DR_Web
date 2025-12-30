import { LocationData } from './locationService';

export interface Hospital {
  id: string;
  name: string;
  address: string;
  distance: string;
  rating?: number;
  phone?: string;
  latitude: number;
  longitude: number;
}

export async function findNearbyEyeHospitals(location: LocationData): Promise<Hospital[]> {
  return getSearchSuggestions(location);
}

function calculateDistance(lat1: number, lon1: number, lat2: number, lon2: number): number {
  const R = 6371;
  const dLat = toRad(lat2 - lat1);
  const dLon = toRad(lon2 - lon1);
  const a =
    Math.sin(dLat / 2) * Math.sin(dLat / 2) +
    Math.cos(toRad(lat1)) * Math.cos(toRad(lat2)) *
    Math.sin(dLon / 2) * Math.sin(dLon / 2);
  const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));
  return R * c;
}

function toRad(degrees: number): number {
  return degrees * (Math.PI / 180);
}

function getSearchSuggestions(location: LocationData): Hospital[] {
  const cityName = location.city || 'your area';
  const hasLocation = location.latitude !== 0 && location.longitude !== 0;

  return [
    {
      id: 'search-1',
      name: 'Eye Hospitals',
      address: hasLocation ? `Find eye hospitals in ${cityName}` : 'Search for eye hospitals nearby',
      distance: 'Nearby',
      latitude: location.latitude,
      longitude: location.longitude
    },
    {
      id: 'search-2',
      name: 'Ophthalmology Clinics',
      address: hasLocation ? `Find clinics in ${cityName}` : 'Search for ophthalmology clinics nearby',
      distance: 'Nearby',
      latitude: location.latitude,
      longitude: location.longitude
    },
    {
      id: 'search-3',
      name: 'Retina Specialists',
      address: hasLocation ? `Find specialists in ${cityName}` : 'Search for retina specialists nearby',
      distance: 'Nearby',
      latitude: location.latitude,
      longitude: location.longitude
    }
  ];
}
