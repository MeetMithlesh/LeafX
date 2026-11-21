#!/usr/bin/env python3
"""
Test script for AgroScan AI Backend
Tests all API endpoints and functionality
"""

import requests
import json
import os
import sys
from pathlib import Path

# Configuration
API_URL = "http://localhost:8000"
TIMEOUT = 30

class Colors:
    """Terminal colors"""
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    END = '\033[0m'


def print_header(text):
    print(f"\n{Colors.BLUE}{'='*60}")
    print(f"  {text}")
    print(f"{'='*60}{Colors.END}\n")


def print_success(text):
    print(f"{Colors.GREEN}✓ {text}{Colors.END}")


def print_error(text):
    print(f"{Colors.RED}✗ {text}{Colors.END}")


def print_info(text):
    print(f"{Colors.YELLOW}ℹ {text}{Colors.END}")


def test_server_connection():
    """Test if server is reachable"""
    print_header("1. Testing Server Connection")
    
    try:
        response = requests.get(f"{API_URL}/", timeout=TIMEOUT)
        if response.status_code == 200:
            print_success(f"Server is reachable at {API_URL}")
            data = response.json()
            print_info(f"Message: {data.get('message', 'N/A')}")
            return True
        else:
            print_error(f"Server returned status {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print_error(f"Cannot connect to server at {API_URL}")
        print_info(f"Make sure backend is running: python main.py")
        return False
    except Exception as e:
        print_error(f"Connection error: {str(e)}")
        return False


def test_health_check():
    """Test health check endpoint"""
    print_header("2. Testing Health Check Endpoint")
    
    try:
        response = requests.get(f"{API_URL}/health", timeout=TIMEOUT)
        data = response.json()
        
        if response.status_code == 200:
            print_success("Health check endpoint works")
            print_info(f"Status: {data.get('status', 'unknown')}")
            print_info(f"Model loaded: {data.get('model_loaded', False)}")
            
            if not data.get('model_loaded'):
                print_error("Model is NOT loaded. Check potatoes.h5 location.")
                return False
            
            print_success("Model is loaded and ready")
            return True
        else:
            print_error(f"Unexpected status code: {response.status_code}")
            return False
    except Exception as e:
        print_error(f"Health check failed: {str(e)}")
        return False


def test_disease_endpoint():
    """Test disease information endpoint"""
    print_header("3. Testing Disease Information Endpoint")
    
    try:
        response = requests.get(f"{API_URL}/diseases", timeout=TIMEOUT)
        
        if response.status_code == 200:
            data = response.json()
            print_success("Disease information endpoint works")
            
            diseases = data.get('diseases', {})
            print_info(f"Available diseases: {len(diseases)}")
            
            for idx, disease in diseases.items():
                print_info(f"  [{idx}] {disease}")
            
            return True
        else:
            print_error(f"Unexpected status code: {response.status_code}")
            return False
    except Exception as e:
        print_error(f"Failed to get disease info: {str(e)}")
        return False


def test_prediction_with_dummy_image():
    """Test prediction endpoint with a simple image"""
    print_header("4. Testing Prediction Endpoint")
    
    # Check for test image
    test_image_paths = [
        Path.cwd() / "test_image.jpg",
        Path.cwd() / "sample.jpg",
        Path(__file__).parent / "test_image.jpg",
    ]
    
    test_image = None
    for path in test_image_paths:
        if path.exists():
            test_image = path
            break
    
    if not test_image:
        print_info("No test image found. Creating a simple test image...")
        
        try:
            from PIL import Image
            import numpy as np
            
            # Create a simple RGB image
            img_array = np.random.randint(0, 256, (256, 256, 3), dtype=np.uint8)
            img = Image.fromarray(img_array)
            test_image = Path.cwd() / "test_image_generated.jpg"
            img.save(test_image)
            print_success(f"Created test image: {test_image}")
        except ImportError:
            print_error("Cannot create test image (Pillow not available)")
            print_info("To test with an image, please provide a .jpg file")
            return None
        except Exception as e:
            print_error(f"Failed to create test image: {str(e)}")
            return None
    
    if not test_image:
        return None
    
    try:
        print_info(f"Using test image: {test_image}")
        print_info("Uploading image to /predict endpoint...")
        
        with open(test_image, 'rb') as f:
            files = {'file': f}
            response = requests.post(
                f"{API_URL}/predict",
                files=files,
                timeout=TIMEOUT
            )
        
        if response.status_code == 200:
            data = response.json()
            print_success("Prediction successful!")
            
            print_info(f"Plant Type: {data.get('plantType', 'N/A')}")
            print_info(f"Health Score: {data.get('healthScore', 'N/A')}%")
            print_info(f"Status: {data.get('status', 'N/A')}")
            
            diagnosis = data.get('diagnosis', {})
            print_info(f"Condition: {diagnosis.get('condition', 'N/A')}")
            print_info(f"Confidence: {diagnosis.get('probability', 0)*100:.2f}%")
            print_info(f"Severity: {diagnosis.get('severity', 'N/A')}")
            
            confidence_scores = data.get('confidence_scores', {})
            print_info("Confidence Scores:")
            for disease, score in confidence_scores.items():
                print_info(f"  - {disease}: {score*100:.2f}%")
            
            return True
        else:
            print_error(f"Unexpected status code: {response.status_code}")
            if response.text:
                print_error(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print_error(f"Prediction test failed: {str(e)}")
        return False


def test_documentation():
    """Test documentation endpoint"""
    print_header("5. Testing Documentation Endpoint")
    
    try:
        response = requests.get(f"{API_URL}/docs", timeout=TIMEOUT)
        
        if response.status_code == 200:
            print_success("Interactive API documentation is available")
            print_info(f"Visit: {API_URL}/docs to explore endpoints")
            return True
        else:
            print_error(f"Documentation endpoint returned {response.status_code}")
            return False
    except Exception as e:
        print_error(f"Documentation test failed: {str(e)}")
        return False


def main():
    """Run all tests"""
    print(f"\n{Colors.BLUE}{'='*60}")
    print(f"  AgroScan AI Backend - Test Suite")
    print(f"{'='*60}{Colors.END}\n")
    
    print_info(f"Testing API at: {API_URL}")
    print_info("This will verify backend functionality\n")
    
    results = []
    
    # Run tests
    results.append(("Server Connection", test_server_connection()))
    
    if results[-1][1]:  # Only continue if server is reachable
        results.append(("Health Check", test_health_check()))
        results.append(("Disease Info", test_disease_endpoint()))
        results.append(("Prediction", test_prediction_with_dummy_image()))
        results.append(("Documentation", test_documentation()))
    
    # Summary
    print_header("Test Summary")
    
    passed = sum(1 for _, result in results if result is True)
    failed = sum(1 for _, result in results if result is False)
    skipped = sum(1 for _, result in results if result is None)
    
    for test_name, result in results:
        if result is True:
            print_success(f"{test_name}")
        elif result is False:
            print_error(f"{test_name}")
        else:
            print_info(f"{test_name} (Skipped)")
    
    print()
    print_info(f"Passed: {passed}")
    print_info(f"Failed: {failed}")
    print_info(f"Skipped: {skipped}")
    
    if failed == 0 and passed > 0:
        print_success("\n✓ All tests passed! Backend is working correctly.\n")
        return 0
    elif failed > 0:
        print_error(f"\n✗ {failed} test(s) failed. Check backend logs.\n")
        return 1
    else:
        print_info("\nNo tests could be run. Is the backend server running?\n")
        return 1


if __name__ == "__main__":
    try:
        exit_code = main()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print(f"\n\n{Colors.YELLOW}Tests interrupted by user{Colors.END}\n")
        sys.exit(130)
    except Exception as e:
        print(f"\n{Colors.RED}Unexpected error: {str(e)}{Colors.END}\n")
        sys.exit(1)
