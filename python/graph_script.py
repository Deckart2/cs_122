# General Imports
import bokeh.io
import geopandas as gpd
import pandas as pd
import json
import numpy as np
import requests
from urllib.request import urlopen

# Bokeh Imports
from bokeh.models import (CDSView, ColorBar, ColumnDataSource,
                          CustomJS, CustomJSFilter,
                          GeoJSONDataSource, HoverTool,
                          LinearColorMapper, Slider, CategoricalColorMapper)
from bokeh.layouts import column, row, widgetbox
from bokeh.palettes import brewer
from bokeh.plotting import figure
from bokeh.palettes import Spectral6
from bokeh.transform import factor_cmap

# Uploading dataframes
districts = gpd.read_file('generated_data/districts1.shp')

# Converting dataframes to GEOJSON
geosource_districts = GeoJSONDataSource(geojson=districts.to_json())

# Creating a green palette for the geomaps
green_palette = brewer['BuGn'][8][::-1]

# Creating a blue palette for the geomaps
blue_palette = brewer['Blues'][8][::-1]

# Creating a red palette for the geomaps
red_palette = brewer['OrRd'][8][::-1]

# Creating a diverging palette for the geomaps
diverging_palette = brewer['RdBu'][8][::-1]

def tweet_count(title):
    """
    Creates the visualizations for the web application using the Bokeh framework

    Args:
        title ([string]): title of figure
    Returns:
        p (bokeh object): bokeh plot figure
    """
    # Instantiate LinearColorMapper that linearly maps numbers in a range,
    # into a sequence of colors.
    color_mapper = LinearColorMapper(palette=green_palette, low=0, high=1500)

    # Create color bar.
    color_bar = ColorBar(color_mapper=color_mapper,
                            label_standoff=8,
                            width=500, height=20,
                            border_line_color=None,
                            location=(0, 0),
                            orientation='horizontal')

    # Create figure object.
    p1 = figure(title=title,
                plot_height=600,
                plot_width=950,
                toolbar_location='below',
                tools="pan, wheel_zoom, box_zoom, reset")
    
    # Hiding Axis Labels
    p1.xaxis.major_tick_line_color = None  # turn off x-axis major ticks
    p1.xaxis.minor_tick_line_color = None  # turn off x-axis minor ticks
    p1.yaxis.major_tick_line_color = None  # turn off y-axis major ticks
    p1.yaxis.minor_tick_line_color = None  # turn off y-axis minor ticks
    p1.xaxis.major_label_text_font_size = '0pt'  # turn off x-axis tick labels
    p1.yaxis.major_label_text_font_size = '0pt'  # turn off y-axis tick labels
    
    # Add patch renderer to figure.
    states = p1.patches("xs", "ys", source=geosource_districts,
                        fill_color={'field': 'tweet_cnt_',
                                    'transform': color_mapper},
                        line_color='gray',
                        line_width=0.75,
                        fill_alpha=1)

    # Create hover tool
    p1.add_tools(HoverTool(renderers=[states],
                           tooltips=[('State', '@state_name'),
                                     ('Party', '@party'),
                                     ('Name of Representative', '@name'),
                                     ('Vote Summary', '@vote_summa'),
                                     ('Tweet Keywords', '@keywords_l')
                                     ]))
    # Specify layout
    p1.add_layout(color_bar, 'below')

    return p1

def user_count(title):
    """
    Creates the visualizations for the web application using the Bokeh framework

    Args:
        title ([string]): title of figure
    Returns:
        p (bokeh object): bokeh plot figure
    """
    # Instantiate LinearColorMapper that linearly maps numbers in a range,
    # into a sequence of colors.
    color_mapper = LinearColorMapper(palette=green_palette, low=0, high=300)

    # Create color bar.
    color_bar = ColorBar(color_mapper=color_mapper,
                            label_standoff=8,
                            width=500, height=20,
                            border_line_color=None,
                            location=(0, 0),
                            orientation='horizontal')

    # Create figure object.
    p2 = figure(title=title,
                plot_height=600,
                plot_width=950,
                toolbar_location='below',
                tools="pan, wheel_zoom, box_zoom, reset")
    
    # Hiding Axis Labels
    p2.xaxis.major_tick_line_color = None  # turn off x-axis major ticks
    p2.xaxis.minor_tick_line_color = None  # turn off x-axis minor ticks
    p2.yaxis.major_tick_line_color = None  # turn off y-axis major ticks
    p2.yaxis.minor_tick_line_color = None  # turn off y-axis minor ticks
    p2.xaxis.major_label_text_font_size = '0pt'  # turn off x-axis tick labels
    p2.yaxis.major_label_text_font_size = '0pt'  # turn off y-axis tick labels

    # Add patch renderer to figure.
    states = p2.patches("xs", "ys", source=geosource_districts,
                        fill_color={'field': 'users_cnt_',
                                    'transform': color_mapper},
                        line_color='gray',
                        line_width=0.75,
                        fill_alpha=1)

    # Create hover tool
    p2.add_tools(HoverTool(renderers=[states],
                           tooltips=[('State', '@state_name'),
                                     ('Party', '@party'),
                                     ('Name of Representative', '@name'),
                                     ('Vote Summary', '@vote_summa'),
                                     ('Tweet Keywords', '@keywords_l')
                                     ]))
    # Specify layout
    p2.add_layout(color_bar, 'below')

    return p2

def vote_summary(title):
    """
    Creates the visualizations for the web application using the Bokeh framework

    Args:
        title ([string]): title of figure
    Returns:
        p (bokeh object): bokeh plot figure
    """
    color_mapper = CategoricalColorMapper(
        palette=["#7cd274", "gray", "#f7a9a1"], 
        factors=['democractic', 'mixed', 'anti_democratic'])

    # Create figure object.
    p3 = figure(title=title,
                plot_height=600,
                plot_width=950,
                toolbar_location='below',
                tools="pan, wheel_zoom, box_zoom, reset")
    
    # Hiding Axis Labels
    p3.xaxis.major_tick_line_color = None  # turn off x-axis major ticks
    p3.xaxis.minor_tick_line_color = None  # turn off x-axis minor ticks
    p3.yaxis.major_tick_line_color = None  # turn off y-axis major ticks
    p3.yaxis.minor_tick_line_color = None  # turn off y-axis minor ticks
    p3.xaxis.major_label_text_font_size = '0pt'  # turn off x-axis tick labels
    p3.yaxis.major_label_text_font_size = '0pt'  # turn off y-axis tick labels

    # Add patch renderer to figure.
    states = p3.patches("xs", "ys", source=geosource_districts,
                        fill_color={'field': 'vote_summa',
                                    'transform': color_mapper},
                        line_color='gray',
                        line_width=0.75,
                        fill_alpha=1)

    # Create hover tool
    p3.add_tools(HoverTool(renderers=[states],
                           tooltips=[('State', '@state_name'),
                                     ('Party', '@party'),
                                     ('Impeach Trump', '@vote_17'),
                                     ('Reject Arizona election results', '@vote_10'),
                                     ('Approve Pennsylvania election results', '@vote_11'),
                                     ('Name of Representative', '@name'),
                                     ('Vote Summary', '@vote_summa')
                                     ]))

    return p3

def positive_reps(title):
    """
    Creates the visualizations for the web application using the Bokeh framework

    Args:
        title ([string]): title of figure
    Returns:
        p (bokeh object): bokeh plot figure
    """
    # Instantiate LinearColorMapper that linearly maps numbers in a range,
    # into a sequence of colors.
    color_mapper = LinearColorMapper(palette=blue_palette, low=0, high=max(districts['percent_po']))

    # Create color bar.
    color_bar = ColorBar(color_mapper=color_mapper,
                            label_standoff=8,
                            width=500, height=20,
                            border_line_color=None,
                            location=(0, 0),
                            orientation='horizontal')

    # Create figure object.
    p4 = figure(title="Percent Positive for Reps",
                plot_height=600,
                plot_width=950,
                toolbar_location='below',
                tools="pan, wheel_zoom, box_zoom, reset")
    
    # Hiding Axis Labels
    p4.xaxis.major_tick_line_color = None  # turn off x-axis major ticks
    p4.xaxis.minor_tick_line_color = None  # turn off x-axis minor ticks
    p4.yaxis.major_tick_line_color = None  # turn off y-axis major ticks
    p4.yaxis.minor_tick_line_color = None  # turn off y-axis minor ticks
    p4.xaxis.major_label_text_font_size = '0pt'  # turn off x-axis tick labels
    p4.yaxis.major_label_text_font_size = '0pt'  # turn off y-axis tick labels

    # Add patch renderer to figure.
    states = p4.patches("xs", "ys", source=geosource_districts,
                        fill_color={'field': 'percent_po',
                                    'transform': color_mapper},
                        line_color='gray',
                        line_width=0.75,
                        fill_alpha=1)

    # Create hover tool
    p4.add_tools(HoverTool(renderers=[states],
                            tooltips=[('State', '@state_name'),
                                    ('Party', '@party'),
                                    ('Percent Positive', '@percent_po'),
                                    ('Name of Representative', '@name'),
                                    ('Vote Summary', '@vote_summa'),
                                    ('Common Words', '@common_wor')
                                    ]))
    # Specify layout
    p4.add_layout(color_bar, 'below') 
    
    return p4      

def negative_reps(title):
    """
    Creates the visualizations for the web application using the Bokeh framework

    Args:
        title ([string]): title of figure
    Returns:
        p (bokeh object): bokeh plot figure
    """
    # Instantiate LinearColorMapper that linearly maps numbers in a range,
    # into a sequence of colors.
    color_mapper = LinearColorMapper(palette=red_palette, low=0, high=max(districts['percent_ne']))

    # Create color bar.
    color_bar = ColorBar(color_mapper=color_mapper,
                            label_standoff=8,
                            width=500, height=20,
                            border_line_color=None,
                            location=(0, 0),
                            orientation='horizontal')

    # Create figure object.
    p5 = figure(title="Percent Negative for Reps",
                plot_height=600,
                plot_width=950,
                toolbar_location='below',
                tools="pan, wheel_zoom, box_zoom, reset")
    
    # Hiding Axis Labels
    p5.xaxis.major_tick_line_color = None  # turn off x-axis major ticks
    p5.xaxis.minor_tick_line_color = None  # turn off x-axis minor ticks
    p5.yaxis.major_tick_line_color = None  # turn off y-axis major ticks
    p5.yaxis.minor_tick_line_color = None  # turn off y-axis minor ticks
    p5.xaxis.major_label_text_font_size = '0pt'  # turn off x-axis tick labels
    p5.yaxis.major_label_text_font_size = '0pt'  # turn off y-axis tick labels

    # Add patch renderer to figure.
    states = p5.patches("xs", "ys", source=geosource_districts,
                        fill_color={'field': 'percent_ne',
                                    'transform': color_mapper},
                        line_color='gray',
                        line_width=0.75,
                        fill_alpha=1)

    # Create hover tool
    p5.add_tools(HoverTool(renderers=[states],
                            tooltips=[('State', '@state_name'),
                                    ('Party', '@party'),
                                    ('Percent Negative', '@percent_ne'),
                                    ('Name of Representative', '@name'),
                                    ('Vote Summary', '@vote_summa'),
                                    ('Common Words', '@common_wor')
                                    ]))
    # Specify layout
    p5.add_layout(color_bar, 'below')    
    return p5

def reps_vs_constituents(title):
    """
    Creates the visualizations for the web application using the Bokeh framework

    Args:
        title ([string]): title of figure
    Returns:
        p (bokeh object): bokeh plot figure
    """
    # Instantiate LinearColorMapper that linearly maps numbers in a range,
    # into a sequence of colors.
    color_mapper = LinearColorMapper(palette=diverging_palette, low=min(districts['mean_dif_s']), high=max(districts['mean_dif_s']))

    # Create color bar.
    color_bar = ColorBar(color_mapper=color_mapper,
                            label_standoff=8,
                            width=500, height=20,
                            border_line_color=None,
                            location=(0, 0),
                            orientation='horizontal')

    # Create figure object.
    p6 = figure(title=title,
                plot_height=600,
                plot_width=950,
                toolbar_location='below',
                tools="pan, wheel_zoom, box_zoom, reset")
    
    # Hiding Axis Labels
    p6.xaxis.major_tick_line_color = None  # turn off x-axis major ticks
    p6.xaxis.minor_tick_line_color = None  # turn off x-axis minor ticks
    p6.yaxis.major_tick_line_color = None  # turn off y-axis major ticks
    p6.yaxis.minor_tick_line_color = None  # turn off y-axis minor ticks
    p6.xaxis.major_label_text_font_size = '0pt'  # turn off x-axis tick labels
    p6.yaxis.major_label_text_font_size = '0pt'  # turn off y-axis tick labels

    # Add patch renderer to figure.
    states = p6.patches("xs", "ys", source=geosource_districts,
                        fill_color={'field': 'mean_dif_s',
                                    'transform': color_mapper},
                        line_color='gray',
                        line_width=0.75,
                        fill_alpha=1)

    # Create hover tool
    p6.add_tools(HoverTool(renderers=[states],
                            tooltips=[('State', '@state_name'),
                                    ('Party', '@party'),
                                    ('Percent Positive', '@percent_po'),
                                    ('Name of Representative', '@name'),
                                    ('Vote Summary', '@vote_summa'),
                                    ('Constituent Common words', '@keywords_l'),
                                    ('Representative Common words', '@common_wor')
                                    ]))
    # Specify layout
    p6.add_layout(color_bar, 'below') 
    
    return p6      