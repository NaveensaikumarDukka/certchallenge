#!/usr/bin/env python3
"""
Simple test script to demonstrate the Wealth Advisor API functionality
"""

import requests
import json
import time
from typing import Dict, Any

# API base URL
BASE_URL = "http://localhost:8000"

def test_health_check():
    """Test the health check endpoint"""
    print("Testing health check...")
    try:
        response = requests.get(f"{BASE_URL}/health")
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
        return response.status_code == 200
    except Exception as e:
        print(f"Error: {e}")
        return False

def test_advisor_query():
    """Test the wealth advisor query endpoint"""
    print("\nTesting wealth advisor query...")
    try:
        payload = {
            "question": "What are the best investment strategies for retirement planning?",
            "include_context": True,
            "stream_response": False
        }
        
        response = requests.post(f"{BASE_URL}/api/v1/advisor/query", json=payload)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Response: {data.get('response', 'No response')}")
            print(f"Tools used: {data.get('tools_used', [])}")
            print(f"Confidence: {data.get('confidence', 0)}")
            return True
        else:
            print(f"Error: {response.text}")
            return False
            
    except Exception as e:
        print(f"Error: {e}")
        return False

def test_rag_query():
    """Test the RAG query endpoint"""
    print("\nTesting RAG query...")
    try:
        payload = {
            "question": "What are the key principles of wealth management?",
            "top_k": 3
        }
        
        response = requests.post(f"{BASE_URL}/api/v1/rag/query", json=payload)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Response: {data.get('response', 'No response')}")
            print(f"Sources: {data.get('sources', [])}")
            return True
        else:
            print(f"Error: {response.text}")
            return False
            
    except Exception as e:
        print(f"Error: {e}")
        return False

def test_context_parsing():
    """Test context parsing functionality"""
    print("\nTesting context parsing...")
    try:
        # Test Tavily context parsing
        tavily_context = """
        <result>
        <title>Investment Strategies 2024</title>
        <content>Latest investment strategies for wealth management include diversification, asset allocation, and risk management.</content>
        <url>https://example.com/investment-strategies</url>
        <score>0.95</score>
        </result>
        """
        
        payload = {
            "context": tavily_context,
            "source_type": "tavily"
        }
        
        response = requests.post(f"{BASE_URL}/api/v1/context/parse-tavily", json=payload)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Source: {data.get('source', 'Unknown')}")
            print(f"Formatted output: {data.get('formatted_output', 'No output')[:200]}...")
            return True
        else:
            print(f"Error: {response.text}")
            return False
            
    except Exception as e:
        print(f"Error: {e}")
        return False

def test_tools():
    """Test tool endpoints"""
    print("\nTesting tools...")
    
    # Test Tavily search
    try:
        response = requests.get(f"{BASE_URL}/api/v1/tools/search?query=wealth management strategies&max_results=3")
        print(f"Tavily search status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"Found {data.get('total_results', 0)} results")
    except Exception as e:
        print(f"Tavily search error: {e}")
    
    # Test ArXiv search
    try:
        response = requests.get(f"{BASE_URL}/api/v1/tools/arxiv?query=investment portfolio&max_results=3")
        print(f"ArXiv search status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"Found {data.get('total_papers', 0)} papers")
    except Exception as e:
        print(f"ArXiv search error: {e}")
    
    # Test YFinance
    try:
        response = requests.get(f"{BASE_URL}/api/v1/tools/yfinance?symbol=AAPL")
        print(f"YFinance status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"Stock data for {data.get('symbol', 'Unknown')}")
    except Exception as e:
        print(f"YFinance error: {e}")

def test_evaluation():
    """Test evaluation functionality"""
    print("\nTesting evaluation...")
    try:
        # Generate test dataset
        payload = {
            "num_tests": 5,
            "categories": ["investment_advice", "retirement_planning"],
            "difficulty_level": "medium"
        }
        
        response = requests.post(f"{BASE_URL}/api/v1/evaluation/generate-tests", json=payload)
        print(f"Test generation status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            test_questions = data.get('test_questions', [])
            print(f"Generated {len(test_questions)} test questions")
            
            # Run evaluation
            eval_payload = {
                "test_questions": test_questions[:3],  # Use first 3 questions
                "include_detailed_results": False
            }
            
            eval_response = requests.post(f"{BASE_URL}/api/v1/evaluation/evaluate", json=eval_payload)
            print(f"Evaluation status: {eval_response.status_code}")
            
            if eval_response.status_code == 200:
                eval_data = eval_response.json()
                print(f"Overall score: {eval_data.get('overall_score', 0)}")
                print(f"Recommendations: {eval_data.get('recommendations', [])}")
                return True
                
    except Exception as e:
        print(f"Evaluation error: {e}")
        return False

def test_analytics():
    """Test analytics endpoints"""
    print("\nTesting analytics...")
    
    try:
        # Usage analytics
        response = requests.get(f"{BASE_URL}/api/v1/analytics/usage")
        print(f"Usage analytics status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"Total queries: {data.get('total_queries', 0)}")
            print(f"Successful queries: {data.get('successful_queries', 0)}")
    
    except Exception as e:
        print(f"Usage analytics error: {e}")
    
    try:
        # Performance metrics
        response = requests.get(f"{BASE_URL}/api/v1/analytics/performance")
        print(f"Performance metrics status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"Overall performance score: {data.get('overall_performance_score', 0)}")
    
    except Exception as e:
        print(f"Performance metrics error: {e}")

def main():
    """Run all tests"""
    print("Wealth Advisor API Test Suite")
    print("=" * 50)
    
    tests = [
        ("Health Check", test_health_check),
        ("Wealth Advisor Query", test_advisor_query),
        ("RAG Query", test_rag_query),
        ("Context Parsing", test_context_parsing),
        ("Tools", test_tools),
        ("Evaluation", test_evaluation),
        ("Analytics", test_analytics)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n{'='*20} {test_name} {'='*20}")
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"Test failed with exception: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "="*50)
    print("TEST SUMMARY")
    print("="*50)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "PASS" if result else "FAIL"
        print(f"{test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed!")
    else:
        print("⚠️  Some tests failed. Check the API server and configuration.")

if __name__ == "__main__":
    main() 