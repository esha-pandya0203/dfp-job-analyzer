#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
BLS (Bureau of Labor Statistics) API Integration
===============================================

BLS劳工统计局API集成模块
用于获取就业增长率、薪资统计等官方劳工数据

作者: Orange Team
版本: 1.0
"""

import requests
import pandas as pd
import json
import time
from typing import Dict, List, Optional, Any
import logging

logger = logging.getLogger(__name__)


class BLSAPIClient:
    """BLS API客户端"""
    
    def __init__(self, api_key: Optional[str] = None):
        """
        初始化BLS API客户端
        
        Args:
            api_key: BLS API密钥 (可选，有密钥可以获得更高的请求限制)
        """
        self.api_key = api_key
        self.base_url = "https://api.bls.gov/publicAPI/v2"
        self.headers = {
            'Content-Type': 'application/json',
            'User-Agent': 'Job-Market-Analyzer/1.0'
        }
        
        # 请求限制
        self.requests_per_second = 0.5  # 每秒最多0.5个请求
        self.last_request_time = 0
        
    def _rate_limit(self):
        """实施请求频率限制"""
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
        获取职业数据
        
        Args:
            occupation_codes: 职业代码列表
            start_year: 开始年份
            end_year: 结束年份
            
        Returns:
            职业数据字典
        """
        self._rate_limit()
        
        # 构建请求数据
        request_data = {
            "seriesid": occupation_codes,
            "startyear": str(start_year),
            "endyear": str(end_year),
            "catalog": True,
            "calculations": True,
            "annualaverage": True,
            "aspects": True
        }
        
        # 如果有API密钥，添加到请求中
        if self.api_key:
            request_data["registrationkey"] = self.api_key
        
        try:
            logger.info(f"请求BLS数据: {occupation_codes}")
            response = requests.post(
                f"{self.base_url}/timeseries/data/",
                headers=self.headers,
                json=request_data,
                timeout=30
            )
            response.raise_for_status()
            
            data = response.json()
            
            if data.get("status") == "REQUEST_SUCCEEDED":
                logger.info("BLS数据请求成功")
                return data
            else:
                logger.error(f"BLS API错误: {data.get('message', 'Unknown error')}")
                return {}
                
        except requests.exceptions.RequestException as e:
            logger.error(f"BLS API请求失败: {e}")
            return {}
    
    def get_employment_data(self, occupation_codes: List[str]) -> pd.DataFrame:
        """
        获取就业数据
        
        Args:
            occupation_codes: 职业代码列表
            
        Returns:
            就业数据DataFrame
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
        获取薪资数据
        
        Args:
            occupation_codes: 职业代码列表
            
        Returns:
            薪资数据DataFrame
        """
        # 薪资数据通常使用不同的系列ID
        # 这里需要根据具体的BLS数据系列进行调整
        salary_codes = [code.replace("00", "01") for code in occupation_codes]  # 示例转换
        
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
        搜索职业
        
        Args:
            keyword: 搜索关键词
            
        Returns:
            匹配的职业列表
        """
        # 这是一个简化的实现
        # 实际的BLS API可能需要不同的端点
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
                    "description": f"BLS职业代码: {', '.join(codes)}"
                })
        
        return results


class BLSAnalyzer:
    """BLS数据分析器"""
    
    def __init__(self, api_key: Optional[str] = None):
        """
        初始化BLS分析器
        
        Args:
            api_key: BLS API密钥
        """
        self.client = BLSAPIClient(api_key)
        self.employment_data = pd.DataFrame()
        self.salary_data = pd.DataFrame()
    
    def analyze_occupation_trends(self, occupation_codes: List[str]) -> Dict[str, Any]:
        """
        分析职业趋势
        
        Args:
            occupation_codes: 职业代码列表
            
        Returns:
            趋势分析结果
        """
        logger.info(f"分析职业趋势: {occupation_codes}")
        
        # 获取就业数据
        employment_df = self.client.get_employment_data(occupation_codes)
        salary_df = self.client.get_salary_data(occupation_codes)
        
        if employment_df.empty and salary_df.empty:
            return {"error": "无法获取数据"}
        
        results = {
            "occupation_codes": occupation_codes,
            "employment_trends": {},
            "salary_trends": {},
            "growth_rates": {},
            "summary": {}
        }
        
        # 分析就业趋势
        if not employment_df.empty:
            for occupation in employment_df["occupation"].unique():
                occ_data = employment_df[employment_df["occupation"] == occupation]
                if len(occ_data) >= 2:
                    # 计算增长率
                    first_year = occ_data["value"].iloc[0]
                    last_year = occ_data["value"].iloc[-1]
                    growth_rate = ((last_year - first_year) / first_year) * 100
                    
                    results["employment_trends"][occupation] = {
                        "data": occ_data.to_dict("records"),
                        "growth_rate": growth_rate
                    }
        
        # 分析薪资趋势
        if not salary_df.empty:
            for occupation in salary_df["occupation"].unique():
                occ_data = salary_df[salary_df["occupation"] == occupation]
                if len(occ_data) >= 2:
                    # 计算薪资增长率
                    first_salary = occ_data["salary"].iloc[0]
                    last_salary = occ_data["salary"].iloc[-1]
                    salary_growth = ((last_salary - first_salary) / first_salary) * 100
                    
                    results["salary_trends"][occupation] = {
                        "data": occ_data.to_dict("records"),
                        "growth_rate": salary_growth
                    }
        
        # 生成摘要
        results["summary"] = self._generate_summary(results)
        
        return results
    
    def _generate_summary(self, analysis_results: Dict[str, Any]) -> Dict[str, Any]:
        """
        生成分析摘要
        
        Args:
            analysis_results: 分析结果
            
        Returns:
            摘要信息
        """
        summary = {
            "total_occupations": len(analysis_results.get("occupation_codes", [])),
            "fastest_growing": None,
            "highest_paid": None,
            "average_growth_rate": 0,
            "average_salary_growth": 0
        }
        
        # 找出增长最快的职业
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
        
        # 找出薪资最高的职业
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
        获取市场洞察
        
        Args:
            target_occupations: 目标职业列表
            
        Returns:
            市场洞察数据
        """
        logger.info(f"获取市场洞察: {target_occupations}")
        
        # 搜索职业代码
        occupation_codes = []
        for occupation in target_occupations:
            search_results = self.client.search_occupations(occupation)
            for result in search_results:
                occupation_codes.extend(result["codes"])
        
        if not occupation_codes:
            return {"error": "未找到匹配的职业代码"}
        
        # 分析趋势
        trends = self.analyze_occupation_trends(occupation_codes)
        
        # 生成洞察
        insights = {
            "target_occupations": target_occupations,
            "trends_analysis": trends,
            "recommendations": self._generate_recommendations(trends),
            "market_outlook": self._assess_market_outlook(trends)
        }
        
        return insights
    
    def _generate_recommendations(self, trends: Dict[str, Any]) -> List[str]:
        """
        生成建议
        
        Args:
            trends: 趋势分析结果
            
        Returns:
            建议列表
        """
        recommendations = []
        
        summary = trends.get("summary", {})
        
        if summary.get("fastest_growing"):
            fastest = summary["fastest_growing"]
            recommendations.append(
                f"考虑进入 {fastest['occupation']} 领域，"
                f"就业增长率为 {fastest['growth_rate']:.1f}%"
            )
        
        if summary.get("highest_paid"):
            highest = summary["highest_paid"]
            recommendations.append(
                f"{highest['occupation']} 提供最高薪资，"
                f"平均薪资为 ${highest['salary']:,.0f}"
            )
        
        return recommendations
    
    def _assess_market_outlook(self, trends: Dict[str, Any]) -> str:
        """
        评估市场前景
        
        Args:
            trends: 趋势分析结果
            
        Returns:
            市场前景评估
        """
        summary = trends.get("summary", {})
        avg_growth = summary.get("average_growth_rate", 0)
        
        if avg_growth > 5:
            return "市场前景非常乐观，就业增长强劲"
        elif avg_growth > 2:
            return "市场前景良好，就业稳步增长"
        elif avg_growth > 0:
            return "市场前景稳定，就业略有增长"
        else:
            return "市场前景谨慎，就业增长缓慢"


def main():
    """主函数 - BLS API集成示例"""
    print("=" * 60)
    print("BLS API Integration - 劳工统计局API集成")
    print("=" * 60)
    
    # 创建BLS分析器
    analyzer = BLSAnalyzer()
    
    while True:
        print("\n请选择操作:")
        print("1. 搜索职业")
        print("2. 分析职业趋势")
        print("3. 获取市场洞察")
        print("4. 退出")
        
        choice = input("\n请输入选择 (1-4): ").strip()
        
        if choice == '1':
            keyword = input("请输入职业关键词: ").strip()
            if keyword:
                results = analyzer.client.search_occupations(keyword)
                if results:
                    print(f"\n找到 {len(results)} 个匹配职业:")
                    for result in results:
                        print(f"  - {result['name']}: {result['description']}")
                else:
                    print("没有找到匹配的职业")
        
        elif choice == '2':
            occupation_codes = input("请输入职业代码 (用逗号分隔): ").strip().split(',')
            occupation_codes = [code.strip() for code in occupation_codes if code.strip()]
            
            if occupation_codes:
                trends = analyzer.analyze_occupation_trends(occupation_codes)
                if "error" not in trends:
                    print("\n职业趋势分析结果:")
                    print(json.dumps(trends, indent=2, ensure_ascii=False))
                else:
                    print(f"分析失败: {trends['error']}")
        
        elif choice == '3':
            occupations = input("请输入目标职业 (用逗号分隔): ").strip().split(',')
            occupations = [occ.strip() for occ in occupations if occ.strip()]
            
            if occupations:
                insights = analyzer.get_market_insights(occupations)
                if "error" not in insights:
                    print("\n市场洞察:")
                    print(json.dumps(insights, indent=2, ensure_ascii=False))
                else:
                    print(f"获取洞察失败: {insights['error']}")
        
        elif choice == '4':
            print("感谢使用BLS API集成!")
            break
        
        else:
            print("无效选择，请重新输入!")


if __name__ == "__main__":
    main()
