# Plot candlestick chart

import os
import mplfinance as mpf
import matplotlib
import datetime
import pandas as pd
import numpy as np


def __clean_index(df, valid_index):
    # valid_index must be sorted
    idx_to_drop = df.index[(df.index < valid_index[0]) | (df.index > valid_index[-1])]
    df.drop(idx_to_drop, inplace=True)
    
def __extend_index(df, target_index):
    df_ext = df.reindex(target_index)
    # Align timestamps not exist in target_index
    unmatched = set(df.index) - set(target_index)
    for time in unmatched:
        i = df_ext.index.get_loc(time, method='ffill')   # align to the entry time of the bar
        df_ext.iloc[i] = df[time]
#         print(f'- align {time} to {df_ext.index[i]}')
    return df_ext

def __add_mark_layer(mark_layer, mark_set, direction, mark_size, is_show_marks, bar_data):
    if is_show_marks and mark_set is not None:
        for color, marks in mark_set.items():
            split_color = color.split('-')
            if len(split_color) == 2:
                color = split_color[0]
                size = int(split_color[1])
            else:
                size = mark_size
            __clean_index(marks, bar_data.index)
            if not marks.empty:
                marks = __extend_index(marks, bar_data.index)
                if direction == 'buy':
                    mark_layer.append(mpf.make_addplot(marks, type='scatter', markersize=size, marker='^', color=color))
                else:
                    mark_layer.append(mpf.make_addplot(marks, type='scatter', markersize=size, marker='v', color=color))


def candle_plot(bar_data, title, buy_marks=None, sell_marks=None, mark_size=100, show_marks=True, del_nan=False, 
                day_gap=False, save_to=None, bar_type='candle'):
    """
    Works great for jupyter notebook. For other back ends, change "matplotlib.use()"
    :param save_to: /folder/to/save/example.jpg, non-existent folders will be created
    :param bar_type: 'candle' or 'line'
    """
    
    bar_data = bar_data.copy()
    if del_nan:
        bar_data.dropna(subset=['Close'], inplace=True)
    if day_gap:
        # This works by adding 09:25-09:29 NaN prices, for CN stocks only
        dates = set(bar_data.index.date)
        indices = []
        for date in dates:
            indices.extend([datetime.datetime.combine(date, datetime.time(9, i)) for i in range(29, 24, -1)])
        gap = pd.DataFrame(np.nan, index=indices, columns=bar_data.columns)
        bar_data = pd.concat([bar_data, gap])
        bar_data.sort_index(inplace=True)
    
    options = {}
    if save_to:
        save_dir = os.path.dirname(save_to)
        if save_dir and not os.path.exists(save_dir):
            os.makedirs(save_dir)
        options['savefig'] = save_to
        matplotlib.use('agg')   # necessary to prevent memory leak
    else:
        matplotlib.use('module://ipykernel.pylab.backend_inline')
    
    mark_layer = []
    __add_mark_layer(mark_layer, buy_marks, 'buy', mark_size, show_marks, bar_data)
    __add_mark_layer(mark_layer, sell_marks, 'sell', mark_size, show_marks, bar_data)
    if mark_layer:
        options['addplot'] = mark_layer
    
    mpf.plot(bar_data, title=title, type=bar_type, style='yahoo', volume=True, figsize=(12.1, 6.5), **options)
