import streamlit as st
from typing import Dict, Any, List, Optional
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta


class HIAComponents:
    """Reusable UI components for HIA application."""
    
    @staticmethod
    def metric_gauge(value: float, min_val: float, max_val: float, 
                    title: str, unit: str = "") -> go.Figure:
        """
        Creates a gauge chart for displaying metrics.
        
        Args:
            value: Current value
            min_val: Minimum value
            max_val: Maximum value
            title: Chart title
            unit: Unit of measurement
            
        Returns:
            Plotly figure object
        """
        # Determine color based on value
        if value < min_val or value > max_val:
            color = "red"
        elif abs(value - min_val) < (max_val - min_val) * 0.1 or \
             abs(value - max_val) < (max_val - min_val) * 0.1:
            color = "orange"
        else:
            color = "green"
        
        fig = go.Figure(go.Indicator(
            mode="gauge+number",
            value=value,
            domain={'x': [0, 1], 'y': [0, 1]},
            title={'text': title},
            number={'suffix': f" {unit}"},
            gauge={
                'axis': {'range': [min_val, max_val]},
                'bar': {'color': color},
                'steps': [
                    {'range': [min_val, min_val + (max_val - min_val) * 0.3], 'color': "lightgray"},
                    {'range': [min_val + (max_val - min_val) * 0.3, 
                             min_val + (max_val - min_val) * 0.7], 'color': "gray"},
                    {'range': [min_val + (max_val - min_val) * 0.7, max_val], 'color': "lightgray"}
                ],
                'threshold': {
                    'line': {'color': "red", 'width': 4},
                    'thickness': 0.75,
                    'value': max_val * 0.9
                }
            }
        ))
        
        fig.update_layout(height=250, margin=dict(l=20, r=20, t=40, b=20))
        return fig
    
    @staticmethod
    def trend_line_chart(data: pd.DataFrame, x_col: str, y_col: str, 
                        title: str, reference_lines: Optional[Dict[str, float]] = None) -> go.Figure:
        """
        Creates a trend line chart with optional reference lines.
        
        Args:
            data: DataFrame with trend data
            x_col: Column name for x-axis
            y_col: Column name for y-axis
            title: Chart title
            reference_lines: Dict of reference line names and values
            
        Returns:
            Plotly figure object
        """
        fig = px.line(data, x=x_col, y=y_col, title=title,
                     markers=True, line_shape='linear')
        
        # Add reference lines
        if reference_lines:
            for name, value in reference_lines.items():
                fig.add_hline(y=value, line_dash="dash", 
                            annotation_text=name,
                            annotation_position="right")
        
        fig.update_layout(
            xaxis_title=x_col,
            yaxis_title=y_col,
            hovermode='x unified',
            height=400
        )
        
        return fig
    
    @staticmethod
    def medication_timeline(medications: List[Dict[str, Any]]) -> go.Figure:
        """
        Creates a timeline visualization for medications.
        
        Args:
            medications: List of medication dictionaries
            
        Returns:
            Plotly figure object
        """
        fig = go.Figure()
        
        for i, med in enumerate(medications):
            start_date = pd.to_datetime(med['start_date'])
            end_date = pd.to_datetime(med.get('end_date', datetime.now()))
            
            # Add trace for each medication
            fig.add_trace(go.Scatter(
                x=[start_date, end_date],
                y=[i, i],
                mode='lines+markers',
                name=med['name'],
                line=dict(width=10),
                marker=dict(size=12),
                hovertemplate=f"{med['name']}<br>Dosage: {med.get('dosage', 'N/A')}<br>%{{x}}"
            ))
        
        fig.update_layout(
            title="Medication Timeline",
            xaxis_title="Date",
            yaxis_title="Medications",
            yaxis=dict(
                tickmode='array',
                tickvals=list(range(len(medications))),
                ticktext=[med['name'] for med in medications]
            ),
            height=300 + len(medications) * 50,
            showlegend=False
        )
        
        return fig
    
    @staticmethod
    def health_score_card(score: int, category: str, 
                         description: str = "") -> None:
        """
        Displays a health score card component.
        
        Args:
            score: Score value (0-100)
            category: Category name
            description: Optional description
        """
        # Determine color and emoji based on score
        if score >= 80:
            color = "#2ecc71"
            emoji = "✅"
            status = "Excellent"
        elif score >= 60:
            color = "#f39c12"
            emoji = "⚠️"
            status = "Good"
        else:
            color = "#e74c3c"
            emoji = "❗"
            status = "Needs Attention"
        
        # Create card HTML
        card_html = f"""
        <div style="
            background-color: {color}20;
            border-left: 4px solid {color};
            padding: 1rem;
            border-radius: 0.5rem;
            margin-bottom: 1rem;
        ">
            <h4 style="margin: 0; color: {color};">
                {emoji} {category}
            </h4>
            <p style="font-size: 2rem; font-weight: bold; margin: 0.5rem 0; color: {color};">
                {score}/100
            </p>
            <p style="margin: 0; color: #666;">
                Status: {status}
            </p>
            {f'<p style="margin: 0.5rem 0 0 0; font-size: 0.9rem;">{description}</p>' if description else ''}
        </div>
        """
        
        st.markdown(card_html, unsafe_allow_html=True)
    
    @staticmethod
    def lab_results_table(results: List[Dict[str, Any]]) -> None:
        """
        Displays lab results in a formatted table.
        
        Args:
            results: List of lab result dictionaries
        """
        if not results:
            st.info("No lab results available")
            return
        
        # Convert to DataFrame for better display
        df = pd.DataFrame(results)
        
        # Add status column with color coding
        def get_status_color(row):
            if row.get('is_normal', True):
                return 'background-color: #d4edda'  # Light green
            else:
                return 'background-color: #f8d7da'  # Light red
        
        # Style the dataframe
        styled_df = df.style.apply(lambda x: [get_status_color(x)] * len(x), axis=1)
        
        st.dataframe(styled_df, use_container_width=True)
    
    @staticmethod
    def chat_message(role: str, content: str, timestamp: datetime) -> None:
        """
        Displays a chat message with appropriate styling.
        
        Args:
            role: 'user' or 'assistant'
            content: Message content
            timestamp: Message timestamp
        """
        if role == "user":
            st.markdown(f"""
            <div style="
                background-color: #e3f2fd;
                padding: 1rem;
                border-radius: 1rem;
                margin-bottom: 1rem;
                margin-left: 20%;
            ">
                <p style="margin: 0; font-weight: bold;">You</p>
                <p style="margin: 0.5rem 0;">{content}</p>
                <p style="margin: 0; font-size: 0.8rem; color: #666;">
                    {timestamp.strftime('%I:%M %p')}
                </p>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div style="
                background-color: #f5f5f5;
                padding: 1rem;
                border-radius: 1rem;
                margin-bottom: 1rem;
                margin-right: 20%;
            ">
                <p style="margin: 0; font-weight: bold;">HIA Assistant</p>
                <p style="margin: 0.5rem 0;">{content}</p>
                <p style="margin: 0; font-size: 0.8rem; color: #666;">
                    {timestamp.strftime('%I:%M %p')}
                </p>
            </div>
            """, unsafe_allow_html=True)
    
    @staticmethod
    def recommendation_card(recommendation: Dict[str, Any]) -> None:
        """
        Displays a recommendation card.
        
        Args:
            recommendation: Dictionary with recommendation details
        """
        priority_colors = {
            'high': '#e74c3c',
            'medium': '#f39c12',
            'low': '#3498db'
        }
        
        color = priority_colors.get(recommendation.get('priority', 'low'), '#3498db')
        
        with st.container():
            col1, col2 = st.columns([1, 10])
            
            with col1:
                st.markdown(f"<div style='font-size: 2rem;'>💡</div>", 
                          unsafe_allow_html=True)
            
            with col2:
                st.markdown(f"""
                <div style="
                    border-left: 3px solid {color};
                    padding-left: 1rem;
                ">
                    <h5 style="margin: 0; color: {color};">
                        {recommendation.get('type', 'Recommendation')}
                    </h5>
                    <p style="margin: 0.5rem 0;">
                        {recommendation.get('recommendation', '')}
                    </p>
                </div>
                """, unsafe_allow_html=True)
                
                if 'actions' in recommendation:
                    st.markdown("**Suggested Actions:**")
                    for action in recommendation['actions']:
                        st.markdown(f"- {action}")
    
    @staticmethod
    def progress_indicator(current: int, total: int, label: str) -> None:
        """
        Shows a progress indicator with label.
        
        Args:
            current: Current value
            total: Total value
            label: Progress label
        """
        progress = current / total if total > 0 else 0
        
        st.markdown(f"""
        <div style="margin-bottom: 1rem;">
            <div style="display: flex; justify-content: space-between; margin-bottom: 0.5rem;">
                <span>{label}</span>
                <span>{current}/{total}</span>
            </div>
            <div style="
                background-color: #e0e0e0;
                border-radius: 0.5rem;
                height: 10px;
                overflow: hidden;
            ">
                <div style="
                    background-color: #3498db;
                    height: 100%;
                    width: {progress * 100}%;
                    transition: width 0.3s ease;
                "></div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    @staticmethod
    def info_card(title: str, content: str, icon: str = "ℹ️", 
                 color: str = "#3498db") -> None:
        """
        Displays an information card.
        
        Args:
            title: Card title
            content: Card content
            icon: Icon to display
            color: Card accent color
        """
        st.markdown(f"""
        <div style="
            background-color: {color}10;
            border: 1px solid {color}30;
            border-radius: 0.5rem;
            padding: 1rem;
            margin-bottom: 1rem;
        ">
            <h4 style="margin: 0; color: {color};">
                {icon} {title}
            </h4>
            <p style="margin: 0.5rem 0 0 0;">
                {content}
            </p>
        </div>
        """, unsafe_allow_html=True)