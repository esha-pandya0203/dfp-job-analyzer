#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
BLS (Bureau of Labor Statistics) API Integration
===============================================

BLS Bureau of Labor Statistics API integration module
Used to fetch employment growth rates, salary statistics and other official labor data

Author: Orange Team
Version: 1.0
"""

import requests
import pandas as pd
import json
import time
from typing import Dict, List, Optional, Any
import logging

logger = logging.getLogger(__name__)


class BLSAPIClient:
    """BLS API client"""
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize BLS API client
        
        Args:
            api_key: BLS API key (optional, having a key provides higher request limits)
        """
        self.api_key = api_key
        self.base_url = "https://api.bls.gov/publicAPI/v2"
        self.headers = {
            'Content-Type': 'application/json',
            'User-Agent': 'Job-Market-Analyzer/1.0'
        }
        
        # Request rate limiting
        self.requests_per_second = 0.5  # Maximum 0.5 requests per second
        self.last_request_time = 0
        
    def _rate_limit(self):
        """Implement request rate limiting"""
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        min_interval = 1.0 / self.requests_per_second
        
        if time_since_last < min_interval:
            sleep_time = min_interval - time_since_last
            time.sleep(sleep_time)
        
        self.last_request_time = time.time()
    
    def get_occupation_data(self, occupation_codes: List[str], 
                          start_year: int = 2020, 
                          end_year: int = 2023) -> Dict[str, Any]:
        """
        Get occupation data
        
        Args:
            occupation_codes: List of occupation codes
            start_year: Start year
            end_year: End year
            
        Returns:
            Occupation data dictionary
        """
        self._rate_limit()
        
        # Build request data
        request_data = {
            "seriesid": occupation_codes,
            "startyear": str(start_year),
            "endyear": str(end_year),
            "catalog": True,
            "calculations": True,
            "annualaverage": True,
            "aspects": True
        }
        
        # If API key is available, add it to the request
        if self.api_key:
            request_data["registrationkey"] = self.api_key
        
        try:
            logger.info(f"Requesting BLS data: {occupation_codes}")
            response = requests.post(
                f"{self.base_url}/timeseries/data/",
                headers=self.headers,
                json=request_data,
                timeout=30
            )
            response.raise_for_status()
            
            data = response.json()
            
            if data.get("status") == "REQUEST_SUCCEEDED":
                logger.info("BLS data request successful")
                return data
            else:
                logger.error(f"BLS API error: {data.get('message', 'Unknown error')}")
                return {}
                
        except requests.exceptions.RequestException as e:
            logger.error(f"BLS API request failed: {e}")
            return {}
    
    def get_employment_data(self, occupation_codes: List[str]) -> pd.DataFrame:
        """
        Get employment data
        
        Args:
            occupation_codes: List of occupation codes
            
        Returns:
            Employment data DataFrame
        """
        data = self.get_occupation_data(occupation_codes)
        
        if not data or "Results" not in data:
            return pd.DataFrame()
        
        employment_data = []
        
        for series in data["Results"]["series"]:
            series_id = series["seriesID"]
            occupation_name = series.get("catalog", {}).get("series_title", "Unknown")
            
            for item in series["data"]:
                employment_data.append({
                    "series_id": series_id,
                    "occupation": occupation_name,
                    "year": int(item["year"]),
                    "period": item["period"],
                    "value": float(item["value"]) if item["value"] != "null" else None,
                    "footnotes": item.get("footnotes", [])
                })
        
        return pd.DataFrame(employment_data)
    
    def get_salary_data(self, occupation_codes: List[str]) -> pd.DataFrame:
        """
        Get salary data
        
        Args:
            occupation_codes: List of occupation codes
            
        Returns:
            Salary data DataFrame
        """
        # Salary data typically uses different series IDs
        # This needs to be adjusted based on specific BLS data series
        salary_codes = [code.replace("00", "01") for code in occupation_codes]  # Example conversion
        
        data = self.get_occupation_data(salary_codes)
        
        if not data or "Results" not in data:
            return pd.DataFrame()
        
        salary_data = []
        
        for series in data["Results"]["series"]:
            series_id = series["seriesID"]
            occupation_name = series.get("catalog", {}).get("series_title", "Unknown")
            
            for item in series["data"]:
                salary_data.append({
                    "series_id": series_id,
                    "occupation": occupation_name,
                    "year": int(item["year"]),
                    "period": item["period"],
                    "salary": float(item["value"]) if item["value"] != "null" else None,
                    "footnotes": item.get("footnotes", [])
                })
        
        return pd.DataFrame(salary_data)
    
    def search_occupations(self, keyword: str) -> List[Dict[str, str]]:
        """
        Search occupations
        
        Args:
            keyword: Search keyword
            
        Returns:
            List of matching occupations
        """
        # This is a simplified implementation
        # The actual BLS API may require different endpoints
        common_occupations = {
            "data scientist": ["15-2051.00"],
            "software developer": ["15-1252.00"],
            "data analyst": ["15-2051.00"],
            "machine learning engineer": ["15-1299.00"],
            "business analyst": ["13-1111.00"],
            "project manager": ["11-9199.00"],
            "product manager": ["11-9199.00"],
            "data engineer": ["15-1299.00"],
            "devops engineer": ["15-1299.00"],
            "cloud architect": ["15-1299.00"]
        }
        
        results = []
        keyword_lower = keyword.lower()
        
        for occupation, codes in common_occupations.items():
            if keyword_lower in occupation:
                results.append({
                    "name": occupation,
                    "codes": codes,
                    "description": f"BLS occupation codes: {', '.join(codes)}"
                })
        
        return results


class BLSAnalyzer:
    """BLS data analyzer"""
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize BLS analyzer
        
        Args:
            api_key: BLS API key
        """
        self.client = BLSAPIClient(api_key)
        self.employment_data = pd.DataFrame()
        self.salary_data = pd.DataFrame()
    
    def analyze_occupation_trends(self, occupation_codes: List[str]) -> Dict[str, Any]:
        """
        Analyze occupation trends
        
        Args:
            occupation_codes: List of occupation codes
            
        Returns:
            Trend analysis results
        """
        logger.info(f"Analyzing occupation trends: {occupation_codes}")
        
        # Get employment data
        employment_df = self.client.get_employment_data(occupation_codes)
        salary_df = self.client.get_salary_data(occupation_codes)
        
        if employment_df.empty and salary_df.empty:
            return {"error": "Unable to fetch data"}
        
        results = {
            "occupation_codes": occupation_codes,
            "employment_trends": {},
            "salary_trends": {},
            "growth_rates": {},
            "summary": {}
        }
        
        # Analyze employment trends
        if not employment_df.empty:
            for occupation in employment_df["occupation"].unique():
                occ_data = employment_df[employment_df["occupation"] == occupation]
                if len(occ_data) >= 2:
                    # Calculate growth rate
                    first_year = occ_data["value"].iloc[0]
                    last_year = occ_data["value"].iloc[-1]
                    growth_rate = ((last_year - first_year) / first_year) * 100
                    
                    results["employment_trends"][occupation] = {
                        "data": occ_data.to_dict("records"),
                        "growth_rate": growth_rate
                    }
        
        # Analyze salary trends
        if not salary_df.empty:
            for occupation in salary_df["occupation"].unique():
                occ_data = salary_df[salary_df["occupation"] == occupation]
                if len(occ_data) >= 2:
                    # Calculate salary growth rate
                    first_salary = occ_data["salary"].iloc[0]
                    last_salary = occ_data["salary"].iloc[-1]
                    salary_growth = ((last_salary - first_salary) / first_salary) * 100
                    
                    results["salary_trends"][occupation] = {
                        "data": occ_data.to_dict("records"),
                        "growth_rate": salary_growth
                    }
        
        # Generate summary
        results["summary"] = self._generate_summary(results)
        
        return results
    
    def _generate_summary(self, analysis_results: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate analysis summary
        
        Args:
            analysis_results: Analysis results
            
        Returns:
            Summary information
        """
        summary = {
            "total_occupations": len(analysis_results.get("occupation_codes", [])),
            "fastest_growing": None,
            "highest_paid": None,
            "average_growth_rate": 0,
            "average_salary_growth": 0
        }
        
        # Find fastest growing occupation
        employment_trends = analysis_results.get("employment_trends", {})
        if employment_trends:
            fastest_growing = max(
                employment_trends.items(),
                key=lambda x: x[1].get("growth_rate", 0)
            )
            summary["fastest_growing"] = {
                "occupation": fastest_growing[0],
                "growth_rate": fastest_growing[1]["growth_rate"]
            }
        
        # Find highest paid occupation
        salary_trends = analysis_results.get("salary_trends", {})
        if salary_trends:
            highest_paid = max(
                salary_trends.items(),
                key=lambda x: x[1].get("data", [{}])[-1].get("salary", 0)
            )
            summary["highest_paid"] = {
                "occupation": highest_paid[0],
                "salary": highest_paid[1]["data"][-1]["salary"]
            }
        
        return summary
    
    def get_market_insights(self, target_occupations: List[str]) -> Dict[str, Any]:
        """
        Get market insights
        
        Args:
            target_occupations: List of target occupations
            
        Returns:
            Market insights data
        """
        logger.info(f"Getting market insights: {target_occupations}")
        
        # Search occupation codes
        occupation_codes = []
        for occupation in target_occupations:
            search_results = self.client.search_occupations(occupation)
            for result in search_results:
                occupation_codes.extend(result["codes"])
        
        if not occupation_codes:
            return {"error": "No matching occupation codes found"}
        
        # Analyze trends
        trends = self.analyze_occupation_trends(occupation_codes)
        
        # Generate insights
        insights = {
            "target_occupations": target_occupations,
            "trends_analysis": trends,
            "recommendations": self._generate_recommendations(trends),
            "market_outlook": self._assess_market_outlook(trends)
        }
        
        return insights
    
    def _generate_recommendations(self, trends: Dict[str, Any]) -> List[str]:
        """
        Generate recommendations
        
        Args:
            trends: Trend analysis results
            
        Returns:
            List of recommendations
        """
        recommendations = []
        
        summary = trends.get("summary", {})
        
        if summary.get("fastest_growing"):
            fastest = summary["fastest_growing"]
            recommendations.append(
                f"Consider entering the {fastest['occupation']} field, "
                f"with employment growth rate of {fastest['growth_rate']:.1f}%"
            )
        
        if summary.get("highest_paid"):
            highest = summary["highest_paid"]
            recommendations.append(
                f"{highest['occupation']} offers the highest salary, "
                f"with average salary of ${highest['salary']:,.0f}"
            )
        
        return recommendations
    
    def _assess_market_outlook(self, trends: Dict[str, Any]) -> str:
        """
        Assess market outlook
        
        Args:
            trends: Trend analysis results
            
        Returns:
            Market outlook assessment
        """
        summary = trends.get("summary", {})
        avg_growth = summary.get("average_growth_rate", 0)
        
        if avg_growth > 5:
            return "Market outlook is very optimistic with strong employment growth"
        elif avg_growth > 2:
            return "Market outlook is good with steady employment growth"
        elif avg_growth > 0:
            return "Market outlook is stable with slight employment growth"
        else:
            return "Market outlook is cautious with slow employment growth"


def main():
    """Main function - BLS API integration example"""
    print("=" * 60)
    print("BLS API Integration - Bureau of Labor Statistics API Integration")
    print("=" * 60)
    
    # Create BLS analyzer
    analyzer = BLSAnalyzer()
    
    while True:
        print("\nPlease select an operation:")
        print("1. Search occupations")
        print("2. Analyze occupation trends")
        print("3. Get market insights")
        print("4. Exit")
        
        choice = input("\nPlease enter your choice (1-4): ").strip()
        
        if choice == '1':
            keyword = input("Please enter occupation keyword: ").strip()
            if keyword:
                results = analyzer.client.search_occupations(keyword)
                if results:
                    print(f"\nFound {len(results)} matching occupations:")
                    for result in results:
                        print(f"  - {result['name']}: {result['description']}")
                else:
                    print("No matching occupations found")
        
        elif choice == '2':
            occupation_codes = input("Please enter occupation codes (comma-separated): ").strip().split(',')
            occupation_codes = [code.strip() for code in occupation_codes if code.strip()]
            
            if occupation_codes:
                trends = analyzer.analyze_occupation_trends(occupation_codes)
                if "error" not in trends:
                    print("\nOccupation trend analysis results:")
                    print(json.dumps(trends, indent=2, ensure_ascii=False))
                else:
                    print(f"Analysis failed: {trends['error']}")
        
        elif choice == '3':
            occupations = input("Please enter target occupations (comma-separated): ").strip().split(',')
            occupations = [occ.strip() for occ in occupations if occ.strip()]
            
            if occupations:
                insights = analyzer.get_market_insights(occupations)
                if "error" not in insights:
                    print("\nMarket insights:")
                    print(json.dumps(insights, indent=2, ensure_ascii=False))
                else:
                    print(f"Failed to get insights: {insights['error']}")
        
        elif choice == '4':
            print("Thank you for using BLS API integration!")
            break
        
        else:
            print("Invalid choice, please try again!")


if __name__ == "__main__":
    main()
