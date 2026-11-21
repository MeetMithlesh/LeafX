"""
Frontend Integration Helper
Example code and utilities for integrating the FastAPI backend with React frontend
"""

# ============================================================================
# JAVASCRIPT/REACT INTEGRATION CODE - Copy this to your React component
# ============================================================================

REACT_INTEGRATION_CODE = """
// api/agroscanApi.js

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

export const agroscanApi = {
  /**
   * Check if backend is healthy
   */
  async checkHealth() {
    try {
      const response = await fetch(`${API_URL}/health`);
      return await response.json();
    } catch (error) {
      console.error('Health check failed:', error);
      throw error;
    }
  },

  /**
   * Analyze plant image and get disease prediction
   * @param {File} imageFile - Image file to analyze
   * @returns {Promise<Object>} Prediction results
   */
  async predictDisease(imageFile) {
    try {
      const formData = new FormData();
      formData.append('file', imageFile);

      const response = await fetch(`${API_URL}/predict`, {
        method: 'POST',
        body: formData,
        // Don't set Content-Type header, browser will set it with boundary
      });

      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || 'Prediction failed');
      }

      return await response.json();
    } catch (error) {
      console.error('Prediction error:', error);
      throw error;
    }
  },

  /**
   * Get information about all detectable diseases
   */
  async getDiseases() {
    try {
      const response = await fetch(`${API_URL}/diseases`);
      return await response.json();
    } catch (error) {
      console.error('Failed to fetch disease info:', error);
      throw error;
    }
  },
};

// ============================================================================
// USAGE IN YOUR REACT COMPONENT
// ============================================================================

/**
 * Example: Using in App.jsx
 */

import React, { useState } from 'react';
import { agroscanApi } from './api/agroscanApi';

export const AnalyzeImageComponent = () => {
  const [loading, setLoading] = useState(false);
  const [prediction, setPrediction] = useState(null);
  const [error, setError] = useState(null);

  const handleImageUpload = async (event) => {
    const file = event.target.files[0];
    if (!file) return;

    setLoading(true);
    setError(null);

    try {
      // Validate file type
      const validTypes = ['image/jpeg', 'image/png', 'image/gif', 'image/bmp'];
      if (!validTypes.includes(file.type)) {
        throw new Error('Please upload a valid image file');
      }

      // Call backend API
      const result = await agroscanApi.predictDisease(file);
      setPrediction(result);
    } catch (err) {
      setError(err.message || 'Failed to analyze image');
      console.error('Analysis error:', err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <input
        type="file"
        accept="image/*"
        onChange={handleImageUpload}
        disabled={loading}
      />

      {loading && <p>Analyzing image...</p>}

      {error && <p style={{ color: 'red' }}>{error}</p>}

      {prediction && (
        <div>
          <h3>Analysis Results</h3>
          <p>Health Score: {prediction.healthScore}%</p>
          <p>Condition: {prediction.diagnosis.condition}</p>
          <p>Confidence: {(prediction.diagnosis.probability * 100).toFixed(2)}%</p>
          <p>Treatment: {prediction.diagnosis.treatment}</p>
        </div>
      )}
    </div>
  );
};

// ============================================================================
// ENVIRONMENT VARIABLES FOR REACT
// ============================================================================

/**
 * .env file for React app:
 * 
 * REACT_APP_API_URL=http://localhost:8000
 * 
 * Or for production:
 * REACT_APP_API_URL=https://your-api-domain.com
 */

// ============================================================================
// ERROR HANDLING AND RETRY LOGIC
// ============================================================================

/**
 * Retry utility for failed requests
 */
async function retryFetch(fetchFn, maxRetries = 3, delay = 1000) {
  for (let i = 0; i < maxRetries; i++) {
    try {
      return await fetchFn();
    } catch (error) {
      if (i === maxRetries - 1) throw error;
      console.log(`Retry ${i + 1}/${maxRetries} after ${delay}ms`);
      await new Promise(resolve => setTimeout(resolve, delay));
    }
  }
}

/**
 * Usage:
 * const result = await retryFetch(() => agroscanApi.predictDisease(file));
 */

// ============================================================================
// RESPONSE MAPPING FOR UI
// ============================================================================

/**
 * Map backend response to UI-friendly format
 */
function mapPredictionToUI(prediction) {
  return {
    scanId: prediction.id,
    plantType: prediction.plantType,
    healthScore: prediction.healthScore,
    status: prediction.status,
    disease: prediction.diagnosis.condition,
    confidence: (prediction.diagnosis.probability * 100).toFixed(2),
    severity: prediction.diagnosis.severity,
    description: prediction.diagnosis.description,
    treatment: prediction.diagnosis.treatment,
    prevention: prediction.diagnosis.prevention,
    allConfidences: prediction.confidence_scores,
  };
}

// ============================================================================
// LOADING STATE MANAGEMENT
// ============================================================================

/**
 * Custom hook for image analysis
 */
function useImageAnalysis() {
  const [state, setState] = useState({
    loading: false,
    prediction: null,
    error: null,
    progress: 0,
  });

  const analyzePlant = async (file) => {
    setState(prev => ({ ...prev, loading: true, error: null, progress: 10 }));

    try {
      setState(prev => ({ ...prev, progress: 30 }));
      const result = await agroscanApi.predictDisease(file);
      
      setState(prev => ({ ...prev, progress: 100 }));
      const mappedResult = mapPredictionToUI(result);
      
      setState(prev => ({ 
        ...prev, 
        prediction: mappedResult, 
        loading: false,
        progress: 100 
      }));
      
      return mappedResult;
    } catch (error) {
      setState(prev => ({ 
        ...prev, 
        error: error.message, 
        loading: false,
        progress: 0 
      }));
      throw error;
    }
  };

  const reset = () => {
    setState({
      loading: false,
      prediction: null,
      error: null,
      progress: 0,
    });
  };

  return { ...state, analyzePlant, reset };
}

// ============================================================================
// CACHING RESULTS
// ============================================================================

/**
 * Simple cache for recent predictions
 */
class PredictionCache {
  constructor(maxSize = 10, ttl = 3600000) { // 1 hour TTL
    this.cache = new Map();
    this.maxSize = maxSize;
    this.ttl = ttl;
  }

  getKey(file) {
    // Use file name and size as simple key
    return `${file.name}-${file.size}`;
  }

  get(file) {
    const key = this.getKey(file);
    const item = this.cache.get(key);
    
    if (!item) return null;
    
    // Check if expired
    if (Date.now() - item.timestamp > this.ttl) {
      this.cache.delete(key);
      return null;
    }
    
    return item.data;
  }

  set(file, data) {
    const key = this.getKey(file);
    
    // Maintain max size
    if (this.cache.size >= this.maxSize) {
      const firstKey = this.cache.keys().next().value;
      this.cache.delete(firstKey);
    }
    
    this.cache.set(key, {
      data,
      timestamp: Date.now(),
    });
  }

  clear() {
    this.cache.clear();
  }
}

// Usage:
// const cache = new PredictionCache();
// const cached = cache.get(file);
// if (cached) return cached;
// const result = await agroscanApi.predictDisease(file);
// cache.set(file, result);
"""

# ============================================================================
# CONFIGURATION CONSTANTS
# ============================================================================

CONFIG = {
    'API_TIMEOUT': 30000,  # milliseconds
    'MAX_FILE_SIZE': 10 * 1024 * 1024,  # 10 MB
    'ALLOWED_FORMATS': ['image/jpeg', 'image/png', 'image/gif', 'image/bmp', 'image/webp'],
    'DISEASE_COLORS': {
        'Healthy': '#10b981',  # Green
        'Early Blight': '#f59e0b',  # Amber
        'Late Blight': '#ef4444',  # Red
    },
    'RETRY_ATTEMPTS': 3,
    'RETRY_DELAY': 1000,  # milliseconds
}

print("""
=================================================================
FRONTEND INTEGRATION GUIDE
=================================================================

1. CREATE API CLIENT FILE:
   Create src/api/agroscanApi.js in your React project
   Copy the REACT_INTEGRATION_CODE section above

2. ENVIRONMENT VARIABLES:
   Add to your .env file:
   REACT_APP_API_URL=http://localhost:8000

3. IMPORT AND USE IN COMPONENTS:
   import { agroscanApi } from './api/agroscanApi';
   const result = await agroscanApi.predictDisease(imageFile);

4. HANDLE RESPONSE:
   The response includes:
   - healthScore: 0-100
   - diagnosis: { condition, probability, severity, treatment, prevention }
   - confidence_scores: { "Early Blight": X, "Healthy": Y, "Late Blight": Z }

5. DISPLAY RESULTS:
   - Show health score as percentage
   - Display disease name and confidence
   - Show treatment recommendations
   - List prevention tips

6. ERROR HANDLING:
   - Check for network errors
   - Handle file validation errors
   - Show user-friendly error messages

7. LOADING STATE:
   - Show loading indicator while API call is in progress
   - Display progress (optional)
   - Disable upload button during analysis

=================================================================
""")
