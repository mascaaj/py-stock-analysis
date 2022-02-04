#!/usr/bin/env python

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

__author__  = "Aloke Mascarenhas"
__credits__ = ["Udacity - ML for finance",
                "Charting and Tech Analysis - Fred McAllen", "Yahoo Finance"]
__license__ = "Apache 2.0"
__version__ = "0.0.1"
__status__  = "Developement"

#Todo :
# add proper docstrings to each function.
# add unit testing

def read_file(filename,cols=['Date','Adj Close']):
    """Read in a file name and return dataframe with the specified columns

        Arguments:
            filename {string} -- Path to csv to be loaded
            cols {list} -- List of columns (headers) to be read in.

        Returns:
            dataframe -- dataframe with the corresponding data
    """
    columns = cols
    df= pd.read_csv(filename, index_col="Date",
                    parse_dates=True,usecols=columns,
                    na_values=['nan'])
    return df


def multi_ticker_read(folder_path,start_date,
                    end_date,symbols,log=False,
                    cols=['Date','Adj Close']):
    """Load data from path using dictionary of symbols,
    start and end dates and columns needed"""
    #Define date range
    print("symbols requested: ", symbols)
    dates =  pd.date_range(start_date,end_date)
    print("date range selected:", dates)
    columns = cols
    #Create empty dataframe with dates index
    df1 = pd.DataFrame(index=dates)
    if log==True:
        print(df1)

    for symbol in symbols:
        filename =  folder_path + '{}'.format(symbol) + '.csv'
        if log==True:
             print(filename)
        df_temp = read_file(filename,columns)
        if log==True:
            print(df_temp.head())
        df_temp = df_temp.rename(columns={'Adj Close': symbol})
        df1 = df1.join(df_temp, how="inner")
        if log==True:
             print(df1.head())
    return df1

def plot_data(df,title="Stock prices"):
    """Plot the input dataframe df, add axes labels and title """
    ax = df.plot(title=title)
    ax.set_xlabel("Date")
    ax.set_ylabel("Price")
    plt.show()

def plot_selected(df, columns, start_index, end_index):
    """Plot the desired columns over index values in the given range."""
    df_temp = df.loc[start_index:end_index,columns]
    plot_data(df_temp)

def normalize_data(df):
    """Normalize data with respect to first entry in the dataframe"""
    return df/df.iloc[0,:]

def plot_normalized_data(df,title="Stock prices"):
    """Plot normalized data"""
    df = normalize_data(df)
    ax = df.plot(title=title)
    ax.set_xlabel("Date")
    ax.set_ylabel("Price")
    ax.axhline(y=1,color="black",linestyle="--")
    plt.show()

def get_rolling_mean(df,window=20,log=False):
    """Calculate Rolling Moving Average for the dataframe"""
    return df.rolling(window).mean()

def get_rolling_sd(df,window=20,log=False):
    """Calculate Rolling Standard Deviation for the dataframe"""
    return df.rolling(window).std()

def get_bollinger_bands(roll_mean,roll_sd):
    """Calculate Bollinger bands for the dataframe """
    upper_band = roll_mean + roll_sd *2
    lower_band = roll_mean - roll_sd *2
    return upper_band,lower_band

def plot_data_stats(df,window=20,title="Stock prices"):
    """Plot the input dataframe df, add axes labels and title """
    ax = df.plot(title=title)
    rm = get_rolling_mean(df,window)
    rsd = get_rolling_sd(df,window)
    ub,lb =  get_bollinger_bands(rm,rsd)
    colname = rm.columns.values.tolist()
    rm = rm.add_prefix('Rolling Mean_')
    colname = ub.columns.values.tolist()
    ub = ub.add_prefix('Bol_Upper_')
    colname = lb.columns.values.tolist()
    lb = lb.add_prefix('Bol_Lower_')
    ax = rm.plot(ax=ax)
    ax = ub.plot(ax=ax)
    ax = lb.plot(ax=ax)
    ax.set_xlabel("Date")
    ax.set_ylabel("Price")
    plt.show()

def get_daily_returns(df,log=False):
    """Returns plot of daily returns in percent.
    Dataframe is returned when log is passed as true"""
    daily_returns = ((df / df.shift(1))-1)*100
    daily_returns.iloc[0,:]=0
    ax = daily_returns.plot(title="Daily returns")
    ax.set_xlabel("Date")
    ax.set_ylabel("% return")
    plt.show()
    if log==True:
        return daily_returns
    else:
        print("logging disabled")

def get_cumulative_returns(df,log=False):
    """Returns plot of cumulative return in percent.
    Dataframe is returned when log is passed as true"""
    price_t0 =  df.iloc[0]
    cum_returns = ((df/price_t0)-1)*100
    ax = cum_returns.plot(title="Cumulative returns")
    ax.set_xlabel("Date")
    ax.set_ylabel("% return")
    plt.show()
    if log==True:
        return cum_returns
    else:
        print("logging disabled")

def daily_returns_stats_single(df):
    """
    Single stock stats
    Prints the daily return stats and histogram with mu and +/- 1 sigma
    returns mean, sigma and kurtosis.
    """
    dr = get_daily_returns(df, log=True)
    dr.hist(bins=20)
    mean = dr.mean().values
    sd = dr.std().values
    print("Mean :",mean)
    print("Std Dev :",sd)
    kurt = dr.kurtosis().values
    print("Kurtosis :",kurt)
    plt.axvline(x=mean,color="white",linestyle="--",linewidth="2")
    plt.axvline(x=mean+sd,color="red",linestyle="--")
    plt.axvline(x=mean-sd,color="red",linestyle="--")
    plt.show()
    return mean,sd,kurt

def daily_returns_stats_multiple(df,bins=20,alpha=0.65,log=True):
    """
    Single stock stats
    Prints the daily return stats and histogram with mu and +/- 1 sigma
    returns mean, sigma and kurtosis in a dataframe
    """
    dr = get_daily_returns(df, log=True)
    symbols = dr.columns.values.tolist()
    for sym in symbols:
        dr[sym].hist(bins=bins,label = sym,edgecolor='k', alpha=alpha)
    mean = dr.mean().values
    sd = dr.std().values
    kurt = dr.kurtosis().values
    output = pd.DataFrame({'mean':mean,'sd':sd,'kurt':kurt},index=symbols)
    if log==True:
        print(output)
    plt.legend(loc='upper right')
    plt.show()
    return output

def daily_scatter_stats(df,symbols=[],log=False):
    """
    Scatterplots and linear regression values for two stocks
    If not specified, the function uses the first two columns
    If log is turned on, beta, alpha values are printed
    Along with the corellation using default pearson method.
    """
    dr = get_daily_returns(df, log=True)
    if not symbols:
        print("Symbol array is empty, selecting the first columns of data frame")
        symbols = dr.columns.values.tolist()
    print(symbols[0],"vs",symbols[1])
    beta,alpha = np.polyfit(dr[symbols[0]],dr[symbols[1]],1)
    if log==True:
        print ("beta_{}".format(symbols[1]), beta)
        print ("alpha_{}".format(symbols[1]), alpha)
    dr.plot(kind='scatter',x=symbols[0],y=symbols[1],edgecolor='k')
    plt.plot(dr[symbols[0]],beta*dr[symbols[0]] + alpha,'-',color="red")
    plt.grid()
    plt.show()
    if log==True:
        print(dr.corr(method='pearson'))
