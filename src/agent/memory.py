import logging
import json
import os
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Tuple
import chromadb
from chromadb.utils import embedding_functions
import sqlite3
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class HealthMemoryStore:
    """
    Manages persistent storage of health data, including:
    - Health metrics over time
    - Medical document embeddings
    - User preferences and history
    - Task results and insights
    """
    
    def __init__(self, storage_path: str = "data/health_memory"):
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(parents=True, exist_ok=True)
        
        # Initialize ChromaDB for vector storage
        self.chroma_client = chromadb.PersistentClient(
            path=str(self.storage_path / "chroma")
        )
        
        # Use sentence transformer for embeddings
        self.embedding_function = embedding_functions.SentenceTransformerEmbeddingFunction(
            model_name="all-MiniLM-L6-v2"
        )
        
        # Create collections
        self.documents_collection = self.chroma_client.get_or_create_collection(
            name="medical_documents",
            embedding_function=self.embedding_function
        )
        
        self.insights_collection = self.chroma_client.get_or_create_collection(
            name="health_insights",
            embedding_function=self.embedding_function
        )
        
        # Initialize SQLite for structured data
        self.db_path = self.storage_path / "health_metrics.db"
        self._init_database()
        
    def _init_database(self):
        """Initializes SQLite database for structured health data."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Health metrics table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS health_metrics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                metric_name TEXT NOT NULL,
                value TEXT NOT NULL,
                unit TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                source TEXT,
                metadata TEXT
            )
        """)
        
        # Medications table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS medications (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                dosage TEXT,
                frequency TEXT,
                start_date DATE,
                end_date DATE,
                prescriber TEXT,
                notes TEXT,
                active BOOLEAN DEFAULT 1
            )
        """)
        
        # User preferences table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS user_preferences (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        conn.commit()
        conn.close()
    
    async def store_health_metrics(self, metrics: Dict[str, Any], source: str = "manual"):
        """Stores health metrics in the database."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        for metric_name, value in metrics.items():
            # Handle complex values
            if isinstance(value, dict):
                actual_value = value.get('value', str(value))
                unit = value.get('unit', '')
                metadata = json.dumps(value)
            else:
                actual_value = str(value)
                unit = ''
                metadata = None
                
            cursor.execute("""
                INSERT INTO health_metrics (metric_name, value, unit, source, metadata)
                VALUES (?, ?, ?, ?, ?)
            """, (metric_name, actual_value, unit, source, metadata))
            
        conn.commit()
        conn.close()
        
        logger.info(f"Stored {len(metrics)} health metrics")
    
    async def store_document(self, document_id: str, content: str, 
                           document_type: str, metadata: Dict[str, Any]):
        """Stores medical document in vector database."""
        # Add to ChromaDB
        self.documents_collection.add(
            documents=[content],
            metadatas=[{
                "document_type": document_type,
                "timestamp": datetime.now().isoformat(),
                **metadata
            }],
            ids=[document_id]
        )
        
        logger.info(f"Stored document {document_id} of type {document_type}")
    
    async def store_task_result(self, task: Any, result: Any):
        """Stores task execution results for future reference."""
        insight = {
            "task_type": task.type.value,
            "task_description": task.description,
            "timestamp": datetime.now().isoformat(),
            "success": result.success
        }
        
        if result.success and result.result:
            # Extract key insights from result
            insight_text = json.dumps(result.result)
            
            self.insights_collection.add(
                documents=[insight_text],
                metadatas=[insight],
                ids=[f"insight_{task.id}_{datetime.now().timestamp()}"]
            )
    
    async def get_relevant_context(self, query: str, n_results: int = 5) -> Dict[str, Any]:
        """Retrieves relevant context for a query."""
        context = {
            "documents": [],
            "insights": [],
            "recent_metrics": {}
        }
        
        # Search relevant documents
        doc_results = self.documents_collection.query(
            query_texts=[query],
            n_results=n_results
        )
        
        if doc_results['documents']:
            context['documents'] = [
                {
                    "content": doc,
                    "metadata": meta
                }
                for doc, meta in zip(doc_results['documents'][0], 
                                   doc_results['metadatas'][0])
            ]
        
        # Search relevant insights
        insight_results = self.insights_collection.query(
            query_texts=[query],
            n_results=n_results
        )
        
        if insight_results['documents']:
            context['insights'] = insight_results['documents'][0]
        
        # Get recent metrics
        context['recent_metrics'] = await self.get_recent_metrics(days=30)
        
        return context
    
    async def get_historical_metrics(self, metrics: List[str], 
                                   time_period: str = 'all') -> Dict[str, List[Dict]]:
        """Retrieves historical data for specified metrics."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Determine time filter
        if time_period == 'all':
            time_filter = ""
        else:
            days = {
                'week': 7,
                'month': 30,
                'quarter': 90,
                'year': 365
            }.get(time_period, 30)
            
            cutoff_date = (datetime.now() - timedelta(days=days)).isoformat()
            time_filter = f"AND timestamp >= '{cutoff_date}'"
        
        historical_data = {}
        
        for metric in metrics:
            if metric == 'all':
                # Get all available metrics
                cursor.execute(f"""
                    SELECT DISTINCT metric_name FROM health_metrics
                    WHERE 1=1 {time_filter}
                """)
                all_metrics = [row[0] for row in cursor.fetchall()]
                
                for m in all_metrics:
                    historical_data[m] = self._get_metric_history(cursor, m, time_filter)
            else:
                historical_data[metric] = self._get_metric_history(cursor, metric, time_filter)
        
        conn.close()
        return historical_data
    
    def _get_metric_history(self, cursor, metric_name: str, time_filter: str) -> List[Dict]:
        """Gets history for a single metric."""
        cursor.execute(f"""
            SELECT value, unit, timestamp, source, metadata
            FROM health_metrics
            WHERE metric_name = ? {time_filter}
            ORDER BY timestamp
        """, (metric_name,))
        
        return [
            {
                "value": row[0],
                "unit": row[1],
                "timestamp": row[2],
                "source": row[3],
                "metadata": json.loads(row[4]) if row[4] else {}
            }
            for row in cursor.fetchall()
        ]
    
    async def get_recent_metrics(self, days: int = 30) -> Dict[str, Any]:
        """Gets the most recent value for each metric."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cutoff_date = (datetime.now() - timedelta(days=days)).isoformat()
        
        cursor.execute("""
            SELECT metric_name, value, unit, MAX(timestamp) as latest_timestamp
            FROM health_metrics
            WHERE timestamp >= ?
            GROUP BY metric_name
        """, (cutoff_date,))
        
        recent_metrics = {
            row[0]: {
                "value": row[1],
                "unit": row[2],
                "timestamp": row[3]
            }
            for row in cursor.fetchall()
        }
        
        conn.close()
        return recent_metrics
    
    async def get_health_summary(self) -> Dict[str, Any]:
        """Gets a comprehensive health summary."""
        summary = {
            "recent_metrics": await self.get_recent_metrics(),
            "active_medications": await self.get_active_medications(),
            "recent_documents": await self.get_recent_documents(5),
            "health_trends": await self.analyze_trends()
        }
        
        return summary
    
    async def get_active_medications(self) -> List[Dict[str, Any]]:
        """Gets list of active medications."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT name, dosage, frequency, start_date, prescriber, notes
            FROM medications
            WHERE active = 1
            ORDER BY name
        """)
        
        medications = [
            {
                "name": row[0],
                "dosage": row[1],
                "frequency": row[2],
                "start_date": row[3],
                "prescriber": row[4],
                "notes": row[5]
            }
            for row in cursor.fetchall()
        ]
        
        conn.close()
        return medications
    
    async def get_recent_documents(self, limit: int = 5) -> List[Dict[str, Any]]:
        """Gets recently analyzed documents."""
        # Get all documents sorted by timestamp
        all_docs = self.documents_collection.get()
        
        if not all_docs['ids']:
            return []
        
        # Sort by timestamp
        docs_with_meta = list(zip(all_docs['ids'], all_docs['metadatas']))
        sorted_docs = sorted(
            docs_with_meta,
            key=lambda x: x[1].get('timestamp', ''),
            reverse=True
        )[:limit]
        
        return [
            {
                "id": doc_id,
                "type": meta.get('document_type'),
                "timestamp": meta.get('timestamp'),
                "summary": meta.get('summary', 'No summary available')
            }
            for doc_id, meta in sorted_docs
        ]
    
    async def analyze_trends(self) -> Dict[str, str]:
        """Analyzes trends in health metrics."""
        trends = {}
        
        # Get historical data for common metrics
        common_metrics = ['blood_pressure', 'cholesterol', 'glucose', 'weight']
        historical = await self.get_historical_metrics(common_metrics, 'quarter')
        
        for metric, history in historical.items():
            if len(history) >= 2:
                # Simple trend analysis
                recent_values = [float(h['value'].split('/')[0]) for h in history[-5:] 
                               if h['value'].replace('.', '').replace('/', '').isdigit()]
                
                if recent_values:
                    if recent_values[-1] > recent_values[0]:
                        trends[metric] = "increasing"
                    elif recent_values[-1] < recent_values[0]:
                        trends[metric] = "decreasing"
                    else:
                        trends[metric] = "stable"
        
        return trends
    
    async def get_metrics_for_visualization(self, data_type: str, 
                                          time_range: str) -> Dict[str, Any]:
        """Gets metrics formatted for visualization."""
        if data_type == 'all':
            metrics = ['all']
        else:
            metrics = [data_type]
            
        historical_data = await self.get_historical_metrics(metrics, time_range)
        
        # Format for visualization
        viz_data = {}
        for metric, history in historical_data.items():
            viz_data[metric] = {
                "timestamps": [h['timestamp'] for h in history],
                "values": [h['value'] for h in history],
                "units": history[0]['unit'] if history else ''
            }
            
        return viz_data
    
    async def store_user_preference(self, key: str, value: Any):
        """Stores user preference."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT OR REPLACE INTO user_preferences (key, value, updated_at)
            VALUES (?, ?, CURRENT_TIMESTAMP)
        """, (key, json.dumps(value)))
        
        conn.commit()
        conn.close()
    
    async def get_user_preference(self, key: str, default: Any = None) -> Any:
        """Gets user preference."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT value FROM user_preferences WHERE key = ?", (key,))
        row = cursor.fetchone()
        
        conn.close()
        
        if row:
            return json.loads(row[0])
        return default