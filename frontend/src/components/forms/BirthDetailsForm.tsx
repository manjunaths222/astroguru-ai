import { useState } from 'react';
import { useForm } from 'react-hook-form';
import { motion } from 'framer-motion';
import api from '@/utils/api';
import { Order, BirthDetails } from '@/types';

interface BirthDetailsFormProps {
  onSuccess: (order: Order) => void;
  onCancel: () => void;
}

interface FormData {
  orderType: 'full_report' | 'query';
  userQuery?: string;
  name: string;
  dateOfBirth: string;
  timeOfBirth: string;
  placeOfBirth: string;
  goals: string[];
}

const BirthDetailsForm: React.FC<BirthDetailsFormProps> = ({ onSuccess, onCancel }) => {
  const { register, handleSubmit, watch, setValue, formState: { errors, isSubmitting } } = useForm<FormData>({
    defaultValues: {
      orderType: 'full_report',
      goals: [],
    },
  });

  const orderType = watch('orderType');
  const [placeSuggestions, setPlaceSuggestions] = useState<Array<{display: string, full: string, lat: number, lon: number}>>([]);
  const [showSuggestions, setShowSuggestions] = useState(false);
  const [selectedPlace, setSelectedPlace] = useState<{ lat: number | null, lon: number | null }>({ lat: null, lon: null });
  const [searchAbortController, setSearchAbortController] = useState<AbortController | null>(null);
  const placeOfBirthValue = watch('placeOfBirth');

  // Handle place of birth input with autocomplete
  const handlePlaceInput = async (value: string) => {
    // Cancel previous search
    if (searchAbortController) {
      searchAbortController.abort();
    }

    if (value.length < 3) {
      setPlaceSuggestions([]);
      setShowSuggestions(false);
      return;
    }

    // Create new abort controller
    const abortController = new AbortController();
    setSearchAbortController(abortController);

    try {
      // Wait 1 second for rate limiting (Nominatim requires max 1 request per second)
      await new Promise(resolve => setTimeout(resolve, 1000));

      if (abortController.signal.aborted) return;

      const url = `https://nominatim.openstreetmap.org/search?` +
        `q=${encodeURIComponent(value)}` +
        `&countrycodes=in` +
        `&limit=10` +
        `&format=json` +
        `&addressdetails=1` +
        `&accept-language=en`;

      const response = await fetch(url, {
        signal: abortController.signal,
        headers: {
          'User-Agent': 'AstroGuru-AI/1.0',
          'Accept': 'application/json'
        }
      });

      if (abortController.signal.aborted) return;

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      const suggestions = data.map((item: any) => {
        const address = item.address || {};
        const parts = [];
        
        if (address.city || address.town || address.village) {
          parts.push(address.city || address.town || address.village);
        }
        if (address.state) {
          parts.push(address.state);
        }
        if (address.country) {
          parts.push(address.country);
        }
        
        const locationString = parts.length > 0 
          ? parts.join(', ')
          : item.display_name;
        
        return {
          display: locationString,
          full: item.display_name,
          lat: parseFloat(item.lat),
          lon: parseFloat(item.lon),
          city: address.city || address.town || address.village || '',
          state: address.state || '',
          country: address.country || 'India'
        };
      });

      if (!abortController.signal.aborted) {
        setPlaceSuggestions(suggestions);
        setShowSuggestions(true);
      }
    } catch (error: any) {
      if (error.name === 'AbortError') {
        return;
      }
      console.error('Error searching locations:', error);
      setPlaceSuggestions([]);
      setShowSuggestions(false);
    }
  };

  const selectPlace = (suggestion: {display: string, lat: number, lon: number}) => {
    setSelectedPlace({ lat: suggestion.lat, lon: suggestion.lon });
    setValue('placeOfBirth', suggestion.display);
    setShowSuggestions(false);
  };

  const onSubmit = async (data: FormData) => {
    try {
      // Use selected coordinates if available, otherwise try to geocode
      let latitude = selectedPlace.lat;
      let longitude = selectedPlace.lon;
      
      // If no coordinates selected, try to get from the place string
      if (latitude === null || longitude === null) {
        const placeData = await getPlaceCoordinates(data.placeOfBirth);
        latitude = placeData?.latitude || null;
        longitude = placeData?.longitude || null;
      }
      
      const birthDetails: BirthDetails = {
        name: data.name,
        dateOfBirth: data.dateOfBirth,
        timeOfBirth: data.timeOfBirth,
        placeOfBirth: data.placeOfBirth,
        latitude: latitude,
        longitude: longitude,
        goals: data.goals,
        ...(data.orderType === 'query' && data.userQuery ? { user_query: data.userQuery } : {}),
      };

      const response = await api.post<Order>('/api/v1/orders', {
        birth_details: birthDetails,
        order_type: data.orderType,
        user_query: data.orderType === 'query' ? data.userQuery : undefined,
      });

      onSuccess(response.data);
    } catch (error: any) {
      console.error('Error creating order:', error);
      alert(error.response?.data?.detail || 'Failed to create order');
    }
  };

  const getPlaceCoordinates = async (place: string) => {
    try {
      const url = `https://nominatim.openstreetmap.org/search?` +
        `q=${encodeURIComponent(place)}` +
        `&countrycodes=in` +
        `&limit=1` +
        `&format=json` +
        `&addressdetails=1`;
      
      await new Promise(resolve => setTimeout(resolve, 1000)); // Rate limiting
      
      const response = await fetch(url, {
        headers: {
          'User-Agent': 'AstroGuru-AI/1.0',
          'Accept': 'application/json'
        }
      });
      
      if (!response.ok) {
        return { latitude: null, longitude: null };
      }
      
      const data = await response.json();
      if (data && data.length > 0) {
        return {
          latitude: parseFloat(data[0].lat),
          longitude: parseFloat(data[0].lon)
        };
      }
    } catch (error) {
      console.error('Error geocoding place:', error);
    }
    return { latitude: null, longitude: null };
  };

  const goalsOptions = ['Career', 'Finance', 'Health', 'Relationships', 'Love Life', 'Spirituality'];

  return (
    <motion.form
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      onSubmit={handleSubmit(onSubmit)}
      className="card space-y-6"
    >
      <h2 className="text-2xl font-bold text-text-primary mb-6">Enter Your Birth Details</h2>

      {/* Order Type */}
      <div>
        <label className="block text-sm font-medium text-text-primary mb-2">
          Order Type *
        </label>
        <select
          {...register('orderType', { required: true })}
          className="input-field"
        >
          <option value="full_report">Full Astrology Report (₹10.00)</option>
          <option value="query">Quick Query (₹5.00)</option>
        </select>
      </div>

      {/* User Query (for query type) */}
      {orderType === 'query' && (
        <motion.div
          initial={{ opacity: 0, height: 0 }}
          animate={{ opacity: 1, height: 'auto' }}
        >
          <label className="block text-sm font-medium text-text-primary mb-2">
            Your Query *
          </label>
          <textarea
            {...register('userQuery', { required: orderType === 'query' })}
            rows={4}
            placeholder="Enter your specific astrology question here..."
            className="input-field"
          />
          <small className="text-text-secondary text-sm">
            For quick queries, you can ask up to 3 messages (initial query + 2 follow-ups).
          </small>
        </motion.div>
      )}

      {/* Name */}
      <div>
        <label className="block text-sm font-medium text-text-primary mb-2">
          Full Name *
        </label>
        <input
          type="text"
          {...register('name', { required: true })}
          placeholder="Enter your full name"
          className="input-field"
        />
      </div>

      {/* Date of Birth */}
      <div>
        <label className="block text-sm font-medium text-text-primary mb-2">
          Date of Birth *
        </label>
        <input
          type="date"
          {...register('dateOfBirth', { required: true })}
          className="input-field"
        />
      </div>

      {/* Time of Birth */}
      <div>
        <label className="block text-sm font-medium text-text-primary mb-2">
          Time of Birth *
        </label>
        <input
          type="time"
          {...register('timeOfBirth', { required: true })}
          className="input-field"
        />
      </div>

      {/* Place of Birth */}
      <div className="relative">
        <label className="block text-sm font-medium text-text-primary mb-2">
          Place of Birth *
        </label>
        <div className="relative">
          <input
            type="text"
            {...register('placeOfBirth', { required: true })}
            placeholder="Enter city, state, country"
            className="input-field"
            autoComplete="off"
            onChange={(e) => {
              const value = e.target.value;
              handlePlaceInput(value);
            }}
            onBlur={() => {
              // Delay hiding suggestions to allow click
              setTimeout(() => setShowSuggestions(false), 200);
            }}
            onFocus={() => {
              if (placeSuggestions.length > 0) {
                setShowSuggestions(true);
              }
            }}
          />
          {showSuggestions && placeSuggestions.length > 0 && (
            <div className="absolute z-50 w-full mt-1 bg-surface border-2 border-primary rounded-lg shadow-xl max-h-60 overflow-y-auto">
              {placeSuggestions.map((suggestion, index) => (
                <div
                  key={index}
                  className="p-3 hover:bg-primary/10 cursor-pointer border-b border-border last:border-b-0 transition-colors"
                  onMouseDown={(e) => {
                    e.preventDefault(); // Prevent input blur
                    selectPlace(suggestion);
                  }}
                >
                  <div className="font-medium text-text-primary">{suggestion.display}</div>
                  <div className="text-sm text-text-secondary">{suggestion.full}</div>
                </div>
              ))}
            </div>
          )}
        </div>
        <small className="text-text-secondary text-sm mt-1 block">
          Start typing (min 3 characters) to see location suggestions
        </small>
      </div>

      {/* Goals */}
      <div>
        <label className="block text-sm font-medium text-text-primary mb-2">
          Your Goals * (Select at least one)
        </label>
        <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
          {goalsOptions.map((goal) => (
            <label key={goal} className="flex items-center space-x-2 cursor-pointer">
              <input
                type="checkbox"
                value={goal}
                {...register('goals', { required: true, validate: (v) => v.length > 0 })}
                className="w-4 h-4 text-primary border-border rounded focus:ring-primary"
              />
              <span className="text-text-primary">{goal}</span>
            </label>
          ))}
        </div>
        {errors.goals && (
          <p className="text-error text-sm mt-1">Please select at least one goal</p>
        )}
      </div>

      {/* Buttons */}
      <div className="flex gap-4 pt-4">
        <button
          type="button"
          onClick={onCancel}
          className="btn-secondary flex-1"
        >
          Cancel
        </button>
        <button
          type="submit"
          disabled={isSubmitting}
          className="btn-primary flex-1"
        >
          {isSubmitting ? 'Creating...' : orderType === 'query' ? 'Pay and Predict' : 'Pay and Generate'}
        </button>
      </div>
    </motion.form>
  );
};

export default BirthDetailsForm;

