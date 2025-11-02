"""
MCP Client for MongoDB Database Context
Compatible with mock MCP server endpoints
"""
import os
import json
import logging
import requests
from typing import List, Dict, Any, Optional
from datetime import datetime
import hashlib

logger = logging.getLogger(__name__)

class MCPClient:
    """Client for interacting with MCP Server"""
    
    def __init__(self, mcp_url: str = None, cache_ttl: int = 300):
        self.mcp_url = mcp_url or os.getenv("MCP_SERVER_URL", "http://localhost:3000")
        self.cache_ttl = cache_ttl
        self.enabled = os.getenv("MCP_ENABLED", "true").lower() == "true"
        self._cache = {}
        self._cache_timestamps = {}
        
        if self.enabled:
            logger.info(f"MCP Client initialized with server: {self.mcp_url}")
            self._verify_connection()
        else:
            logger.warning("MCP Client is disabled. Using fallback static schema.")
    
    def _verify_connection(self):
        """Verify MCP server is reachable"""
        try:
            response = requests.get(f"{self.mcp_url}/health", timeout=5)
            if response.status_code == 200:
                logger.info("✅ MCP Server connection verified")
                data = response.json()
                logger.info(f"MCP Server version: {data.get('version', 'unknown')}")
                logger.info(f"Document count: {data.get('document_count', 'unknown')}")
            else:
                logger.error(f"MCP Server health check failed: {response.status_code}")
                self.enabled = False
        except requests.exceptions.ConnectionError:
            logger.error(f"Cannot connect to MCP Server at {self.mcp_url}")
            logger.warning("MCP Server may still be starting up. Will retry on first use.")
        except Exception as e:
            logger.error(f"MCP Server verification failed: {e}")
            self.enabled = False
    
    def _get_cache_key(self, method: str, params: Dict) -> str:
        """Generate cache key from method and parameters"""
        params_str = json.dumps(params, sort_keys=True, default=str)
        return hashlib.md5(f"{method}:{params_str}".encode()).hexdigest()
    
    def _is_cache_valid(self, cache_key: str) -> bool:
        """Check if cached data is still valid"""
        if cache_key not in self._cache_timestamps:
            return False
        
        timestamp = self._cache_timestamps[cache_key]
        age = (datetime.utcnow() - timestamp).total_seconds()
        return age < self.cache_ttl
    
    def _get_cached(self, cache_key: str) -> Optional[Any]:
        """Get cached data if valid"""
        if self._is_cache_valid(cache_key):
            logger.debug(f"Cache hit for key: {cache_key[:8]}...")
            return self._cache.get(cache_key)
        return None
    
    def _set_cache(self, cache_key: str, data: Any):
        """Store data in cache"""
        self._cache[cache_key] = data
        self._cache_timestamps[cache_key] = datetime.utcnow()
    
    def _call_mcp_tool(self, tool_name: str, parameters: Dict) -> Dict[str, Any]:
        """
        Call an MCP tool with given parameters
        
        Args:
            tool_name: Name of the MCP tool (e.g., 'listCollections', 'getDistinctValues')
            parameters: Tool-specific parameters
            
        Returns:
            Tool execution results
        """
        if not self.enabled:
            raise RuntimeError("MCP Client is disabled")
        
        # Check cache first
        cache_key = self._get_cache_key(tool_name, parameters)
        cached_result = self._get_cached(cache_key)
        if cached_result is not None:
            return cached_result
        
        try:
            # FIXED: Use correct endpoint format for mock server
            url = f"{self.mcp_url}/mcp/tools/{tool_name}"
            
            logger.info(f"Calling MCP tool: {tool_name} at {url}")
            logger.debug(f"Parameters: {parameters}")
            
            response = requests.post(
                url,
                json=parameters,
                timeout=10,
                headers={"Content-Type": "application/json"}
            )
            response.raise_for_status()
            result = response.json()
            
            logger.debug(f"MCP tool '{tool_name}' result: {result}")
            
            # Cache successful results
            self._set_cache(cache_key, result)
            
            logger.info(f"MCP tool '{tool_name}' executed successfully")
            return result
            
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 404:
                logger.error(f"MCP tool '{tool_name}' not found at {url}")
            else:
                logger.error(f"MCP tool call failed for '{tool_name}': HTTP {e.response.status_code}")
            logger.error(f"Response: {e.response.text if hasattr(e, 'response') else 'No response'}")
            raise RuntimeError(f"MCP server error: {e}")
        except requests.exceptions.ConnectionError:
            logger.error(f"Cannot connect to MCP Server at {self.mcp_url}")
            raise RuntimeError("MCP server is not reachable")
        except Exception as e:
            logger.error(f"MCP tool call failed for '{tool_name}': {e}")
            raise RuntimeError(f"MCP server error: {e}")
    
    def list_collections(self, database: str = "cicd_db") -> List[str]:
        """Get list of collections in the database"""
        try:
            result = self._call_mcp_tool("listCollections", {"database": database})
            return result.get("collections", [])
        except Exception as e:
            logger.error(f"Failed to list collections: {e}")
            return ["cdPipelineEvents"]
    
    def get_schema(self, collection: str, database: str = "cicd_db") -> Dict[str, Any]:
        """Get comprehensive schema information for a collection"""
        try:
            result = self._call_mcp_tool("getSchema", {
                "database": database,
                "collection": collection
            })
            return result.get("schema", {})
        except Exception as e:
            logger.error(f"Failed to get schema for {collection}: {e}")
            return self._get_fallback_schema()
    
    def sample_documents(self, 
                        collection: str, 
                        database: str = "cicd_db",
                        limit: int = 10,
                        filter_query: Optional[Dict] = None) -> List[Dict[str, Any]]:
        """Get sample documents from a collection"""
        try:
            params = {
                "database": database,
                "collection": collection,
                "limit": min(limit, 50)
            }
            if filter_query:
                params["filter"] = filter_query
            
            result = self._call_mcp_tool("sampleDocuments", params)
            return result.get("documents", [])
        except Exception as e:
            logger.error(f"Failed to sample documents from {collection}: {e}")
            return []
    
    def get_distinct_values(self,
                           collection: str,
                           field: str,
                           database: str = "cicd_db",
                           limit: int = 100) -> List[Any]:
        """Get distinct values for a specific field"""
        try:
            result = self._call_mcp_tool("getDistinctValues", {
                "database": database,
                "collection": collection,
                "field": field,
                "limit": limit
            })
            values = result.get("values", [])
            logger.info(f"Got {len(values)} distinct values for {field}")
            return values
        except Exception as e:
            logger.error(f"Failed to get distinct values for {field}: {e}")
            return []
    
    def get_field_statistics(self,
                            collection: str,
                            field: str,
                            database: str = "cicd_db") -> Dict[str, Any]:
        """Get statistical information about a field"""
        try:
            result = self._call_mcp_tool("getFieldStatistics", {
                "database": database,
                "collection": collection,
                "field": field
            })
            return result.get("statistics", {})
        except Exception as e:
            logger.error(f"Failed to get statistics for {field}: {e}")
            return {}
    
    def get_indexes(self, collection: str, database: str = "cicd_db") -> List[Dict[str, Any]]:
        """Get index information for a collection"""
        try:
            result = self._call_mcp_tool("getIndexes", {
                "database": database,
                "collection": collection
            })
            return result.get("indexes", [])
        except Exception as e:
            logger.error(f"Failed to get indexes for {collection}: {e}")
            return []
    
    def build_enriched_schema_context(self, collection: str = "cdPipelineEvents") -> str:
        """Build a comprehensive schema context string for the LLM"""
        if not self.enabled:
            return self._get_fallback_schema_text()
        
        try:
            schema = self.get_schema(collection)
            samples = self.sample_documents(collection, limit=5)
            event_types = self.get_distinct_values(collection, "event_type", limit=50)
            sources = self.get_distinct_values(collection, "source", limit=20)
            users = self.get_distinct_values(collection, "user", limit=20)
            indexes = self.get_indexes(collection)
            
            context_parts = [
                f"Collection: {collection}",
                f"Source: Mock MCP Server (Real MongoDB Data)",
                "",
                "=== Field Schema ===",
                json.dumps(schema, indent=2) if schema else "Schema unavailable",
                "",
                "=== Available Event Types ===",
                ", ".join(event_types[:20]) if event_types else "No event types found",
                f"(Total: {len(event_types)} distinct types)" if event_types else "",
                "",
                "=== Available Sources ===",
                ", ".join(sources) if sources else "No sources found",
                "",
                "=== Available Users ===",
                ", ".join(users[:10]) if users else "No users found",
                f"(Total: {len(users)} distinct users)" if users else "",
                "",
                "=== Sample Documents ===",
                json.dumps(samples, indent=2, default=str) if samples else "No samples available",
                "",
                "=== Indexes (for query optimization) ===",
                json.dumps(indexes, indent=2) if indexes else "No indexes found",
            ]
            
            enriched_context = "\n".join(context_parts)
            logger.info(f"Built enriched schema context: {len(enriched_context)} characters")
            logger.info(f"Found {len(event_types)} event types, {len(sources)} sources, {len(users)} users")
            return enriched_context
            
        except Exception as e:
            logger.error(f"Failed to build enriched schema context: {e}")
            logger.warning("Falling back to static schema")
            return self._get_fallback_schema_text()
    
    def _get_fallback_schema(self) -> Dict[str, Any]:
        """Fallback static schema when MCP is unavailable"""
        return {
            "event_type": {"type": "string"},
            "event_timestamp": {"type": "date"},
            "user": {"type": "string"},
            "source": {"type": "string"},
            "duration_seconds": {"type": "number"},
            "pipeline_id": {"type": "string"},
            "metadata": {"type": "object"}
        }
    
    def _get_fallback_schema_text(self) -> str:
        """Fallback static schema text when MCP is unavailable"""
        return """
Collection: cdPipelineEvents

Fields:
- event_type: string (e.g., 'Build Stage Started', 'SAST Security Scan Started')
- event_timestamp: datetime (ISO format)
- user: string (e.g., 'Jane Doe', 'John Smith')
- source: string (e.g., 'GitLab', 'Harness', 'Security Tool')
- duration_seconds: numeric (0 for instantaneous events, >0 for timed operations)
- pipeline_id: string (e.g., 'pipeline-100')
- metadata: object (contains branch, environment, etc.)

Note: This is a fallback static schema. MCP Server is unavailable for dynamic context.
"""
    
    def clear_cache(self):
        """Clear all cached data"""
        self._cache.clear()
        self._cache_timestamps.clear()
        logger.info("MCP cache cleared")


# Singleton instance
_mcp_client_instance = None

def get_mcp_client() -> MCPClient:
    """Get or create the global MCP client instance"""
    global _mcp_client_instance
    if _mcp_client_instance is None:
        _mcp_client_instance = MCPClient()
    return _mcp_client_instance
