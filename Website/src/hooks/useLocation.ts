import { useState, useEffect } from 'react';
import { getUserLocation, LocationData } from '../services/locationService';

export function useLocation() {
  const [location, setLocation] = useState<LocationData | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let mounted = true;

    const loadLocation = async () => {
      try {
        const loc = await getUserLocation();
        if (mounted) {
          setLocation(loc);
        }
      } catch (error) {
        // Location fetch failed
      } finally {
        if (mounted) {
          setLoading(false);
        }
      }
    };

    loadLocation();

    return () => {
      mounted = false;
    };
  }, []);

  return { location, loading };
}
