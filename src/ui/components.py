import streamlit as st
from typing import Dict, Any, List, Optional
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta


class HIAComponents:
    """Reusable UI components for HIA application with modern styling."""
    
    # Define consistent color scheme
    COLORS = {
        'primary': '#2c5aa0',
        'primary_light': '#4a90e2',
        'secondary': '#00b894',
        'success': '#00b894',
        'warning': '#fd79a8',
        'danger': '#e17055',
        'info': '#74b9ff',
        'light': '#f8fafe',
        'text_primary': '#2d3436',
        'text_secondary': '#636e72'
    }
    
    @staticmethod
    def metric_gauge(value: float, min_val: float, max_val: float, 
                    title: str, unit: str = "") -> go.Figure:
        """
        Creates a modern gauge chart for displaying metrics with enhanced styling.
        
        Args:
            value: Current value
            min_val: Minimum value
            max_val: Maximum value
            title: Chart title
            unit: Unit of measurement
            
        Returns:
            Plotly figure object with modern styling
        """
        # Determine color based on value position in range
        range_size = max_val - min_val
        position = (value - min_val) / range_size
        
        if position < 0.3:
            color = HIAComponents.COLORS['danger']
        elif position < 0.7:
            color = HIAComponents.COLORS['warning']
        else:
            color = HIAComponents.COLORS['success']
        
        fig = go.Figure(go.Indicator(
            mode="gauge+number+delta",
            value=value,
            domain={'x': [0, 1], 'y': [0, 1]},
            title={'text': title, 'font': {'size': 18, 'family': 'Inter, sans-serif', 'color': HIAComponents.COLORS['text_primary']}},
            number={'suffix': f" {unit}", 'font': {'size': 24, 'family': 'Poppins, sans-serif'}},
            gauge={
                'axis': {
                    'range': [min_val, max_val],
                    'tickfont': {'size': 12, 'family': 'Inter, sans-serif'}
                },
                'bar': {'color': color, 'thickness': 0.8},
                'bgcolor': "rgba(248, 250, 254, 0.5)",
                'borderwidth': 2,
                'bordercolor': "rgba(44, 90, 160, 0.1)",
                'steps': [
                    {'range': [min_val, min_val + range_size * 0.3], 'color': "rgba(225, 112, 85, 0.2)"},
                    {'range': [min_val + range_size * 0.3, min_val + range_size * 0.7], 'color': "rgba(253, 121, 168, 0.2)"},
                    {'range': [min_val + range_size * 0.7, max_val], 'color': "rgba(0, 184, 148, 0.2)"}
                ],
                'threshold': {
                    'line': {'color': HIAComponents.COLORS['primary'], 'width': 3},
                    'thickness': 0.75,
                    'value': max_val * 0.85
                }
            }
        ))
        
        # Modern layout with improved spacing and fonts
        fig.update_layout(
            height=280,
            margin=dict(l=30, r=30, t=50, b=30),
            paper_bgcolor="rgba(255,255,255,0)",
            plot_bgcolor="rgba(255,255,255,0)",
            font_family="Inter, sans-serif"
        )
        return fig
    
    @staticmethod
    def trend_line_chart(data: pd.DataFrame, x_col: str, y_col: str, 
                        title: str, reference_lines: Optional[Dict[str, float]] = None) -> go.Figure:
        """
        Creates a modern trend line chart with enhanced styling and optional reference lines.
        
        Args:
            data: DataFrame with trend data
            x_col: Column name for x-axis
            y_col: Column name for y-axis
            title: Chart title
            reference_lines: Dict of reference line names and values
            
        Returns:
            Plotly figure object with modern styling
        """
        # Create line chart with modern styling
        fig = px.line(data, x=x_col, y=y_col, title=title,
                     markers=True, line_shape='spline')
        
        # Update line styling
        fig.update_traces(
            line=dict(color=HIAComponents.COLORS['primary'], width=3),
            marker=dict(size=8, color=HIAComponents.COLORS['primary_light'],
                       line=dict(width=2, color='white')),
            hovertemplate='<b>%{x}</b><br>%{y}<extra></extra>'
        )
        
        # Add reference lines with modern styling
        if reference_lines:
            for name, value in reference_lines.items():
                color = HIAComponents.COLORS['danger'] if 'high' in name.lower() else HIAComponents.COLORS['success']
                fig.add_hline(
                    y=value, 
                    line_dash="dash", 
                    line_color=color,
                    line_width=2,
                    annotation_text=name,
                    annotation_position="right",
                    annotation=dict(
                        font=dict(size=12, color=color, family='Inter, sans-serif'),
                        bgcolor="rgba(255,255,255,0.8)",
                        bordercolor=color,
                        borderwidth=1
                    )
                )
        
        # Modern layout
        fig.update_layout(
            title=dict(
                font=dict(size=18, family='Poppins, sans-serif', color=HIAComponents.COLORS['text_primary']),
                x=0.02
            ),
            xaxis_title=x_col,
            yaxis_title=y_col,
            hovermode='x unified',
            height=420,
            paper_bgcolor="rgba(255,255,255,0)",
            plot_bgcolor="rgba(248,250,254,0.3)",
            font_family="Inter, sans-serif",
            xaxis=dict(
                gridcolor="rgba(44, 90, 160, 0.1)",
                showgrid=True,
                zeroline=True,
                zerolinecolor="rgba(44, 90, 160, 0.2)"
            ),
            yaxis=dict(
                gridcolor="rgba(44, 90, 160, 0.1)",
                showgrid=True,
                zeroline=True,
                zerolinecolor="rgba(44, 90, 160, 0.2)"
            )
        )
        
        return fig
    
    @staticmethod
    def medication_timeline(medications: List[Dict[str, Any]]) -> go.Figure:
        """
        Creates a modern timeline visualization for medications.
        
        Args:
            medications: List of medication dictionaries
            
        Returns:
            Plotly figure object with modern styling
        """
        fig = go.Figure()
        
        colors = [HIAComponents.COLORS['primary'], HIAComponents.COLORS['secondary'], 
                 HIAComponents.COLORS['info'], HIAComponents.COLORS['warning']]
        
        for i, med in enumerate(medications):
            start_date = pd.to_datetime(med['start_date'])
            end_date = pd.to_datetime(med.get('end_date', datetime.now()))
            color = colors[i % len(colors)]
            
            # Add trace for each medication with modern styling
            fig.add_trace(go.Scatter(
                x=[start_date, end_date],
                y=[i, i],
                mode='lines+markers',
                name=med['name'],
                line=dict(width=12, color=color),
                marker=dict(size=15, color=color, symbol='circle',
                           line=dict(width=3, color='white')),
                hovertemplate=f"<b>{med['name']}</b><br>Dosage: {med.get('dosage', 'N/A')}<br>%{{x}}<extra></extra>"
            ))
        
        # Modern layout
        fig.update_layout(
            title=dict(
                text="Medication Timeline",
                font=dict(size=18, family='Poppins, sans-serif', color=HIAComponents.COLORS['text_primary']),
                x=0.02
            ),
            xaxis_title="Date",
            yaxis_title="Medications",
            yaxis=dict(
                tickmode='array',
                tickvals=list(range(len(medications))),
                ticktext=[med['name'] for med in medications],
                tickfont=dict(size=12, family='Inter, sans-serif')
            ),
            height=max(300, len(medications) * 60),
            showlegend=False,
            paper_bgcolor="rgba(255,255,255,0)",
            plot_bgcolor="rgba(248,250,254,0.3)",
            font_family="Inter, sans-serif",
            xaxis=dict(
                gridcolor="rgba(44, 90, 160, 0.1)",
                showgrid=True
            ),
            margin=dict(l=20, r=20, t=60, b=20)
        )
        
        return fig
    
    @staticmethod
    def health_score_card(score: int, category: str, 
                         description: str = "") -> None:
        """
        Displays a modern health score card component with enhanced styling.
        
        Args:
            score: Score value (0-100)
            category: Category name
            description: Optional description
        """
        # Determine color, emoji, and status based on score
        if score >= 85:
            color = HIAComponents.COLORS['success']
            bg_color = "rgba(0, 184, 148, 0.1)"
            emoji = "🌟"
            status = "Excellent"
            status_desc = "Keep up the great work!"
        elif score >= 70:
            color = HIAComponents.COLORS['info']
            bg_color = "rgba(116, 185, 255, 0.1)"
            emoji = "✅"
            status = "Good"
            status_desc = "You're doing well!"
        elif score >= 50:
            color = HIAComponents.COLORS['warning']
            bg_color = "rgba(253, 121, 168, 0.1)"
            emoji = "⚠️"
            status = "Fair"
            status_desc = "Room for improvement"
        else:
            color = HIAComponents.COLORS['danger']
            bg_color = "rgba(225, 112, 85, 0.1)"
            emoji = "🚨"
            status = "Needs Attention"
            status_desc = "Please consult your doctor"
        
        # Create modern card HTML
        card_html = f"""
        <div style="
            background: linear-gradient(145deg, #ffffff, {bg_color});
            border: 1px solid {color}30;
            border-left: 4px solid {color};
            border-radius: 16px;
            padding: 2rem;
            margin-bottom: 1.5rem;
            box-shadow: 0 4px 20px rgba(44, 90, 160, 0.12);
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
            position: relative;
            overflow: hidden;
        " onmouseover="this.style.transform='translateY(-4px)'; this.style.boxShadow='0 8px 30px rgba(44, 90, 160, 0.15)'"
           onmouseout="this.style.transform='translateY(0)'; this.style.boxShadow='0 4px 20px rgba(44, 90, 160, 0.12)'">
            
            <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 1.5rem;">
                <h3 style="margin: 0; color: {color}; font-family: 'Poppins', sans-serif; font-weight: 600; font-size: 1.2rem;">
                    {category}
                </h3>
                <span style="font-size: 2rem;">{emoji}</span>
            </div>
            
            <div style="text-align: center; margin-bottom: 1.5rem;">
                <div style="font-size: 3.5rem; font-weight: 700; color: {color}; 
                           font-family: 'Poppins', sans-serif; line-height: 1; margin-bottom: 0.5rem;">
                    {score}
                </div>
                <div style="font-size: 0.9rem; color: #636e72; font-family: 'Inter', sans-serif;">
                    out of 100
                </div>
            </div>
            
            <div style="text-align: center;">
                <div style="display: inline-block; background-color: {color}20; color: {color}; 
                           padding: 0.5rem 1rem; border-radius: 20px; font-size: 0.9rem; 
                           font-weight: 500; font-family: 'Inter', sans-serif; margin-bottom: 0.5rem;">
                    {status}
                </div>
                <div style="font-size: 0.8rem; color: #636e72; font-family: 'Inter', sans-serif;">
                    {status_desc}
                </div>
            </div>
            
            {f'<div style="margin-top: 1rem; padding-top: 1rem; border-top: 1px solid {color}20; font-size: 0.9rem; color: #636e72; font-family: \'Inter\', sans-serif;">{description}</div>' if description else ''}
        </div>
        """
        
        st.markdown(card_html, unsafe_allow_html=True)
    
    @staticmethod
    def lab_results_table(results: List[Dict[str, Any]]) -> None:
        """
        Displays lab results in a modern formatted table with enhanced styling.
        
        Args:
            results: List of lab result dictionaries
        """
        if not results:
            st.markdown("""
            <div style="
                background: linear-gradient(145deg, #ffffff, #f8fafe);
                border: 2px dashed #ddd;
                border-radius: 16px;
                padding: 3rem;
                text-align: center;
                color: #636e72;
                font-family: 'Inter', sans-serif;
            ">
                <div style="font-size: 3rem; margin-bottom: 1rem;">📋</div>
                <div style="font-size: 1.1rem; font-weight: 500; margin-bottom: 0.5rem;">No lab results available</div>
                <div style="font-size: 0.9rem;">Upload documents to see analysis results here</div>
            </div>
            """, unsafe_allow_html=True)
            return
        
        # Convert to DataFrame for better display
        df = pd.DataFrame(results)
        
        # Enhanced table styling function
        def style_table(styler):
            return styler.set_table_styles([
                {'selector': 'thead th', 'props': [
                    ('background-color', HIAComponents.COLORS['primary']),
                    ('color', 'white'),
                    ('font-family', 'Inter, sans-serif'),
                    ('font-weight', '600'),
                    ('padding', '12px'),
                    ('text-align', 'center')
                ]},
                {'selector': 'tbody td', 'props': [
                    ('padding', '12px'),
                    ('border-bottom', '1px solid #e0e0e0'),
                    ('font-family', 'Inter, sans-serif')
                ]},
                {'selector': 'tbody tr:hover', 'props': [
                    ('background-color', '#f8fafe')
                ]}
            ]).apply(lambda x: [
                'background-color: rgba(0, 184, 148, 0.1)' if row.get('is_normal', True) 
                else 'background-color: rgba(225, 112, 85, 0.1)' 
                for row in results
            ], axis=0)
        
        # Apply styling and display
        if len(df.columns) > 0:
            styled_df = df.style.pipe(style_table)
            st.dataframe(styled_df, use_container_width=True)
    
    @staticmethod
    def chat_message(role: str, content: str, timestamp: datetime) -> None:
        """
        Displays a modern chat message with enhanced styling and animations.
        
        Args:
            role: 'user' or 'assistant'
            content: Message content
            timestamp: Message timestamp
        """
        if role == "user":
            st.markdown(f"""
            <div class="chat-message chat-user" style="
                background: linear-gradient(135deg, {HIAComponents.COLORS['primary']}, {HIAComponents.COLORS['primary_light']});
                color: white;
                padding: 1.5rem;
                border-radius: 20px 20px 6px 20px;
                margin-bottom: 1rem;
                margin-left: 15%;
                box-shadow: 0 4px 20px rgba(44, 90, 160, 0.3);
                animation: slideInRight 0.3s ease-out;
                position: relative;
            ">
                <div style="display: flex; align-items: center; margin-bottom: 0.5rem;">
                    <div style="width: 8px; height: 8px; background-color: rgba(255,255,255,0.8); 
                               border-radius: 50%; margin-right: 0.5rem;"></div>
                    <span style="font-weight: 600; font-size: 0.9rem; opacity: 0.9;">You</span>
                </div>
                <div style="line-height: 1.6; margin-bottom: 0.5rem;">{content}</div>
                <div style="font-size: 0.75rem; opacity: 0.8; text-align: right;">
                    {timestamp.strftime('%I:%M %p')}
                </div>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div class="chat-message chat-assistant" style="
                background: linear-gradient(145deg, #ffffff, {HIAComponents.COLORS['light']});
                color: {HIAComponents.COLORS['text_primary']};
                padding: 1.5rem;
                border-radius: 20px 20px 20px 6px;
                margin-bottom: 1rem;
                margin-right: 15%;
                border: 1px solid rgba(44, 90, 160, 0.1);
                box-shadow: 0 4px 20px rgba(44, 90, 160, 0.12);
                animation: slideInLeft 0.3s ease-out;
                position: relative;
            ">
                <div style="display: flex; align-items: center; margin-bottom: 0.5rem;">
                    <div style="width: 24px; height: 24px; background: linear-gradient(135deg, {HIAComponents.COLORS['primary']}, {HIAComponents.COLORS['secondary']}); 
                               border-radius: 50%; margin-right: 0.75rem; display: flex; align-items: center; justify-content: center;">
                        <span style="color: white; font-size: 0.7rem;">🏥</span>
                    </div>
                    <span style="font-weight: 600; font-size: 0.9rem; color: {HIAComponents.COLORS['primary']};">HIA Assistant</span>
                </div>
                <div style="line-height: 1.6; margin-bottom: 0.5rem;">{content}</div>
                <div style="font-size: 0.75rem; color: {HIAComponents.COLORS['text_secondary']}; text-align: right;">
                    {timestamp.strftime('%I:%M %p')}
                </div>
            </div>
            
            <style>
                @keyframes slideInLeft {{
                    from {{ opacity: 0; transform: translateX(-20px); }}
                    to {{ opacity: 1; transform: translateX(0); }}
                }}
                @keyframes slideInRight {{
                    from {{ opacity: 0; transform: translateX(20px); }}
                    to {{ opacity: 1; transform: translateX(0); }}
                }}
            </style>
            """, unsafe_allow_html=True)
    
    @staticmethod
    def recommendation_card(recommendation: Dict[str, Any]) -> None:
        """
        Displays a modern recommendation card with enhanced styling.
        
        Args:
            recommendation: Dictionary with recommendation details
        """
        priority_config = {
            'high': {
                'color': HIAComponents.COLORS['danger'],
                'bg_color': 'rgba(225, 112, 85, 0.1)',
                'icon': '🚨',
                'label': 'High Priority'
            },
            'medium': {
                'color': HIAComponents.COLORS['warning'],
                'bg_color': 'rgba(253, 121, 168, 0.1)',
                'icon': '⚠️',
                'label': 'Medium Priority'
            },
            'low': {
                'color': HIAComponents.COLORS['info'],
                'bg_color': 'rgba(116, 185, 255, 0.1)',
                'icon': '💡',
                'label': 'Low Priority'
            }
        }
        
        priority = recommendation.get('priority', 'low')
        config = priority_config.get(priority, priority_config['low'])
        
        st.markdown(f"""
        <div style="
            background: linear-gradient(145deg, #ffffff, {config['bg_color']});
            border: 1px solid {config['color']}30;
            border-left: 4px solid {config['color']};
            border-radius: 16px;
            padding: 1.5rem;
            margin-bottom: 1.5rem;
            box-shadow: 0 4px 20px rgba(44, 90, 160, 0.12);
            transition: all 0.3s ease;
        " onmouseover="this.style.transform='translateY(-2px)'; this.style.boxShadow='0 8px 30px rgba(44, 90, 160, 0.15)'"
           onmouseout="this.style.transform='translateY(0)'; this.style.boxShadow='0 4px 20px rgba(44, 90, 160, 0.12)'">
            
            <div style="display: flex; align-items: flex-start; margin-bottom: 1rem;">
                <div style="font-size: 2rem; margin-right: 1rem;">{config['icon']}</div>
                <div style="flex: 1;">
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.5rem;">
                        <h4 style="margin: 0; color: {config['color']}; font-family: 'Poppins', sans-serif; 
                                  font-weight: 600; font-size: 1.1rem;">
                            {recommendation.get('type', 'Recommendation')}
                        </h4>
                        <span style="background-color: {config['color']}20; color: {config['color']}; 
                                    padding: 0.25rem 0.75rem; border-radius: 12px; font-size: 0.75rem; 
                                    font-weight: 500; font-family: 'Inter', sans-serif;">
                            {config['label']}
                        </span>
                    </div>
                    <p style="margin: 0; line-height: 1.6; color: {HIAComponents.COLORS['text_primary']}; 
                             font-family: 'Inter', sans-serif;">
                        {recommendation.get('recommendation', '')}
                    </p>
                </div>
            </div>
        """, unsafe_allow_html=True)
        
        # Add suggested actions if available
        if 'actions' in recommendation and recommendation['actions']:
            actions_html = '<div style="margin-top: 1rem; padding-top: 1rem; border-top: 1px solid rgba(44, 90, 160, 0.1);">'
            actions_html += f'<div style="font-weight: 600; margin-bottom: 0.75rem; color: {HIAComponents.COLORS["text_primary"]}; font-family: \'Inter\', sans-serif; font-size: 0.9rem;">Suggested Actions:</div>'
            actions_html += '<div style="display: flex; flex-direction: column; gap: 0.5rem;">'
            
            for i, action in enumerate(recommendation['actions']):
                actions_html += f'''
                <div style="display: flex; align-items: center; padding: 0.5rem; 
                           background-color: rgba(44, 90, 160, 0.05); border-radius: 8px;">
                    <div style="width: 20px; height: 20px; background-color: {config['color']}; 
                               border-radius: 50%; display: flex; align-items: center; justify-content: center; 
                               margin-right: 0.75rem; font-size: 0.7rem; color: white; font-weight: bold;">
                        {i + 1}
                    </div>
                    <span style="font-family: 'Inter', sans-serif; font-size: 0.9rem; 
                                color: {HIAComponents.COLORS['text_primary']};">{action}</span>
                </div>
                '''
            
            actions_html += '</div></div></div>'
            st.markdown(actions_html, unsafe_allow_html=True)
        else:
            st.markdown('</div>', unsafe_allow_html=True)
    
    @staticmethod
    def progress_indicator(current: int, total: int, label: str) -> None:
        """
        Shows a modern progress indicator with enhanced styling.
        
        Args:
            current: Current value
            total: Total value
            label: Progress label
        """
        progress = current / total if total > 0 else 0
        percentage = int(progress * 100)
        
        st.markdown(f"""
        <div style="
            background: linear-gradient(145deg, #ffffff, #f8fafe);
            border: 1px solid rgba(44, 90, 160, 0.1);
            border-radius: 12px;
            padding: 1.5rem;
            margin-bottom: 1rem;
            box-shadow: 0 2px 10px rgba(44, 90, 160, 0.08);
        ">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem;">
                <span style="font-family: 'Inter', sans-serif; font-weight: 500; 
                           color: {HIAComponents.COLORS['text_primary']}; font-size: 1rem;">{label}</span>
                <div style="display: flex; align-items: center; gap: 0.5rem;">
                    <span style="font-family: 'Poppins', sans-serif; font-weight: 600; 
                               color: {HIAComponents.COLORS['primary']}; font-size: 1.1rem;">{current}/{total}</span>
                    <span style="font-size: 0.9rem; color: {HIAComponents.COLORS['text_secondary']};
                               background-color: {HIAComponents.COLORS['primary']}20; 
                               padding: 0.25rem 0.5rem; border-radius: 8px;">
                        {percentage}%
                    </span>
                </div>
            </div>
            <div style="
                background-color: rgba(44, 90, 160, 0.1);
                border-radius: 10px;
                height: 12px;
                overflow: hidden;
                position: relative;
            ">
                <div style="
                    background: linear-gradient(90deg, {HIAComponents.COLORS['primary']}, {HIAComponents.COLORS['secondary']});
                    height: 100%;
                    width: {progress * 100}%;
                    border-radius: 10px;
                    transition: width 0.6s cubic-bezier(0.4, 0, 0.2, 1);
                    position: relative;
                    overflow: hidden;
                ">
                    <div style="
                        position: absolute;
                        top: 0;
                        left: 0;
                        right: 0;
                        bottom: 0;
                        background: linear-gradient(90deg, transparent, rgba(255,255,255,0.3), transparent);
                        animation: shimmer 2s infinite;
                    "></div>
                </div>
            </div>
        </div>
        
        <style>
            @keyframes shimmer {{
                0% {{ transform: translateX(-100%); }}
                100% {{ transform: translateX(100%); }}
            }}
        </style>
        """, unsafe_allow_html=True)
    
    @staticmethod
    def info_card(title: str, content: str, icon: str = "ℹ️", 
                 card_type: str = "info") -> None:
        """
        Displays a modern information card with enhanced styling.
        
        Args:
            title: Card title
            content: Card content
            icon: Icon to display
            card_type: Card type ('info', 'success', 'warning', 'error')
        """
        type_config = {
            'info': {
                'color': HIAComponents.COLORS['info'],
                'bg_color': 'rgba(116, 185, 255, 0.1)',
                'border_color': 'rgba(116, 185, 255, 0.3)'
            },
            'success': {
                'color': HIAComponents.COLORS['success'],
                'bg_color': 'rgba(0, 184, 148, 0.1)',
                'border_color': 'rgba(0, 184, 148, 0.3)'
            },
            'warning': {
                'color': HIAComponents.COLORS['warning'],
                'bg_color': 'rgba(253, 121, 168, 0.1)',
                'border_color': 'rgba(253, 121, 168, 0.3)'
            },
            'error': {
                'color': HIAComponents.COLORS['danger'],
                'bg_color': 'rgba(225, 112, 85, 0.1)',
                'border_color': 'rgba(225, 112, 85, 0.3)'
            }
        }
        
        config = type_config.get(card_type, type_config['info'])
        
        st.markdown(f"""
        <div style="
            background: linear-gradient(145deg, #ffffff, {config['bg_color']});
            border: 1px solid {config['border_color']};
            border-left: 4px solid {config['color']};
            border-radius: 12px;
            padding: 1.5rem;
            margin-bottom: 1.5rem;
            box-shadow: 0 2px 10px rgba(44, 90, 160, 0.08);
            transition: all 0.3s ease;
        " onmouseover="this.style.boxShadow='0 4px 20px rgba(44, 90, 160, 0.12)'"
           onmouseout="this.style.boxShadow='0 2px 10px rgba(44, 90, 160, 0.08)'">
            
            <div style="display: flex; align-items: flex-start; gap: 1rem;">
                <div style="font-size: 1.5rem; flex-shrink: 0;">{icon}</div>
                <div style="flex: 1;">
                    <h4 style="margin: 0 0 0.75rem 0; color: {config['color']}; 
                              font-family: 'Poppins', sans-serif; font-weight: 600; font-size: 1.1rem;">
                        {title}
                    </h4>
                    <p style="margin: 0; line-height: 1.6; color: {HIAComponents.COLORS['text_primary']}; 
                             font-family: 'Inter', sans-serif; font-size: 0.95rem;">
                        {content}
                    </p>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)