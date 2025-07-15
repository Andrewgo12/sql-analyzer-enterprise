#!/usr/bin/env python3
"""
Debug SQL Analysis Endpoint
"""

import requests
import tempfile
import os

def test_analysis_debug():
    base_url = "http://localhost:5000"
    
    # Create test SQL file
    sample_sql = """
    SELECT u.id, u.name, u.email, COUNT(o.id) as order_count
    FROM users u
    LEFT JOIN orders o ON u.id = o.user_id
    WHERE u.active = 1
    GROUP BY u.id, u.name, u.email
    HAVING COUNT(o.id) > 5
    ORDER BY order_count DESC
    LIMIT 100;
    """
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.sql', delete=False) as temp_file:
        temp_file.write(sample_sql)
        temp_file_path = temp_file.name
    
    try:
        # Test file upload
        with open(temp_file_path, 'rb') as f:
            files = {'file': ('test_query.sql', f, 'text/plain')}
            data = {'database_engine': 'mysql'}
            
            print("🔍 Testing SQL Analysis Endpoint")
            print(f"📁 File: {temp_file_path}")
            print(f"📊 Data: {data}")
            
            response = requests.post(f"{base_url}/api/analyze", 
                                   files=files, data=data, timeout=30)
            
            print(f"📈 Status Code: {response.status_code}")
            print(f"📝 Response: {response.text[:500]}...")
            
            if response.status_code == 200:
                print("✅ Analysis successful!")
            else:
                print(f"❌ Analysis failed: {response.status_code}")
                
    finally:
        os.unlink(temp_file_path)

if __name__ == "__main__":
    test_analysis_debug()
