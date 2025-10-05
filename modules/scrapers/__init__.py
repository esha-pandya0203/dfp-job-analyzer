#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Scrapers Package
================

A comprehensive package for web scraping job market data from various sources.

Author: Fan Yang (CMU)
Version: 1.0
"""

from .scraper_manager import ScraperManager
from .indeed_scraper import IndeedScraper
from .onet_scraper import EnhancedONETScraper
from .skill_matcher import SkillMatcher

__all__ = [
    'ScraperManager',
    'IndeedScraper', 
    'EnhancedONETScraper',
    'SkillMatcher'
]
