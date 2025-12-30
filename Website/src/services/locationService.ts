export interface LocationData {
  latitude: number;
  longitude: number;
  city?: string;
  country?: string;
  source: 'browser' | 'ip';
}

export async function getUserLocation(): Promise<LocationData> {
  try {
    const position = await new Promise<GeolocationPosition>((resolve, reject) => {
      if (!navigator.geolocation) {
        reject(new Error('Geolocation not supported'));
        return;
      }

      navigator.geolocation.getCurrentPosition(resolve, reject, {
        timeout: 5000,
        enableHighAccuracy: false
      });
    });

    return {
      latitude: position.coords.latitude,
      longitude: position.coords.longitude,
      source: 'browser'
    };
  } catch (error) {
    return getLocationFromIP();
  }
}

async function getLocationFromIP(): Promise<LocationData> {
  try {
    const response = await fetch('https://ipapi.co/json/');
    const data = await response.json();

    if (data.latitude && data.longitude) {
      return {
        latitude: data.latitude,
        longitude: data.longitude,
        city: data.city,
        country: data.country_name,
        source: 'ip'
      };
    }
  } catch (error) {
    // Primary API failed, try secondary
  }

  try {
    const response = await fetch('http://ip-api.com/json/');
    const data = await response.json();

    if (data.lat && data.lon) {
      return {
        latitude: data.lat,
        longitude: data.lon,
        city: data.city,
        country: data.country,
        source: 'ip'
      };
    }
  } catch (error) {
    // Secondary API failed
  }

  return {
    latitude: 0,
    longitude: 0,
    city: undefined,
    country: undefined,
    source: 'ip'
  };
}
