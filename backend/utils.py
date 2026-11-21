"""
Utility functions for image processing and model predictions
"""
import numpy as np
from PIL import Image
import io
from typing import Tuple, Dict
import os

class ImageProcessor:
    """Handle image preprocessing for model inference"""
    
    @staticmethod
    def load_image(image_bytes: bytes, target_size: Tuple[int, int] = (256, 256)) -> np.ndarray:
        """
        Load and preprocess an image from bytes.
        
        Args:
            image_bytes: Image data as bytes
            target_size: Target size for resizing (width, height)
            
        Returns:
            Preprocessed image array normalized to [0, 1]
        """
        try:
            # Load image
            img = Image.open(io.BytesIO(image_bytes))
            
            # Convert to RGB if necessary
            if img.mode != 'RGB':
                img = img.convert('RGB')
            
            # Resize to target size
            img = img.resize(target_size, Image.Resampling.LANCZOS)
            
            # Convert to numpy array
            img_array = np.array(img, dtype=np.float32)
            
            # Normalize to [0, 1]
            img_array = img_array / 255.0
            
            return img_array
            
        except Exception as e:
            raise ValueError(f"Failed to process image: {str(e)}")
    
    @staticmethod
    def prepare_for_model(img_array: np.ndarray) -> np.ndarray:
        """
        Prepare image array for model prediction by adding batch dimension.
        
        Args:
            img_array: Image array with shape (height, width, channels)
            
        Returns:
            Image array with shape (1, height, width, channels)
        """
        if len(img_array.shape) == 3:
            return np.expand_dims(img_array, axis=0)
        return img_array


class PredictionAnalyzer:
    """Analyze and format model predictions"""
    
    DISEASE_THRESHOLDS = {
        'High': 0.85,
        'Medium': 0.70,
        'Low': 0.50
    }
    
    @staticmethod
    def get_confidence_level(confidence: float) -> str:
        """Determine confidence level based on threshold"""
        if confidence >= PredictionAnalyzer.DISEASE_THRESHOLDS['High']:
            return 'High'
        elif confidence >= PredictionAnalyzer.DISEASE_THRESHOLDS['Medium']:
            return 'Medium'
        else:
            return 'Low'
    
    @staticmethod
    def calculate_health_score(predictions: Dict[str, float]) -> int:
        """
        Calculate overall plant health score (0-100).
        
        Args:
            predictions: Dictionary with disease names and confidence scores
            
        Returns:
            Health score as integer (0-100)
        """
        healthy_confidence = predictions.get('Healthy', 0.0)
        health_score = int(healthy_confidence * 100)
        return max(0, min(100, health_score))
    
    @staticmethod
    def get_recommendations(disease: str, confidence: float) -> Dict:
        """
        Get actionable recommendations based on disease and confidence.
        
        Args:
            disease: Disease name
            confidence: Confidence score (0-1)
            
        Returns:
            Dictionary with recommendations
        """
        confidence_level = PredictionAnalyzer.get_confidence_level(confidence)
        
        recommendations = {
            'confidence_level': confidence_level,
            'urgency': 'Critical' if confidence > 0.9 else 'High' if confidence > 0.75 else 'Medium',
            'immediate_actions': [],
            'follow_up': []
        }
        
        if disease == 'Healthy':
            recommendations['immediate_actions'] = [
                'Continue regular monitoring',
                'Maintain current watering schedule',
                'Keep optimal sunlight exposure'
            ]
            recommendations['follow_up'] = [
                'Check plant weekly for any changes',
                'Monitor for pest activity'
            ]
        
        elif disease == 'Early Blight':
            recommendations['immediate_actions'] = [
                'Remove infected leaves immediately',
                'Apply fungicide treatment',
                'Improve air circulation around plant'
            ]
            recommendations['follow_up'] = [
                'Monitor treated plant for 7-10 days',
                'Reapply fungicide if needed',
                'Avoid overhead watering'
            ]
        
        elif disease == 'Late Blight':
            recommendations['immediate_actions'] = [
                'URGENT: Remove severely affected parts',
                'Apply systemic fungicide immediately',
                'Improve drainage and reduce humidity',
                'Isolate plant to prevent spread'
            ]
            recommendations['follow_up'] = [
                'Monitor daily for progression',
                'Apply fungicide every 3-5 days',
                'Consider destroying plant if severe'
            ]
        
        return recommendations


class FileValidator:
    """Validate uploaded files"""
    
    ALLOWED_EXTENSIONS = {'jpg', 'jpeg', 'png', 'gif', 'bmp', 'webp'}
    MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB
    
    @staticmethod
    def validate_file(filename: str, file_size: int) -> Tuple[bool, str]:
        """
        Validate uploaded file.
        
        Args:
            filename: Name of the file
            file_size: Size of the file in bytes
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        # Check extension
        extension = filename.rsplit('.', 1)[-1].lower()
        if extension not in FileValidator.ALLOWED_EXTENSIONS:
            return False, f"File type '.{extension}' not allowed. Allowed: {', '.join(FileValidator.ALLOWED_EXTENSIONS)}"
        
        # Check file size
        if file_size > FileValidator.MAX_FILE_SIZE:
            return False, f"File size exceeds maximum of {FileValidator.MAX_FILE_SIZE / (1024*1024):.1f} MB"
        
        if file_size == 0:
            return False, "File is empty"
        
        return True, ""
    
    @staticmethod
    def validate_directory(path: str) -> bool:
        """Check if directory exists and is accessible"""
        return os.path.isdir(path) and os.access(path, os.R_OK)


# Example usage functions for testing
def test_image_processing():
    """Test image processing functionality"""
    print("Testing ImageProcessor...")
    # This would be used in tests
    pass


def test_prediction_analysis():
    """Test prediction analysis functionality"""
    print("Testing PredictionAnalyzer...")
    predictions = {
        'Early Blight': 0.05,
        'Healthy': 0.90,
        'Late Blight': 0.05
    }
    health_score = PredictionAnalyzer.calculate_health_score(predictions)
    print(f"Health Score: {health_score}")


if __name__ == "__main__":
    test_prediction_analysis()
