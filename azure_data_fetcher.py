#!/usr/bin/env python3
"""
Azure Data Fetcher Module
Fetches weather data from multiple APIs and stores in Azure
"""

import os
import json
import requests
import time
from datetime import datetime, timedelta
from pathlib import Path
from azure_storage import AzureStorage
from azure_database import AzureDatabase


class AzureDataFetcher:
    """Fetch and store weather data using Azure services"""
    
    def __init__(self, storage=None, database=None):
        """Initialize data fetcher
        
        Args:
            storage (AzureStorage): Azure storage instance
            database (AzureDatabase): Azure database instance
        """
        self.storage = storage or AzureStorage()
        self.database = database or AzureDatabase()
        self.session = requests.Session()
    
    def fetch_nasa_data(self, latitude, longitude, start_date, end_date):
        """Fetch data from NASA POWER API
        
        Args:
            latitude (float): Location latitude
            longitude (float): Location longitude
            start_date (str): Start date (YYYYMMDD)
            end_date (str): End date (YYYYMMDD)
        
        Returns:
            dict: API response or None
        """
        try:
            base_url = "https://power.larc.nasa.gov/api/v1/aggregate"
            params = {
                'start': start_date,
                'end': end_date,
                'latitude': latitude,
                'longitude': longitude,
                'community': 'RE',
                'parameters': 'T2M,RH2M,PS,WS10M',
                'format': 'JSON'
            }
            
            response = self.session.get(base_url, params=params, timeout=30)
            response.raise_for_status()
            
            print(f"✓ NASA POWER API: {start_date} to {end_date}")
            return response.json()
        except Exception as e:
            print(f"✗ NASA POWER API failed: {str(e)}")
            return None
    
    def fetch_openmeteo_data(self, latitude, longitude, start_date, end_date):
        """Fetch data from Open-Meteo API
        
        Args:
            latitude (float): Location latitude
            longitude (float): Location longitude
            start_date (str): Start date (YYYY-MM-DD)
            end_date (str): End date (YYYY-MM-DD)
        
        Returns:
            dict: API response or None
        """
        try:
            base_url = "https://archive-api.open-meteo.com/v1/archive"
            params = {
                'latitude': latitude,
                'longitude': longitude,
                'start_date': start_date,
                'end_date': end_date,
                'hourly': 'temperature_2m,relative_humidity_2m,surface_pressure,wind_speed_10m',
                'timezone': 'UTC'
            }
            
            response = self.session.get(base_url, params=params, timeout=30)
            response.raise_for_status()
            
            print(f"✓ Open-Meteo API: {start_date} to {end_date}")
            return response.json()
        except Exception as e:
            print(f"✗ Open-Meteo API failed: {str(e)}")
            return None
    
    def fetch_weatherbit_data(self, latitude, longitude, start_date, end_date, api_key=None):
        """Fetch data from Weatherbit API
        
        Args:
            latitude (float): Location latitude
            longitude (float): Location longitude
            start_date (str): Start date (YYYY-MM-DD)
            end_date (str): End date (YYYY-MM-DD)
            api_key (str): Weatherbit API key
        
        Returns:
            dict: API response or None
        """
        try:
            api_key = api_key or os.getenv('WEATHERBIT_API_KEY')
            if not api_key:
                print("⚠ Weatherbit API key not found")
                return None
            
            base_url = "https://api.weatherbit.io/v2.0/history/daily"
            params = {
                'lat': latitude,
                'lon': longitude,
                'start_date': start_date,
                'end_date': end_date,
                'key': api_key
            }
            
            response = self.session.get(base_url, params=params, timeout=30)
            response.raise_for_status()
            
            print(f"✓ Weatherbit API: {start_date} to {end_date}")
            return response.json()
        except Exception as e:
            print(f"✗ Weatherbit API failed: {str(e)}")
            return None
    
    def parse_nasa_response(self, response, source_date):
        """Parse NASA POWER response into database items
        
        Args:
            response (dict): API response
            source_date (str): Data source date
        
        Returns:
            list: List of items for database
        """
        items = []
        try:
            if not response or 'properties' not in response:
                return items
            
            data = response['properties']['daily']
            
            for date_str, values in data.items():
                if date_str.startswith('T2M'):
                    continue
                
                item = {
                    'source': 'nasa',
                    'timestamp': f"{date_str[:4]}-{date_str[4:6]}-{date_str[6:8]}T12:00:00Z",
                    'temperature': values.get('T2M'),
                    'humidity': values.get('RH2M'),
                    'pressure': values.get('PS'),
                    'wind_speed': values.get('WS10M'),
                    'source_date': source_date
                }
                items.append(item)
            
            return items
        except Exception as e:
            print(f"✗ Parse NASA response failed: {str(e)}")
            return items
    
    def parse_openmeteo_response(self, response, source_date):
        """Parse Open-Meteo response into database items
        
        Args:
            response (dict): API response
            source_date (str): Data source date
        
        Returns:
            list: List of items for database
        """
        items = []
        try:
            if not response or 'hourly' not in response:
                return items
            
            hourly = response['hourly']
            times = hourly['time']
            temps = hourly['temperature_2m']
            humidity = hourly['relative_humidity_2m']
            pressure = hourly['surface_pressure']
            wind = hourly['wind_speed_10m']
            
            for i, timestamp in enumerate(times):
                item = {
                    'source': 'openmeteo',
                    'timestamp': timestamp,
                    'temperature': temps[i] if i < len(temps) else None,
                    'humidity': humidity[i] if i < len(humidity) else None,
                    'pressure': pressure[i] if i < len(pressure) else None,
                    'wind_speed': wind[i] if i < len(wind) else None,
                    'source_date': source_date
                }
                items.append(item)
            
            return items
        except Exception as e:
            print(f"✗ Parse Open-Meteo response failed: {str(e)}")
            return items
    
    def fetch_and_store_march_april_2026(self, latitude=40.7128, longitude=-74.0060):
        """Fetch and store March-April 2026 data
        
        Args:
            latitude (float): Location latitude (default: NYC)
            longitude (float): Location longitude (default: NYC)
        
        Returns:
            dict: Summary of fetched data
        """
        print("\n" + "="*60)
        print("FETCHING MARCH-APRIL 2026 DATA")
        print("="*60)
        
        summary = {
            'nasa': 0,
            'openmeteo': 0,
            'total_items': 0,
            'start_date': '2026-03-01',
            'end_date': '2026-04-30'
        }
        
        # Fetch NASA POWER data
        print("\n📡 NASA POWER API:")
        nasa_data = self.fetch_nasa_data(latitude, longitude, '20260301', '20260430')
        if nasa_data:
            nasa_items = self.parse_nasa_response(nasa_data, '2026-03-01 to 2026-04-30')
            if self.database.batch_put_items(nasa_items):
                summary['nasa'] = len(nasa_items)
        
        # Fetch Open-Meteo data
        print("\n📡 Open-Meteo API:")
        openmeteo_data = self.fetch_openmeteo_data(latitude, longitude, '2026-03-01', '2026-04-30')
        if openmeteo_data:
            openmeteo_items = self.parse_openmeteo_response(openmeteo_data, '2026-03-01 to 2026-04-30')
            if self.database.batch_put_items(openmeteo_items):
                summary['openmeteo'] = len(openmeteo_items)
        
        summary['total_items'] = summary['nasa'] + summary['openmeteo']
        
        print("\n" + "="*60)
        print("MARCH-APRIL 2026 DATA SUMMARY")
        print("="*60)
        for key, value in summary.items():
            print(f"{key}: {value}")
        
        return summary


if __name__ == "__main__":
    fetcher = AzureDataFetcher()
    
    print("\n" + "="*60)
    print("AZURE DATA FETCHER")
    print("="*60)
    
    # Example: Fetch and store March-April 2026 data
    result = fetcher.fetch_and_store_march_april_2026()
