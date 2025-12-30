import { useState, useEffect } from 'react';
import { MapPin, ExternalLink, Loader2 } from 'lucide-react';
import { LocationData } from '../services/locationService';
import { findNearbyEyeHospitals, Hospital } from '../services/hospitalService';

interface HospitalRecommendationsProps {
  show: boolean;
  userLocation: LocationData | null;
}

export function HospitalRecommendations({ show, userLocation }: HospitalRecommendationsProps) {
  const [loading, setLoading] = useState(false);
  const [hospitals, setHospitals] = useState<Hospital[]>([]);

  useEffect(() => {
    if (show && userLocation && hospitals.length === 0) {
      loadHospitals();
    }
  }, [show, userLocation]);

  const loadHospitals = async () => {
    if (!userLocation) return;

    setLoading(true);

    try {
      const nearbyHospitals = await findNearbyEyeHospitals(userLocation);
      setHospitals(nearbyHospitals);
    } catch (err) {
      // Failed to load hospitals
    } finally {
      setLoading(false);
    }
  };

  if (!show) return null;

  return (
    <div className="mt-8 bg-blue-50 border-2 border-blue-200 rounded-xl p-6">
      <div className="flex items-start gap-3 mb-4">
        <div className="w-10 h-10 bg-blue-600 rounded-lg flex items-center justify-center flex-shrink-0">
          <MapPin className="w-5 h-5 text-white" />
        </div>
        <div className="flex-1">
          <h3 className="text-gray-900 font-semibold mb-1">Find Eye Care Near You</h3>
          <p className="text-sm text-gray-600">
            Consult an ophthalmologist for professional diagnosis and treatment.
          </p>
        </div>
      </div>

      {loading && (
        <div className="flex items-center justify-center py-8">
          <Loader2 className="w-6 h-6 text-blue-600 animate-spin" />
          <span className="ml-3 text-gray-600">Loading nearby facilities...</span>
        </div>
      )}

      {!loading && userLocation && (
        <>
          {hospitals.length > 0 ? (
            <>
              <h4 className="text-gray-900 font-medium mb-3">Search for facilities:</h4>
              <div className="space-y-3">
                {hospitals.map((hospital) => (
                  <div
                    key={hospital.id}
                    className="bg-white rounded-lg border border-gray-200 p-4 hover:border-blue-300 transition-colors"
                  >
                    <div className="flex items-start justify-between gap-3">
                      <div className="flex-1 min-w-0">
                        <h5 className="text-gray-900 font-medium mb-1">{hospital.name}</h5>
                        <p className="text-sm text-gray-600 mb-2 line-clamp-2">{hospital.address}</p>
                        <div className="flex items-center gap-4 text-sm">
                          <span className="text-blue-600 font-medium">{hospital.distance}</span>
                          {hospital.rating && (
                            <span className="text-gray-600">★ {hospital.rating}</span>
                          )}
                        </div>
                      </div>
                      <div className="flex gap-2 flex-shrink-0">
                        <a
                          href={`https://www.google.com/maps/search/${encodeURIComponent(hospital.name)}/@${hospital.latitude},${hospital.longitude},13z`}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="p-2 bg-blue-100 text-blue-600 rounded-lg hover:bg-blue-200 transition-colors"
                          title="Open in Maps"
                        >
                          <ExternalLink className="w-4 h-4" />
                        </a>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </>
          ) : (
            <div className="text-center py-4 text-gray-600">
              <p>Search for ophthalmologists or eye hospitals in your area.</p>
            </div>
          )}

        </>
      )}
    </div>
  );
}
