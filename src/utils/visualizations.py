import logging
from typing import Dict, Any, List, Optional, Union
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.backends.backend_pdf import PdfPages
import seaborn as sns
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from pathlib import Path
import io
import base64

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class HealthVisualizer:
    """
    Creates visualizations for health data including trends, comparisons, and reports.
    """
    
    def __init__(self):
        # Set style
        sns.set_style("whitegrid")
        plt.rcParams['figure.figsize'] = (10, 6)
        plt.rcParams['font.size'] = 10
        
        # Color palette for health metrics
        self.colors = {
            'normal': '#2ecc71',      # Green
            'warning': '#f39c12',     # Orange
            'critical': '#e74c3c',    # Red
            'primary': '#3498db',     # Blue
            'secondary': '#9b59b6',   # Purple
            'neutral': '#95a5a6'      # Gray
        }
    
    def create_trend_charts(self, historical_data: Dict[str, List[Dict]]) -> Dict[str, str]:
        """
        Creates trend charts for health metrics.
        
        Args:
            historical_data: Dictionary with metric names and their historical values
            
        Returns:
            Dictionary with metric names and base64 encoded chart images
        """
        charts = {}
        
        for metric_name, history in historical_data.items():
            if not history:
                continue
            
            try:
                chart_data = self._create_single_trend_chart(metric_name, history)
                charts[metric_name] = chart_data
            except Exception as e:
                logger.error(f"Error creating chart for {metric_name}: {str(e)}")
        
        return charts
    
    def _create_single_trend_chart(self, metric_name: str, history: List[Dict]) -> str:
        """Creates a single trend chart for a metric."""
        fig, ax = plt.subplots(figsize=(10, 6))
        
        # Prepare data
        timestamps = []
        values = []
        
        for record in history:
            try:
                # Parse timestamp
                ts = datetime.fromisoformat(record['timestamp'].replace('Z', '+00:00'))
                timestamps.append(ts)
                
                # Parse value (handle blood pressure specially)
                if '/' in str(record['value']):
                    # Blood pressure - plot both systolic and diastolic
                    systolic, diastolic = map(float, record['value'].split('/'))
                    values.append(systolic)  # We'll handle this specially
                else:
                    values.append(float(record['value']))
            except:
                continue
        
        if not timestamps:
            plt.close()
            return ""
        
        # Sort by timestamp
        sorted_data = sorted(zip(timestamps, values))
        timestamps, values = zip(*sorted_data)
        
        # Plot based on metric type
        if metric_name.lower() == 'blood_pressure':
            # Special handling for blood pressure
            self._plot_blood_pressure(ax, history)
        else:
            # Regular line plot
            ax.plot(timestamps, values, 'o-', color=self.colors['primary'], 
                   linewidth=2, markersize=8)
            
            # Add reference ranges if available
            self._add_reference_ranges(ax, metric_name, values)
        
        # Formatting
        ax.set_title(f'{metric_name} Trend', fontsize=16, fontweight='bold')
        ax.set_xlabel('Date', fontsize=12)
        ax.set_ylabel(f'{metric_name} ({history[0].get("unit", "")})', fontsize=12)
        
        # Format x-axis dates
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
        plt.xticks(rotation=45)
        
        # Add grid
        ax.grid(True, alpha=0.3)
        
        # Tight layout
        plt.tight_layout()
        
        # Convert to base64
        return self._fig_to_base64(fig)
    
    def _plot_blood_pressure(self, ax, history: List[Dict]):
        """Special plotting for blood pressure (systolic/diastolic)."""
        timestamps = []
        systolic_values = []
        diastolic_values = []
        
        for record in history:
            try:
                ts = datetime.fromisoformat(record['timestamp'].replace('Z', '+00:00'))
                systolic, diastolic = map(float, record['value'].split('/'))
                timestamps.append(ts)
                systolic_values.append(systolic)
                diastolic_values.append(diastolic)
            except:
                continue
        
        # Plot both lines
        ax.plot(timestamps, systolic_values, 'o-', color=self.colors['critical'], 
               linewidth=2, markersize=8, label='Systolic')
        ax.plot(timestamps, diastolic_values, 'o-', color=self.colors['primary'], 
               linewidth=2, markersize=8, label='Diastolic')
        
        # Add normal ranges
        ax.axhspan(90, 120, alpha=0.2, color=self.colors['normal'], label='Normal Systolic')
        ax.axhspan(60, 80, alpha=0.1, color=self.colors['normal'], label='Normal Diastolic')
        
        ax.legend()
    
    def _add_reference_ranges(self, ax, metric_name: str, values: List[float]):
        """Adds reference ranges to the plot."""
        reference_ranges = {
            'glucose': (70, 100),
            'cholesterol': (0, 200),
            'ldl': (0, 100),
            'hdl': (40, float('inf')),
            'triglycerides': (0, 150),
            'hemoglobin': (12, 17.5)
        }
        
        metric_lower = metric_name.lower()
        if metric_lower in reference_ranges:
            low, high = reference_ranges[metric_lower]
            
            # Add horizontal lines for reference
            if low > 0:
                ax.axhline(y=low, color=self.colors['warning'], linestyle='--', 
                          alpha=0.7, label='Lower limit')
            if high < float('inf'):
                ax.axhline(y=high, color=self.colors['warning'], linestyle='--', 
                          alpha=0.7, label='Upper limit')
            
            # Shade normal range
            y_min, y_max = ax.get_ylim()
            if high < float('inf'):
                ax.axhspan(low, high, alpha=0.2, color=self.colors['normal'], 
                          label='Normal range')
            
            ax.legend()
    
    def create_health_dashboard(self, data: Dict[str, Any]) -> Dict[str, str]:
        """
        Creates a comprehensive health dashboard with multiple visualizations.
        
        Args:
            data: Health data including metrics, trends, etc.
            
        Returns:
            Dictionary with visualization names and base64 encoded images
        """
        dashboard = {}
        
        # 1. Current metrics overview
        if 'current_metrics' in data:
            dashboard['metrics_overview'] = self._create_metrics_overview(
                data['current_metrics']
            )
        
        # 2. Health score gauge
        if 'health_scores' in data:
            dashboard['health_scores'] = self._create_health_score_gauge(
                data['health_scores']
            )
        
        # 3. Medication timeline
        if 'medications' in data:
            dashboard['medication_timeline'] = self._create_medication_timeline(
                data['medications']
            )
        
        # 4. Comparative analysis
        if 'historical_comparison' in data:
            dashboard['comparison'] = self._create_comparison_chart(
                data['historical_comparison']
            )
        
        return dashboard
    
    def _create_metrics_overview(self, metrics: Dict[str, Any]) -> str:
        """Creates an overview of current health metrics."""
        fig, axes = plt.subplots(2, 3, figsize=(15, 10))
        axes = axes.flatten()
        
        metric_items = list(metrics.items())[:6]  # Show up to 6 metrics
        
        for idx, (metric_name, metric_data) in enumerate(metric_items):
            ax = axes[idx]
            
            value = metric_data.get('value', 'N/A')
            unit = metric_data.get('unit', '')
            status = metric_data.get('status', 'unknown')
            
            # Choose color based on status
            color = self.colors.get(status, self.colors['neutral'])
            
            # Create a simple metric display
            ax.text(0.5, 0.7, str(value), fontsize=36, fontweight='bold',
                   ha='center', va='center', color=color)
            ax.text(0.5, 0.4, unit, fontsize=16, ha='center', va='center')
            ax.text(0.5, 0.1, metric_name, fontsize=14, ha='center', va='center')
            
            # Remove axes
            ax.set_xlim(0, 1)
            ax.set_ylim(0, 1)
            ax.axis('off')
        
        # Hide unused subplots
        for idx in range(len(metric_items), 6):
            axes[idx].axis('off')
        
        plt.suptitle('Current Health Metrics', fontsize=18, fontweight='bold')
        plt.tight_layout()
        
        return self._fig_to_base64(fig)
    
    def _create_health_score_gauge(self, scores: Dict[str, float]) -> str:
        """Creates gauge charts for health scores."""
        num_scores = len(scores)
        fig, axes = plt.subplots(1, num_scores, figsize=(5*num_scores, 5))
        
        if num_scores == 1:
            axes = [axes]
        
        for idx, (aspect, score) in enumerate(scores.items()):
            ax = axes[idx]
            
            # Create gauge
            self._draw_gauge(ax, score, aspect)
        
        plt.tight_layout()
        return self._fig_to_base64(fig)
    
    def _draw_gauge(self, ax, score: float, label: str):
        """Draws a single gauge chart."""
        # Create wedges for the gauge
        theta1, theta2 = 180, 0  # Semi-circle
        radius = 1
        
        # Color based on score
        if score >= 80:
            color = self.colors['normal']
        elif score >= 60:
            color = self.colors['warning']
        else:
            color = self.colors['critical']
        
        # Draw the gauge background
        wedge_bg = plt.matplotlib.patches.Wedge(
            center=(0, 0), r=radius, theta1=theta1, theta2=theta2,
            facecolor='lightgray', edgecolor='gray'
        )
        ax.add_patch(wedge_bg)
        
        # Draw the score wedge
        score_angle = 180 - (score / 100 * 180)
        wedge_score = plt.matplotlib.patches.Wedge(
            center=(0, 0), r=radius*0.9, theta1=180, theta2=score_angle,
            facecolor=color, edgecolor='none'
        )
        ax.add_patch(wedge_score)
        
        # Add score text
        ax.text(0, -0.2, f'{score:.0f}', fontsize=36, fontweight='bold',
               ha='center', va='center')
        ax.text(0, -0.5, label, fontsize=14, ha='center', va='center')
        
        # Set limits and remove axes
        ax.set_xlim(-1.2, 1.2)
        ax.set_ylim(-0.7, 1.2)
        ax.axis('off')
    
    def _create_medication_timeline(self, medications: List[Dict[str, Any]]) -> str:
        """Creates a timeline visualization for medications."""
        fig, ax = plt.subplots(figsize=(12, 6))
        
        # Sort medications by start date
        sorted_meds = sorted(medications, key=lambda x: x.get('start_date', ''))
        
        y_positions = range(len(sorted_meds))
        
        for idx, med in enumerate(sorted_meds):
            start_date = datetime.fromisoformat(med.get('start_date', datetime.now().isoformat()))
            end_date = med.get('end_date')
            
            if end_date:
                end_date = datetime.fromisoformat(end_date)
            else:
                end_date = datetime.now()  # Ongoing medication
            
            # Draw timeline bar
            duration = (end_date - start_date).days
            ax.barh(idx, duration, left=start_date, height=0.6,
                   color=self.colors['primary'], alpha=0.7)
            
            # Add medication name
            ax.text(start_date - timedelta(days=5), idx, med['name'],
                   ha='right', va='center', fontsize=10)
        
        # Formatting
        ax.set_yticks([])
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
        ax.set_xlabel('Timeline', fontsize=12)
        ax.set_title('Medication Timeline', fontsize=16, fontweight='bold')
        
        plt.tight_layout()
        return self._fig_to_base64(fig)
    
    def _create_comparison_chart(self, comparison_data: Dict[str, Any]) -> str:
        """Creates a comparison chart for different time periods."""
        fig, ax = plt.subplots(figsize=(10, 6))
        
        metrics = list(comparison_data.keys())
        periods = ['Previous', 'Current']
        
        x = np.arange(len(metrics))
        width = 0.35
        
        previous_values = [comparison_data[m].get('previous', 0) for m in metrics]
        current_values = [comparison_data[m].get('current', 0) for m in metrics]
        
        # Create bars
        bars1 = ax.bar(x - width/2, previous_values, width, label='Previous',
                       color=self.colors['secondary'])
        bars2 = ax.bar(x + width/2, current_values, width, label='Current',
                       color=self.colors['primary'])
        
        # Add value labels
        for bars in [bars1, bars2]:
            for bar in bars:
                height = bar.get_height()
                ax.text(bar.get_x() + bar.get_width()/2., height,
                       f'{height:.1f}', ha='center', va='bottom')
        
        # Formatting
        ax.set_xlabel('Metrics', fontsize=12)
        ax.set_ylabel('Values', fontsize=12)
        ax.set_title('Health Metrics Comparison', fontsize=16, fontweight='bold')
        ax.set_xticks(x)
        ax.set_xticklabels(metrics, rotation=45, ha='right')
        ax.legend()
        
        plt.tight_layout()
        return self._fig_to_base64(fig)
    
    async def generate_report_pdf(self, report_content: str, 
                                health_summary: Dict[str, Any]) -> str:
        """
        Generates a PDF report with text and visualizations.
        
        Args:
            report_content: Text content of the report
            health_summary: Health data for visualizations
            
        Returns:
            Path to generated PDF file
        """
        pdf_path = Path("reports") / f"health_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        pdf_path.parent.mkdir(exist_ok=True)
        
        with PdfPages(pdf_path) as pdf:
            # Page 1: Title and summary
            fig = plt.figure(figsize=(8.5, 11))
            fig.text(0.5, 0.9, 'Health Insights Report', fontsize=24, 
                    fontweight='bold', ha='center')
            fig.text(0.5, 0.85, f'Generated on {datetime.now().strftime("%B %d, %Y")}',
                    fontsize=12, ha='center')
            
            # Add report content (wrapped)
            wrapped_text = self._wrap_text(report_content, 80)
            fig.text(0.1, 0.1, wrapped_text, fontsize=10, va='bottom',
                    wrap=True, family='monospace')
            
            pdf.savefig(fig, bbox_inches='tight')
            plt.close()
            
            # Additional pages with visualizations
            if 'recent_metrics' in health_summary:
                # Create and add metrics visualization
                metrics_fig = self._create_metrics_overview_for_pdf(
                    health_summary['recent_metrics']
                )
                pdf.savefig(metrics_fig, bbox_inches='tight')
                plt.close()
        
        return str(pdf_path)
    
    def _create_metrics_overview_for_pdf(self, metrics: Dict[str, Any]):
        """Creates a metrics overview specifically for PDF generation."""
        fig, ax = plt.subplots(figsize=(8.5, 11))
        
        # Create a table of metrics
        metric_data = []
        for name, data in metrics.items():
            metric_data.append([
                name,
                str(data.get('value', 'N/A')),
                data.get('unit', ''),
                data.get('timestamp', '')[:10]  # Date only
            ])
        
        # Create table
        table = ax.table(cellText=metric_data,
                        colLabels=['Metric', 'Value', 'Unit', 'Date'],
                        cellLoc='center',
                        loc='center')
        
        table.auto_set_font_size(False)
        table.set_fontsize(10)
        table.scale(1, 2)
        
        ax.axis('off')
        ax.set_title('Current Health Metrics', fontsize=16, fontweight='bold', pad=20)
        
        return fig
    
    def _fig_to_base64(self, fig) -> str:
        """Converts a matplotlib figure to base64 string."""
        buf = io.BytesIO()
        fig.savefig(buf, format='png', dpi=150, bbox_inches='tight')
        buf.seek(0)
        img_base64 = base64.b64encode(buf.read()).decode('utf-8')
        plt.close(fig)
        return img_base64
    
    def _wrap_text(self, text: str, width: int) -> str:
        """Wraps text to specified width."""
        import textwrap
        return '\n'.join(textwrap.wrap(text, width))