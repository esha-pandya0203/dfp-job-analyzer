#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
宾夕法尼亚州BLS API集成
======================

专门用于获取宾夕法尼亚州就业数据的BLS API集成模块
包括就业统计、薪资数据、行业分析等

Author: Fan Yang (CMU)
Version: 1.0
"""

import requests
import pandas as pd
import json
import time
from typing import Dict, List, Optional, Any
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class PennsylvaniaBLSAPI:
    """宾夕法尼亚州BLS API客户端"""
    
    def __init__(self, api_key: Optional[str] = None):
        """
        初始化宾夕法尼亚州BLS API客户端
        
        Args:
            api_key: BLS API密钥（可选，有密钥可提供更高的请求限制）
        """
        self.api_key = api_key
        self.base_url = "https://api.bls.gov/publicAPI/v2"
        self.pa_state_code = "PA"
        self.pa_state_name = "Pennsylvania"
        
        self.headers = {
            'Content-Type': 'application/json',
            'User-Agent': 'Pennsylvania-Job-Analyzer/1.0'
        }
        
        # 请求频率限制
        self.requests_per_second = 0.5  # 最大每秒0.5个请求
        self.last_request_time = 0
        
        # 宾夕法尼亚州主要城市代码
        self.pa_city_codes = {
            "Philadelphia": "PA0001",
            "Pittsburgh": "PA0002", 
            "Allentown": "PA0003",
            "Erie": "PA0004",
            "Reading": "PA0005",
            "Scranton": "PA0006",
            "Bethlehem": "PA0007",
            "Lancaster": "PA0008",
            "Harrisburg": "PA0009",
            "Altoona": "PA0010"
        }
        
        # 宾夕法尼亚州主要行业代码
        self.pa_industry_codes = {
            "Healthcare": "62",
            "Education": "61", 
            "Manufacturing": "31-33",
            "Technology": "51",
            "Finance": "52",
            "Energy": "22",
            "Agriculture": "11",
            "Tourism": "72",
            "Transportation": "48-49"
        }
    
    def _rate_limit(self):
        """实现请求频率限制"""
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        min_interval = 1.0 / self.requests_per_second
        
        if time_since_last < min_interval:
            sleep_time = min_interval - time_since_last
            time.sleep(sleep_time)
        
        self.last_request_time = time.time()
    
    def get_pennsylvania_employment_data(self, occupation_codes: List[str], 
                                       start_year: int = 2020, 
                                       end_year: int = 2023) -> Dict[str, Any]:
        """
        获取宾夕法尼亚州就业数据
        
        Args:
            occupation_codes: 职业代码列表
            start_year: 开始年份
            end_year: 结束年份
            
        Returns:
            宾夕法尼亚州就业数据字典
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
            logger.info(f"请求宾夕法尼亚州BLS数据: {occupation_codes}")
            response = requests.post(
                f"{self.base_url}/timeseries/data/",
                headers=self.headers,
                json=request_data,
                timeout=30
            )
            response.raise_for_status()
            
            data = response.json()
            
            if data.get("status") == "REQUEST_SUCCEEDED":
                logger.info("宾夕法尼亚州BLS数据请求成功")
                return data
            else:
                logger.error(f"BLS API错误: {data.get('message', '未知错误')}")
                return {}
                
        except requests.exceptions.RequestException as e:
            logger.error(f"宾夕法尼亚州BLS API请求失败: {e}")
            return {}
    
    def get_pennsylvania_salary_data(self, occupation_codes: List[str]) -> pd.DataFrame:
        """
        获取宾夕法尼亚州薪资数据
        
        Args:
            occupation_codes: 职业代码列表
            
        Returns:
            宾夕法尼亚州薪资数据DataFrame
        """
        # 薪资数据通常使用不同的系列ID
        # 这里需要根据具体的BLS数据系列进行调整
        salary_codes = [code.replace("00", "01") for code in occupation_codes]  # 示例转换
        
        data = self.get_pennsylvania_employment_data(salary_codes)
        
        if not data or "Results" not in data:
            return pd.DataFrame()
        
        salary_data = []
        
        for series in data["Results"]["series"]:
            series_id = series["seriesID"]
            occupation_name = series.get("catalog", {}).get("series_title", "未知")
            
            for item in series["data"]:
                salary_data.append({
                    "series_id": series_id,
                    "occupation": occupation_name,
                    "state": self.pa_state_name,
                    "year": int(item["year"]),
                    "period": item["period"],
                    "salary": float(item["value"]) if item["value"] != "null" else None,
                    "footnotes": item.get("footnotes", [])
                })
        
        return pd.DataFrame(salary_data)
    
    def get_pennsylvania_employment_by_city(self, occupation_codes: List[str]) -> pd.DataFrame:
        """
        获取宾夕法尼亚州各城市就业数据
        
        Args:
            occupation_codes: 职业代码列表
            
        Returns:
            宾夕法尼亚州城市就业数据DataFrame
        """
        city_employment_data = []
        
        for city_name, city_code in self.pa_city_codes.items():
            # 为每个城市构建特定的系列ID
            city_occupation_codes = [f"{city_code}{code}" for code in occupation_codes]
            
            data = self.get_pennsylvania_employment_data(city_occupation_codes)
            
            if data and "Results" in data:
                for series in data["Results"]["series"]:
                    series_id = series["seriesID"]
                    occupation_name = series.get("catalog", {}).get("series_title", "未知")
                    
                    for item in series["data"]:
                        city_employment_data.append({
                            "series_id": series_id,
                            "occupation": occupation_name,
                            "city": city_name,
                            "state": self.pa_state_name,
                            "year": int(item["year"]),
                            "period": item["period"],
                            "employment": float(item["value"]) if item["value"] != "null" else None,
                            "footnotes": item.get("footnotes", [])
                        })
            
            # 添加延迟避免请求过于频繁
            time.sleep(1)
        
        return pd.DataFrame(city_employment_data)
    
    def get_pennsylvania_industry_data(self, industry_codes: List[str]) -> pd.DataFrame:
        """
        获取宾夕法尼亚州行业数据
        
        Args:
            industry_codes: 行业代码列表
            
        Returns:
            宾夕法尼亚州行业数据DataFrame
        """
        industry_data = []
        
        for industry_name, industry_code in self.pa_industry_codes.items():
            if industry_code in industry_codes:
                # 构建行业特定的系列ID
                industry_series_ids = [f"PA{industry_code}0000000000000"]  # 示例格式
                
                data = self.get_pennsylvania_employment_data(industry_series_ids)
                
                if data and "Results" in data:
                    for series in data["Results"]["series"]:
                        series_id = series["seriesID"]
                        
                        for item in series["data"]:
                            industry_data.append({
                                "series_id": series_id,
                                "industry": industry_name,
                                "industry_code": industry_code,
                                "state": self.pa_state_name,
                                "year": int(item["year"]),
                                "period": item["period"],
                                "employment": float(item["value"]) if item["value"] != "null" else None,
                                "footnotes": item.get("footnotes", [])
                            })
                
                # 添加延迟
                time.sleep(1)
        
        return pd.DataFrame(industry_data)
    
    def search_pennsylvania_occupations(self, keyword: str) -> List[Dict[str, str]]:
        """
        搜索宾夕法尼亚州职业
        
        Args:
            keyword: 搜索关键词
            
        Returns:
            匹配的职业列表
        """
        # 宾夕法尼亚州常见职业映射
        pa_occupations = {
            "data scientist": ["15-2051.00"],
            "software developer": ["15-1252.00"],
            "data analyst": ["15-2051.00"],
            "machine learning engineer": ["15-1299.00"],
            "business analyst": ["13-1111.00"],
            "project manager": ["11-9199.00"],
            "product manager": ["11-9199.00"],
            "data engineer": ["15-1299.00"],
            "devops engineer": ["15-1299.00"],
            "cloud architect": ["15-1299.00"],
            "nurse": ["29-1141.00"],
            "teacher": ["25-2021.00"],
            "engineer": ["17-2199.00"],
            "accountant": ["13-2011.00"],
            "marketing manager": ["11-2021.00"],
            "sales representative": ["41-4011.00"],
            "customer service": ["43-4051.00"],
            "administrative assistant": ["43-6011.00"],
            "truck driver": ["53-3032.00"],
            "construction worker": ["47-2061.00"]
        }
        
        results = []
        keyword_lower = keyword.lower()
        
        for occupation, codes in pa_occupations.items():
            if keyword_lower in occupation:
                results.append({
                    "name": occupation,
                    "codes": codes,
                    "state": self.pa_state_name,
                    "description": f"宾夕法尼亚州职业代码: {', '.join(codes)}"
                })
        
        return results
    
    def get_pennsylvania_market_summary(self) -> Dict[str, Any]:
        """
        获取宾夕法尼亚州市场摘要
        
        Returns:
            宾夕法尼亚州市场摘要数据
        """
        # 由于BLS API需要注册，这里提供模拟的宾夕法尼亚州数据
        summary = {
            "state": self.pa_state_name,
            "state_code": self.pa_state_code,
            "total_employment": 6000000,
            "unemployment_rate": 4.2,
            "average_salary": 55000,
            "median_salary": 52000,
            "top_growing_occupations": [
                {"occupation": "数据科学家", "growth_rate": 15.2, "employment": 2500},
                {"occupation": "软件开发工程师", "growth_rate": 12.8, "employment": 15000},
                {"occupation": "机器学习工程师", "growth_rate": 18.5, "employment": 1200},
                {"occupation": "云架构师", "growth_rate": 14.3, "employment": 800},
                {"occupation": "数据分析师", "growth_rate": 11.7, "employment": 3500}
            ],
            "top_industries": [
                {"industry": "医疗保健", "employment": 800000, "growth": 2.1},
                {"industry": "教育", "employment": 600000, "growth": 1.8},
                {"industry": "制造业", "employment": 500000, "growth": 0.5},
                {"industry": "技术", "employment": 300000, "growth": 3.2},
                {"industry": "金融", "employment": 250000, "growth": 1.5}
            ],
            "major_cities": [
                {"city": "费城", "employment": 1500000, "avg_salary": 62000, "unemployment": 4.1},
                {"city": "匹兹堡", "employment": 1200000, "avg_salary": 58000, "unemployment": 4.3},
                {"city": "阿伦敦", "employment": 400000, "avg_salary": 52000, "unemployment": 4.5},
                {"city": "伊利", "employment": 300000, "avg_salary": 48000, "unemployment": 4.8},
                {"city": "雷丁", "employment": 250000, "avg_salary": 50000, "unemployment": 4.2}
            ],
            "education_requirements": {
                "bachelor_degree": 35.2,
                "master_degree": 12.8,
                "associate_degree": 18.5,
                "high_school": 28.3,
                "no_formal_education": 5.2
            },
            "skill_demand": {
                "python": 45.2,
                "java": 38.7,
                "javascript": 42.1,
                "sql": 52.3,
                "aws": 28.9,
                "machine_learning": 15.6,
                "data_analysis": 41.8,
                "project_management": 33.4
            }
        }
        
        return summary

class PennsylvaniaMarketAnalyzer:
    """宾夕法尼亚州市场分析器"""
    
    def __init__(self, api_key: Optional[str] = None):
        """
        初始化宾夕法尼亚州市场分析器
        
        Args:
            api_key: BLS API密钥
        """
        self.client = PennsylvaniaBLSAPI(api_key)
        self.employment_data = pd.DataFrame()
        self.salary_data = pd.DataFrame()
        self.city_data = pd.DataFrame()
        self.industry_data = pd.DataFrame()
    
    def analyze_pennsylvania_trends(self, occupation_codes: List[str]) -> Dict[str, Any]:
        """
        分析宾夕法尼亚州趋势
        
        Args:
            occupation_codes: 职业代码列表
            
        Returns:
            趋势分析结果
        """
        logger.info(f"分析宾夕法尼亚州趋势: {occupation_codes}")
        
        # 获取就业数据
        employment_df = self.client.get_pennsylvania_employment_data(occupation_codes)
        salary_df = self.client.get_pennsylvania_salary_data(occupation_codes)
        
        if not employment_df and not salary_df:
            return {"error": "无法获取数据"}
        
        results = {
            "state": "Pennsylvania",
            "occupation_codes": occupation_codes,
            "employment_trends": {},
            "salary_trends": {},
            "growth_rates": {},
            "summary": {}
        }
        
        # 分析就业趋势
        if employment_df:
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
        if salary_df:
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
        results["summary"] = self._generate_pennsylvania_summary(results)
        
        return results
    
    def _generate_pennsylvania_summary(self, analysis_results: Dict[str, Any]) -> Dict[str, Any]:
        """
        生成宾夕法尼亚州分析摘要
        
        Args:
            analysis_results: 分析结果
            
        Returns:
            摘要信息
        """
        summary = {
            "state": "Pennsylvania",
            "total_occupations": len(analysis_results.get("occupation_codes", [])),
            "fastest_growing": None,
            "highest_paid": None,
            "average_growth_rate": 0,
            "average_salary_growth": 0
        }
        
        # 找到增长最快的职业
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
        
        # 找到薪资最高的职业
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
    
    def get_pennsylvania_insights(self, target_occupations: List[str]) -> Dict[str, Any]:
        """
        获取宾夕法尼亚州洞察
        
        Args:
            target_occupations: 目标职业列表
            
        Returns:
            宾夕法尼亚州洞察数据
        """
        logger.info(f"获取宾夕法尼亚州洞察: {target_occupations}")
        
        # 搜索职业代码
        occupation_codes = []
        for occupation in target_occupations:
            search_results = self.client.search_pennsylvania_occupations(occupation)
            for result in search_results:
                occupation_codes.extend(result["codes"])
        
        if not occupation_codes:
            return {"error": "未找到匹配的职业代码"}
        
        # 分析趋势
        trends = self.analyze_pennsylvania_trends(occupation_codes)
        
        # 获取市场摘要
        market_summary = self.client.get_pennsylvania_market_summary()
        
        # 生成洞察
        insights = {
            "state": "Pennsylvania",
            "target_occupations": target_occupations,
            "trends_analysis": trends,
            "market_summary": market_summary,
            "recommendations": self._generate_pennsylvania_recommendations(trends, market_summary),
            "market_outlook": self._assess_pennsylvania_outlook(trends, market_summary)
        }
        
        return insights
    
    def _generate_pennsylvania_recommendations(self, trends: Dict[str, Any], 
                                             market_summary: Dict[str, Any]) -> List[str]:
        """
        生成宾夕法尼亚州建议
        
        Args:
            trends: 趋势分析结果
            market_summary: 市场摘要
            
        Returns:
            建议列表
        """
        recommendations = []
        
        summary = trends.get("summary", {})
        market = market_summary
        
        if summary.get("fastest_growing"):
            fastest = summary["fastest_growing"]
            recommendations.append(
                f"考虑进入 {fastest['occupation']} 领域，"
                f"宾夕法尼亚州就业增长率为 {fastest['growth_rate']:.1f}%"
            )
        
        if summary.get("highest_paid"):
            highest = summary["highest_paid"]
            recommendations.append(
                f"{highest['occupation']} 提供最高薪资，"
                f"宾夕法尼亚州平均薪资为 ${highest['salary']:,.0f}"
            )
        
        # 基于宾夕法尼亚州特定数据添加建议
        if market.get("top_growing_occupations"):
            top_occupation = market["top_growing_occupations"][0]
            recommendations.append(
                f"宾夕法尼亚州增长最快的职业是 {top_occupation['occupation']}，"
                f"增长率为 {top_occupation['growth_rate']}%"
            )
        
        return recommendations
    
    def _assess_pennsylvania_outlook(self, trends: Dict[str, Any], 
                                   market_summary: Dict[str, Any]) -> str:
        """
        评估宾夕法尼亚州市场前景
        
        Args:
            trends: 趋势分析结果
            market_summary: 市场摘要
            
        Returns:
            市场前景评估
        """
        summary = trends.get("summary", {})
        market = market_summary
        
        avg_growth = summary.get("average_growth_rate", 0)
        unemployment_rate = market.get("unemployment_rate", 0)
        
        if avg_growth > 5 and unemployment_rate < 4:
            return "宾夕法尼亚州市场前景非常乐观，就业增长强劲，失业率低"
        elif avg_growth > 2 and unemployment_rate < 5:
            return "宾夕法尼亚州市场前景良好，就业稳步增长"
        elif avg_growth > 0 and unemployment_rate < 6:
            return "宾夕法尼亚州市场前景稳定，就业略有增长"
        else:
            return "宾夕法尼亚州市场前景谨慎，就业增长缓慢"

def main():
    """主函数 - 宾夕法尼亚州BLS API集成示例"""
    print("=" * 60)
    print("宾夕法尼亚州BLS API集成 - 劳工统计局API集成")
    print("=" * 60)
    
    # 创建宾夕法尼亚州分析器
    analyzer = PennsylvaniaMarketAnalyzer()
    
    while True:
        print("\n请选择操作:")
        print("1. 搜索宾夕法尼亚州职业")
        print("2. 分析宾夕法尼亚州职业趋势")
        print("3. 获取宾夕法尼亚州市场洞察")
        print("4. 获取宾夕法尼亚州市场摘要")
        print("5. 退出")
        
        choice = input("\n请输入您的选择 (1-5): ").strip()
        
        if choice == '1':
            keyword = input("请输入职业关键词: ").strip()
            if keyword:
                results = analyzer.client.search_pennsylvania_occupations(keyword)
                if results:
                    print(f"\n找到 {len(results)} 个匹配的宾夕法尼亚州职业:")
                    for result in results:
                        print(f"  - {result['name']}: {result['description']}")
                else:
                    print("未找到匹配的宾夕法尼亚州职业")
        
        elif choice == '2':
            occupation_codes = input("请输入职业代码 (逗号分隔): ").strip().split(',')
            occupation_codes = [code.strip() for code in occupation_codes if code.strip()]
            
            if occupation_codes:
                trends = analyzer.analyze_pennsylvania_trends(occupation_codes)
                if "error" not in trends:
                    print("\n宾夕法尼亚州职业趋势分析结果:")
                    print(json.dumps(trends, indent=2, ensure_ascii=False))
                else:
                    print(f"分析失败: {trends['error']}")
        
        elif choice == '3':
            occupations = input("请输入目标职业 (逗号分隔): ").strip().split(',')
            occupations = [occ.strip() for occ in occupations if occ.strip()]
            
            if occupations:
                insights = analyzer.get_pennsylvania_insights(occupations)
                if "error" not in insights:
                    print("\n宾夕法尼亚州市场洞察:")
                    print(json.dumps(insights, indent=2, ensure_ascii=False))
                else:
                    print(f"获取洞察失败: {insights['error']}")
        
        elif choice == '4':
            summary = analyzer.client.get_pennsylvania_market_summary()
            print("\n宾夕法尼亚州市场摘要:")
            print(json.dumps(summary, indent=2, ensure_ascii=False))
        
        elif choice == '5':
            print("感谢使用宾夕法尼亚州BLS API集成!")
            break
        
        else:
            print("无效选择，请重试!")

if __name__ == "__main__":
    main()



