"""Test API endpoints."""

import requests
import json

BASE_URL = "http://localhost:8000"

def test_analysis():
    """Test analysis endpoint."""
    response = requests.post(
        f"{BASE_URL}/api/v1/analysis/",
        json={
            "target": "sample_repos/sample_python_project/main.py",
            "analysis_types": ["complexity", "pattern"],
            "async_mode": False
        }
    )
    print("Analysis:", response.json())

def test_search():
    """Test search endpoint."""
    response = requests.post(
        f"{BASE_URL}/api/v1/search/",
        json={
            "query": "calculate total price",
            "max_results": 5
        }
    )
    print("Search:", response.json())

def test_metrics():
    """Test metrics endpoint."""
    response = requests.post(
        f"{BASE_URL}/api/v1/metrics/",
        json={
            "target": "sample_repos/sample_python_project",
            "metric_types": ["complexity", "quality"]
        }
    )
    print("Metrics:", response.json())

if __name__ == "__main__":
    print("Testing API endpoints...")
    test_analysis()
    test_search()
    test_metrics() 