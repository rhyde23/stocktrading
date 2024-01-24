#This script calculates the variety of indicators used for entrance/exit strategies

import time

#Import the Python package yfinance. yfinance is an open source project that scrapes stock quotes and other stock data from Yahoo Finance
import yfinance as yf

#This is the global variable that stores the historical data of a stock from yfinance
hist_data = None

#All of these global variables for indicator calculations will be populated within the "calculate_indicators" function
indicator_outputs, avg_gains, avg_losses, fast_emas, slow_emas, macds, macd_emas = {}, [], [], [], [], [], []

#Function to create the RSI "smoothing effect" based on the next closing price difference
#Input = the current average gain/loss, the RSI period in days, and the next closing price difference between a day and its previous day
def update_rsi(current_avg:float, period:int, difference:float) :
    return ((current_avg*(period-1))+difference)/period

#Function to calculate Relative Strength Indexes (RSI's)
#Input = periods for RSI calculation in days, the index of the current day within the yfinance closing price data
def calculate_rsi(periods:list, i:int) :
    
    #Calculate difference between the current day's closing price and the previous day's closing price
    difference = hist_data.iloc[i]["Close"]-hist_data.iloc[i-1]["Close"]

    #Loop that iterates through every RSI period of the function's input
    for x, period in enumerate(periods) :

        #If the number of days iterated so far in the Main loop hasn't reached the RSI period, keep adding the closing price difference until initial smoothing.
        if i < period :

            #If the difference is a gain, add it to the average gain for this RSI period
            if difference >= 0 :
                avg_gains[x] += difference

            #If the difference is a loss, add it to the average loss for this RSI period
            else :
                avg_losses[x] += -difference

        #If the number of days iterated so far in the Main loop HAS reached the RSI period, begin smoothing effect
        else :

            #If the number of days iterated so far in the Main loop is exacly equal to the RSI period, calculate initial RSI value before smoothing by dividing the total sums so far by the RSI period in days
            if i == period :
                avg_gains[x] = avg_gains[x]/period
                avg_losses[x] = avg_losses[x]/period

            #If the difference is a gain, smooth average gain and average loss using the difference for the average gain and 0 for the average loss
            if difference >= 0 :
                avg_gains[x] = update_rsi(avg_gains[x], period, difference)
                avg_losses[x] = update_rsi(avg_losses[x], period, 0)

            #If the difference is a loss, smooth average gain and average loss using the difference for the average loss and 0 for the average gain
            else :
                avg_gains[x] = update_rsi(avg_gains[x], period, 0)
                avg_losses[x] = update_rsi(avg_losses[x], period, -difference)

#Function to update any Exponential Moving Average (EMA) given a recent close value using the EMA formula
#Input = the current EMA, the exponential percentage, and the recent close value
def update_ema(current_ema:float, exp_percentage:float, recent_close:float) :
    return (recent_close*exp_percentage)+(current_ema*(1-exp_percentage))

#Function to calculate Exponential Moving Averages (EMAS's)
#Input = periods for EMA calculation in days, the index of the current day within the yfinance closing price data
def calculate_ema(periods:list, i:int) :

    #Define this day's closing price
    recent_close = hist_data.iloc[i]["Close"]

    #Loop that iterates through every EMA period of the function's input
    for period in periods :

        #Update EMA for this period using the "update_ema" function
        indicator_outputs["EMA"][period] = update_ema(indicator_outputs["EMA"][period], 2/(period+1), recent_close) #2/(period in days + 1) is the formula to calculate an exponential percentage 


#Function to calculate Moving Average Convergence/Divergences (MACD's) and their EMA's. 
#Input = MACD combinations in the form of the tuple: (Fast EMA period in days, Slow EMA Period in days, MACD EMA Period in days), the index of the current day within the yfinance closing price data
def calculate_macd(combinations:list, i:int) :

    #Loop that iterates through every MACD combination input
    for x, combination in enumerate(combinations) :

        #Update fast EMA and slow EMA for this MACD combination using the "update_ema" function
        fast_emas[x] = update_ema(fast_emas[x], 2/(combination[0]+1), hist_data.iloc[i]["Close"]) #2/(period in days + 1) is the formula to calculate an exponential percentage
        slow_emas[x] = update_ema(slow_emas[x], 2/(combination[1]+1), hist_data.iloc[i]["Close"]) #2/(period in days + 1) is the formula to calculate an exponential percentage

        #Update the MACD value using the MACD formula
        macds[x] = fast_emas[x]-slow_emas[x]

        #If the MACD EMA value is none, set its initial value to the current MACD
        if macd_emas[x] == None :
            macd_emas[x] = macds[x]

        #Update the MACD EMA value using the "update_ema" function
        macd_emas[x] = update_ema(macd_emas[x], 2/(combination[2]+1), macds[x]) #2/(period in days + 1) is the formula to calculate an exponential percentage
 
#Main function to return a stocks' technical indicator values
#Input = stock ticker, dictionary with key=technical indicator abbreviation and value=the list of different settings combinations that need to be calculated for that indicator

def calculate_indicators(ticker:str, indicator_inputs:dict, historical_data_period:int) :
    
    #Declare global scope for all of these variables
    global indicator_outputs, hist_data, avg_gains, avg_losses, fast_emas, slow_emas, macds, macd_emas
    
    #Access stocks' historical data from yahoo finance
    hist_data = yf.Ticker(ticker).history(period=str(historical_data_period)+"D")

    #Set the default average gain and average loss values for each period to 0 for RSI calculations
    avg_gains, avg_losses = [0]*len(indicator_inputs["RSI"]), [0]*len(indicator_inputs["RSI"])

    #Set all the EMA's for each input period to the first available closing price from the yahoo finance data for EMA calculations
    indicator_outputs["EMA"] = {inp:hist_data.iloc[0]["Close"] for inp in indicator_inputs["EMA"]}

    #Set fast period EMA's and slow period EMA's to the default value of the first closing price from the yfinance closing price data 
    fast_emas = [hist_data.iloc[0]["Close"]]*len(indicator_inputs["MACD"])
    slow_emas = [hist_data.iloc[0]["Close"]]*len(indicator_inputs["MACD"])

    #Set MACD's and MACD's EMA's to a null value 
    macds = [None]*len(indicator_inputs["MACD"])
    macd_emas = [None]*len(indicator_inputs["MACD"])

    #Main loop that iterates through every day's closing stock price going back in history
    for i in range(1, len(hist_data)) :
        calculate_rsi(indicator_inputs["RSI"], i)
        calculate_ema(indicator_inputs["EMA"], i)
        calculate_macd(indicator_inputs["MACD"], i)

    #RSI results for each RSI period input using the RSI formula
    indicator_outputs["RSI"] = {indicator_inputs["RSI"][ind]:100-(100/(1+(avg_gains[ind]/avg_losses[ind]))) for ind in range(len(indicator_inputs["RSI"]))}

    #MACD and MACD EMA results for each MACD setting combination
    macd_zipped = list(zip(macds, macd_emas))
    indicator_outputs["MACD"] = {indicator_inputs["MACD"][ind]:macd_zipped[ind] for ind in range(len(indicator_inputs["MACD"]))}

    #Add the current price of the stock to the outputs dictionary
    indicator_outputs["CurrentPrice"] = hist_data.iloc[-1]["Close"]
    
    #Return indicator_outputs dictionary
    return indicator_outputs

def update_indicators(recent_close_price:int, old_indicators:dict) :
    current_indicators = {}
    #current_indicators["RSI"] = {update_input:update_rsi(current_avg:float, period:int, difference:float)}
    for update_input in old_indicators["RSI"] :
        #current_indicators[] = "weqfgqeg"
        pass


start = time.time()
print(calculate_indicators("MSFT", {"RSI":[5, 9, 14], "EMA":[10, 20, 50, 100, 200], "MACD":[(12, 26, 9), (5, 35, 5), (19, 39, 9)]}, 1000))
print(time.time()-start) #Speed performance tracking
#while True :
    #print(calculate_indicators("MSFT", {"RSI":[3], "EMA":[10], "MACD":[(12, 26, 9)]}, 1000))

