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
        
        # Try to initialize ChromaDB, but fall back to simple storage if it fails
        self.use_vector_db = False
        self.documents_collection = None
        self.insights_collection = None
        
        try:
            # Initialize ChromaDB for vector storage
            self.chroma_client = chromadb.PersistentClient(
                path=str(self.storage_path / "chroma")
            )
            
            # Use a simpler embedding function that doesn't require onnxruntime
            try:
                # Create collections without embedding function to avoid onnxruntime issues
                self.documents_collection = self.chroma_client.get_or_create_collection(
                    name="medical_documents"
                )
                
                self.insights_collection = self.chroma_client.get_or_create_collection(
                    name="health_insights"
                )
                self.use_vector_db = True
                logger.info("ChromaDB initialized successfully")
                
            except Exception as e:
                logger.warning(f"ChromaDB collection creation failed: {str(e)}")
                raise e
                
        except Exception as e:
            logger.warning(f"ChromaDB initialization failed: {str(e)}")
            logger.info("Falling back to simple in-memory storage")
            # Simple fallback storage
            self.documents_store = {}
            self.insights_store = []
        
        # Initialize SQLite for structured data (this should always work)
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
        if self.use_vector_db and self.documents_collection:
            try:
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
                logger.info(f"Stored document {document_id} of type {document_type} in ChromaDB")
            except Exception as e:
                logger.error(f"Failed to store document in ChromaDB: {str(e)}")
                # Fall back to simple storage
                self._store_document_simple(document_id, content, document_type, metadata)
        else:
            # Use simple storage
            self._store_document_simple(document_id, content, document_type, metadata)
    
    def _store_document_simple(self, document_id: str, content: str, 
                              document_type: str, metadata: Dict[str, Any]):
        """Simple document storage fallback."""
        if not hasattr(self, 'documents_store'):
            self.documents_store = {}
        
        self.documents_store[document_id] = {
            "content": content,
            "document_type": document_type,
            "timestamp": datetime.now().isoformat(),
            **metadata
        }
        logger.info(f"Stored document {document_id} of type {document_type} in simple storage")
    
    async def store_task_result(self, task: Any, result: Any):
        """Stores task execution results for future reference."""
        insight = {
            "task_type": task.type.value,
            "task_description": task.description,
            "timestamp": datetime.now().isoformat(),
            "success": result.success
        }
        
        if result.success and result.result:
            if self.use_vector_db and self.insights_collection:
                try:
                    # Extract key insights from result
                    insight_text = json.dumps(result.result)
                    
                    self.insights_collection.add(
                        documents=[insight_text],
                        metadatas=[insight],
                        ids=[f"insight_{task.id}_{datetime.now().timestamp()}"]
                    )
                    logger.info("Stored task result in ChromaDB")
                except Exception as e:
                    logger.error(f"Failed to store task result in ChromaDB: {str(e)}")
                    self._store_insight_simple(insight, result.result)
            else:
                # Use simple storage
                self._store_insight_simple(insight, result.result)
    
    def _store_insight_simple(self, insight: Dict[str, Any], result_data: Any):
        """Simple insight storage fallback."""
        if not hasattr(self, 'insights_store'):
            self.insights_store = []
        
        insight_record = {
            **insight,
            "result_data": result_data
        }
        self.insights_store.append(insight_record)
        logger.info("Stored task result in simple storage")
    
    async def get_relevant_context(self, query: str, n_results: int = 5) -> Dict[str, Any]:
        """Retrieves relevant context for a query."""
        context = {
            "documents": [],
            "insights": [],
            "recent_metrics": {}
        }
        
        if self.use_vector_db and self.documents_collection and self.insights_collection:
            try:
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
                    
            except Exception as e:
                logger.error(f"ChromaDB query failed: {str(e)}")
                # Fall back to simple search
                context = self._get_context_simple(query, n_results)
        else:
            # Use simple storage
            context = self._get_context_simple(query, n_results)
        
        # Get recent metrics (this always works)
        context['recent_metrics'] = await self.get_recent_metrics(days=30)
        
        return context
    
    def _get_context_simple(self, query: str, n_results: int = 5) -> Dict[str, Any]:
        """Simple context retrieval fallback."""
        context = {
            "documents": [],
            "insights": [],
            "recent_metrics": {}
        }
        
        # Simple keyword search in documents
        if hasattr(self, 'documents_store'):
            query_lower = query.lower()
            matching_docs = []
            
            for doc_id, doc_data in self.documents_store.items():
                if query_lower in doc_data['content'].lower():
                    matching_docs.append({
                        "content": doc_data['content'][:500] + "...",  # Truncate for brevity
                        "metadata": {k: v for k, v in doc_data.items() if k != 'content'}
                    })
                    if len(matching_docs) >= n_results:
                        break
            
            context['documents'] = matching_docs
        
        # Simple search in insights
        if hasattr(self, 'insights_store'):
            query_lower = query.lower()
            matching_insights = []
            
            for insight in self.insights_store[-n_results:]:  # Get recent insights
                if query_lower in str(insight.get('result_data', '')).lower():
                    matching_insights.append(str(insight.get('result_data', '')))
            
            context['insights'] = matching_insights
        
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