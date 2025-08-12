#!/usr/bin/env python3
"""
Test Example for AST Code Chunker

This file demonstrates various code structures that the AST chunker can handle.
"""

import os
import sys
from typing import List, Dict, Optional
from dataclasses import dataclass
import json

# Global configuration
DEBUG_MODE = True
VERSION = "2.0.0"
MAX_RETRIES = 3


@dataclass
class User:
    """Represents a user in the system."""
    id: int
    name: str
    email: str
    active: bool = True


class DatabaseConnection:
    """Manages database connections and queries."""
    
    def __init__(self, host: str, port: int = 5432):
        """
        Initialize database connection.
        
        Args:
            host: Database host
            port: Database port
        """
        self.host = host
        self.port = port
        self.connection = None
        self._cache = {}
    
    def connect(self) -> bool:
        """Establish connection to database."""
        try:
            # Simulated connection logic
            self.connection = f"Connected to {self.host}:{self.port}"
            return True
        except Exception as e:
            print(f"Connection failed: {e}")
            return False
    
    def execute_query(self, query: str, params: Optional[Dict] = None) -> List[Dict]:
        """
        Execute a database query.
        
        Args:
            query: SQL query string
            params: Query parameters
            
        Returns:
            List of result dictionaries
        """
        if not self.connection:
            raise RuntimeError("Not connected to database")
        
        # Check cache
        cache_key = f"{query}:{json.dumps(params or {})}"
        if cache_key in self._cache:
            return self._cache[cache_key]
        
        # Simulated query execution
        results = [{"id": 1, "data": "sample"}]
        self._cache[cache_key] = results
        return results
    
    def disconnect(self):
        """Close database connection."""
        if self.connection:
            self.connection = None
            self._cache.clear()


class DataProcessor:
    """Processes and transforms data."""
    
    def __init__(self, db: DatabaseConnection):
        """
        Initialize processor with database connection.
        
        Args:
            db: Database connection instance
        """
        self.db = db
        self.processed_count = 0
    
    def process_batch(self, items: List[Dict]) -> List[Dict]:
        """
        Process a batch of items.
        
        Args:
            items: List of items to process
            
        Returns:
            Processed items
        """
        processed = []
        for item in items:
            processed_item = self._transform_item(item)
            if self._validate_item(processed_item):
                processed.append(processed_item)
                self.processed_count += 1
        
        return processed
    
    def _transform_item(self, item: Dict) -> Dict:
        """Transform a single item."""
        return {
            **item,
            "processed": True,
            "timestamp": "2024-01-01"
        }
    
    def _validate_item(self, item: Dict) -> bool:
        """Validate a processed item."""
        return item.get("processed", False)
    
    def get_statistics(self) -> Dict:
        """Get processing statistics."""
        return {
            "total_processed": self.processed_count,
            "status": "active"
        }


def create_connection(config: Dict) -> DatabaseConnection:
    """
    Factory function to create database connection.
    
    Args:
        config: Configuration dictionary
        
    Returns:
        Configured DatabaseConnection instance
    """
    host = config.get("host", "localhost")
    port = config.get("port", 5432)
    
    conn = DatabaseConnection(host, port)
    if conn.connect():
        return conn
    else:
        raise ConnectionError("Failed to create database connection")


def process_data_pipeline(data: List[Dict], config: Dict) -> Dict:
    """
    Main data processing pipeline.
    
    Args:
        data: Input data
        config: Pipeline configuration
        
    Returns:
        Processing results
    """
    # Create connection
    db = create_connection(config)
    
    try:
        # Initialize processor
        processor = DataProcessor(db)
        
        # Process data
        results = processor.process_batch(data)
        
        # Get statistics
        stats = processor.get_statistics()
        
        return {
            "results": results,
            "statistics": stats,
            "success": True
        }
    
    finally:
        # Clean up
        db.disconnect()


def main():
    """Main entry point."""
    config = {
        "host": "localhost",
        "port": 5432
    }
    
    test_data = [
        {"id": 1, "value": "test1"},
        {"id": 2, "value": "test2"}
    ]
    
    try:
        result = process_data_pipeline(test_data, config)
        print(f"Processing complete: {result}")
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()