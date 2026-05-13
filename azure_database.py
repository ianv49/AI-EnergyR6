#!/usr/bin/env python3
"""
Azure Cosmos DB Module
Handles database operations for storing and querying weather data
"""

import json
from datetime import datetime, timedelta
from uuid import uuid4
from azure_config import AzureConfig


class AzureDatabase:
    """Azure Cosmos DB operations for weather data"""
    
    def __init__(self, config=None, database_name='energy-data-db', container_name='energy-data'):
        """Initialize Azure database
        
        Args:
            config (AzureConfig): Azure configuration object
            database_name (str): Database name
            container_name (str): Container name
        """
        self.config = config or AzureConfig()
        self.cosmos_client = self.config.get_cosmos_client()
        self.database_name = database_name
        self.container_name = container_name
        
        # Create or get database and container
        self.database = self.cosmos_client.get_database_client(database_name)
        self.container = self.database.get_container_client(container_name)
    
    def put_item(self, item):
        """Insert or update a single item in database
        
        Args:
            item (dict): Item to insert
        
        Returns:
            dict: Item response with id
        """
        try:
            if 'id' not in item:
                item['id'] = str(uuid4())
            
            response = self.container.upsert_item(item)
            print(f"✓ Stored item: {item.get('id')} - {item.get('source', 'unknown')}")
            return response
        except Exception as e:
            print(f"✗ Failed to store item: {str(e)}")
            return None
    
    def batch_put_items(self, items, batch_size=100):
        """Insert or update multiple items in batch
        
        Args:
            items (list): List of items to insert
            batch_size (int): Number of items per batch
        
        Returns:
            int: Number of items stored
        """
        count = 0
        print(f"\nStoring {len(items)} items in batches of {batch_size}...")
        
        for i in range(0, len(items), batch_size):
            batch = items[i:i+batch_size]
            
            for item in batch:
                if self.put_item(item):
                    count += 1
            
            print(f"  ✓ Batch {i//batch_size + 1}: {len(batch)} items stored")
        
        print(f"✓ Total: {count} items stored")
        return count
    
    def get_item(self, item_id, partition_key=None):
        """Retrieve a single item by ID
        
        Args:
            item_id (str): Item ID
            partition_key (str): Partition key value (source or date)
        
        Returns:
            dict: Item data
        """
        try:
            response = self.container.read_item(item=item_id, partition_key=partition_key or item_id)
            return response
        except Exception as e:
            print(f"✗ Failed to retrieve item {item_id}: {str(e)}")
            return None
    
    def query_by_source(self, source, limit=100):
        """Query items by data source
        
        Args:
            source (str): Data source (nasa, openmeteo, weatherbit, meteostat)
            limit (int): Maximum items to return
        
        Returns:
            list: Query results
        """
        try:
            query = f"""
                SELECT * FROM c 
                WHERE c.source = @source
                ORDER BY c.timestamp DESC
            """
            
            parameters = [{"name": "@source", "value": source}]
            results = list(self.container.query_items(query=query, parameters=parameters, max_item_count=limit))
            
            print(f"✓ Found {len(results)} items from source: {source}")
            return results
        except Exception as e:
            print(f"✗ Query failed: {str(e)}")
            return []
    
    def query_by_source_date(self, source, date, limit=1000):
        """Query items by source and specific date
        
        Args:
            source (str): Data source
            date (str): Date (YYYY-MM-DD)
            limit (int): Maximum items to return
        
        Returns:
            list: Query results
        """
        try:
            start_time = f"{date}T00:00:00Z"
            end_time = f"{date}T23:59:59Z"
            
            query = f"""
                SELECT * FROM c 
                WHERE c.source = @source 
                AND c.timestamp >= @start_time
                AND c.timestamp <= @end_time
                ORDER BY c.timestamp ASC
            """
            
            parameters = [
                {"name": "@source", "value": source},
                {"name": "@start_time", "value": start_time},
                {"name": "@end_time", "value": end_time}
            ]
            
            results = list(self.container.query_items(query=query, parameters=parameters, max_item_count=limit))
            
            print(f"✓ Found {len(results)} items from {source} on {date}")
            return results
        except Exception as e:
            print(f"✗ Query failed: {str(e)}")
            return []
    
    def query_by_date_range(self, start_date, end_date, source=None, limit=10000):
        """Query items by date range
        
        Args:
            start_date (str): Start date (YYYY-MM-DD)
            end_date (str): End date (YYYY-MM-DD)
            source (str): Optional source filter
            limit (int): Maximum items to return
        
        Returns:
            list: Query results
        """
        try:
            start_time = f"{start_date}T00:00:00Z"
            end_time = f"{end_date}T23:59:59Z"
            
            if source:
                query = f"""
                    SELECT * FROM c 
                    WHERE c.source = @source
                    AND c.timestamp >= @start_time
                    AND c.timestamp <= @end_time
                    ORDER BY c.timestamp ASC
                """
                parameters = [
                    {"name": "@source", "value": source},
                    {"name": "@start_time", "value": start_time},
                    {"name": "@end_time", "value": end_time}
                ]
            else:
                query = f"""
                    SELECT * FROM c 
                    WHERE c.timestamp >= @start_time
                    AND c.timestamp <= @end_time
                    ORDER BY c.timestamp ASC
                """
                parameters = [
                    {"name": "@start_time", "value": start_time},
                    {"name": "@end_time", "value": end_time}
                ]
            
            results = list(self.container.query_items(query=query, parameters=parameters, max_item_count=limit))
            
            date_range = f"{start_date} to {end_date}"
            print(f"✓ Found {len(results)} items for {date_range}")
            return results
        except Exception as e:
            print(f"✗ Query failed: {str(e)}")
            return []
    
    def delete_item(self, item_id, partition_key=None):
        """Delete an item from database
        
        Args:
            item_id (str): Item ID
            partition_key (str): Partition key value
        
        Returns:
            bool: True if successful
        """
        try:
            self.container.delete_item(item=item_id, partition_key=partition_key or item_id)
            print(f"✓ Deleted item: {item_id}")
            return True
        except Exception as e:
            print(f"✗ Failed to delete item: {str(e)}")
            return False
    
    def get_table_stats(self):
        """Get statistics about stored data
        
        Returns:
            dict: Statistics including count, sources, date range
        """
        try:
            # Count total items
            count_query = "SELECT VALUE COUNT(1) FROM c"
            count = list(self.container.query_items(query=count_query))[0]
            
            # Get unique sources
            sources_query = "SELECT DISTINCT c.source FROM c"
            sources = [item['source'] for item in self.container.query_items(query=sources_query)]
            
            # Get date range
            date_range_query = """
                SELECT {
                    'min_date': MIN(c.timestamp),
                    'max_date': MAX(c.timestamp)
                } FROM c
            """
            date_range = list(self.container.query_items(query=date_range_query))[0]
            
            stats = {
                'total_items': count,
                'unique_sources': len(sources),
                'sources': sources,
                'min_date': date_range['min_date'],
                'max_date': date_range['max_date']
            }
            
            return stats
        except Exception as e:
            print(f"✗ Failed to get stats: {str(e)}")
            return {}


if __name__ == "__main__":
    db = AzureDatabase()
    
    print("\n" + "="*60)
    print("AZURE COSMOS DB OPERATIONS")
    print("="*60)
    
    # Example: Store a single item
    sample_item = {
        'source': 'nasa',
        'timestamp': datetime.now().isoformat() + 'Z',
        'temperature': 25.5,
        'humidity': 65.0,
        'pressure': 1013.25,
        'wind_speed': 5.2
    }
    db.put_item(sample_item)
    
    # Example: Get stats
    print("\nDatabase Statistics:")
    stats = db.get_table_stats()
    for key, value in stats.items():
        print(f"  {key}: {value}")
