import matplotlib.pyplot as plt
import pandas as pd
from database import get_adherence_data, get_daily_adherence
from matplotlib import patheffects
import numpy as np

def create_pie_chart(days=7):
    """Create 3D pie chart with glowing effects and trending colors"""
    data = get_adherence_data(days)
    
    if not data:
        return None
    
    labels = [row[0] for row in data]
    sizes = [row[1] for row in data]
    
    # Trending gradient colors (Neon/Cyber theme)
    colors = {
        'Taken': '#00ff87',      # Neon Green
        'Missed': '#ff0080',     # Neon Pink/Red
        'Delayed': '#ffd700'     # Gold
    }
    
    chart_colors = [colors.get(label, '#4CAF50') for label in labels]
    
    # Create figure with dark background
    fig, ax = plt.subplots(figsize=(10, 8), facecolor='#1a1a2e')
    ax.set_facecolor('#1a1a2e')
    
    # Create 3D pie chart with explosion effect
    explode = [0.1 if label == 'Missed' else 0.05 for label in labels]
    
    wedges, texts, autotexts = ax.pie(
        sizes, 
        labels=labels, 
        autopct='%1.1f%%',
        colors=chart_colors,
        explode=explode,
        startangle=90,
        shadow=True,
        textprops={'fontsize': 14, 'weight': 'bold', 'color': 'white'}
    )
    
    # Add glowing effect to wedges
    for i, wedge in enumerate(wedges):
        wedge.set_edgecolor('white')
        wedge.set_linewidth(2)
        # Add glow effect
        wedge.set_path_effects([
            patheffects.withStroke(linewidth=8, foreground=chart_colors[i], alpha=0.3),
            patheffects.Normal()
        ])
    
    # Style the percentage text with glow
    for autotext in autotexts:
        autotext.set_color('white')
        autotext.set_fontsize(16)
        autotext.set_weight('bold')
        autotext.set_path_effects([
            patheffects.withStroke(linewidth=3, foreground='black', alpha=0.8)
        ])
    
    # Style labels with glow
    for text in texts:
        text.set_color('white')
        text.set_fontsize(16)
        text.set_weight('bold')
        text.set_path_effects([
            patheffects.withStroke(linewidth=3, foreground='black', alpha=0.8)
        ])
    
    # Add title with glow effect
    title = ax.set_title(
        f'Medication Adherence (Last {days} Days)', 
        fontsize=20, 
        weight='bold', 
        color='#00ff87',
        pad=20
    )
    title.set_path_effects([
        patheffects.withStroke(linewidth=4, foreground='#00ff87', alpha=0.5)
    ])
    
    plt.tight_layout()
    return fig

def create_bar_chart(days=7):
    """Create 3D-style bar chart with gradient and glowing effects"""
    data = get_daily_adherence(days)
    
    if not data:
        return None
    
    df = pd.DataFrame(data, columns=['Date', 'Status', 'Count'])
    pivot_df = df.pivot(index='Date', columns='Status', values='Count').fillna(0)
    
    # Trending gradient colors
    colors_dict = {
        'Taken': '#00ff87',      # Neon Green
        'Missed': '#ff0080',     # Neon Pink
        'Delayed': '#ffd700'     # Gold
    }
    
    # Create figure with dark background
    fig, ax = plt.subplots(figsize=(12, 7), facecolor='#1a1a2e')
    ax.set_facecolor('#1a1a2e')
    
    # Get the columns in the order we want
    column_order = ['Taken', 'Missed', 'Delayed']
    existing_columns = [col for col in column_order if col in pivot_df.columns]
    
    # Create bar positions
    x = np.arange(len(pivot_df.index))
    width = 0.6
    
    # Plot stacked bars with gradient effect
    bottom = np.zeros(len(pivot_df.index))
    
    for col in existing_columns:
        color = colors_dict[col]
        bars = ax.bar(
            x, 
            pivot_df[col], 
            width,
            label=col,
            bottom=bottom,
            color=color,
            edgecolor='white',
            linewidth=2,
            alpha=0.9
        )
        
        # Add 3D shadow effect
        for bar in bars:
            height = bar.get_height()
            if height > 0:
                # Create shadow/depth effect
                shadow = plt.Rectangle(
                    (bar.get_x() + 0.02, bar.get_y() + 0.02),
                    bar.get_width(),
                    height,
                    facecolor='black',
                    alpha=0.3,
                    zorder=bar.get_zorder() - 1
                )
                ax.add_patch(shadow)
                
                # Add glow effect
                bar.set_path_effects([
                    patheffects.withStroke(linewidth=5, foreground=color, alpha=0.4)
                ])
        
        bottom += pivot_df[col]
    
    # Customize axes
    ax.set_xlabel('Date', fontsize=14, weight='bold', color='white')
    ax.set_ylabel('Number of Doses', fontsize=14, weight='bold', color='white')
    ax.set_title(
        f'Daily Medication Adherence (Last {days} Days)', 
        fontsize=18, 
        weight='bold', 
        color='#00ff87',
        pad=20
    )
    
    # Style x-axis
    ax.set_xticks(x)
    ax.set_xticklabels(pivot_df.index, rotation=45, ha='right', color='white', fontsize=11)
    
    # Style y-axis
    ax.tick_params(axis='y', colors='white', labelsize=11)
    
    # Add grid with glow
    ax.grid(True, alpha=0.2, color='#00ff87', linestyle='--', linewidth=1)
    ax.set_axisbelow(True)
    
    # Style spines
    for spine in ax.spines.values():
        spine.set_edgecolor('#00ff87')
        spine.set_linewidth(2)
    
    # Create custom legend with glow
    legend = ax.legend(
        title='Status',
        loc='upper left',
        framealpha=0.9,
        facecolor='#2a2a3e',
        edgecolor='#00ff87',
        fontsize=12,
        title_fontsize=13
    )
    legend.get_frame().set_linewidth(2)
    
    # Style legend text
    for text in legend.get_texts():
        text.set_color('white')
        text.set_weight('bold')
    
    legend.get_title().set_color('#00ff87')
    legend.get_title().set_weight('bold')
    
    plt.tight_layout()
    return fig

def calculate_adherence_score():
    """Calculate overall adherence percentage"""
    data = get_adherence_data(30)
    
    if not data:
        return 0
    
    total_taken = sum([row[1] for row in data if row[0] == 'Taken'])
    total_doses = sum([row[1] for row in data])
    
    if total_doses == 0:
        return 0
    
    return round((total_taken / total_doses) * 100, 1)
