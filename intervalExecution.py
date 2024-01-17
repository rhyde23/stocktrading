#This script will run every interval

import calculateIndicators, requests
from bs4 import BeautifulSoup

from datetime import datetime
from pytz import timezone


#SELECTION STRATEGIES
#Selection strategy that extracts the list of 100 most traded stocks from tradingview.com and filters out stocks that don't meet the minimum relative volume of 1.5
def selection1() :
    
    #Processes url request for tradingview.com of the most active stocks of the day
    r = requests.get("https://www.tradingview.com/markets/stocks-usa/market-movers-active/")

    #Apply BeautifulSoup() to the website request
    soup = BeautifulSoup(r.content, 'html.parser')

    #Empty list that will be populated with stock tickers that meet the relative volume criteria
    accepted = []

    #Loop that iterates through each stock in the top 100 most traded stocks of the day from tradingview.com
    for stock in soup.find_all("tr", {"class":"row-RdUXZpkv listRow"}) :
        
        #Get the ticker of the current stock
        ticker = stock.attrs['data-rowkey'].split(":")[1]
        
        #Get its relative volume and accept stock if its relative volume is greater or equal to the minimum relative volume input
        try :
            relative_volume = float(stock.find_all("td", {"class":"cell-RLhfr_y4 right-RLhfr_y4"})[3].contents[0])
            if relative_volume >= 1.5 :
                accepted.append(ticker)
        except :
            pass
        
    #Return accepted list of stock tickers
    return accepted

#Selection strategy that simply returns the "Big 7" tech stock of the modern era
def selection2() :
    return ["AAPL", "AMZN", "MSFT", "NVDA", "META", "TSLA", "GOOG"]

#ENTRANCE STRATEGIES

indicator_outputs = {}

#Possible entrance strategy based on a mid-term analysis
def entrance1() :
    if indicator_outputs["RSI"][14] > 70 and indicator_outputs["EMA"][20] > indicator_outputs["EMA"][50] and indicator_outputs["MACD"][(12, 26, 9)][0] > indicator_outputs["MACD"][(12, 26, 9)][1] :
        return 1
    if indicator_outputs["RSI"][14] < 30 and indicator_outputs["EMA"][20] < indicator_outputs["EMA"][50] and indicator_outputs["MACD"][(12, 26, 9)][0] > indicator_outputs["MACD"][(12, 26, 9)][1] :
        return 2

#Possible entrance strategy based on a short-term analysis
def entrance2() :
    if indicator_outputs["RSI"][9] > 70 and indicator_outputs["EMA"][9] > indicator_outputs["EMA"][21] and indicator_outputs["MACD"][(5, 35, 5)][0] > indicator_outputs["MACD"][(5, 35, 5)][1] :
        return 1
    if indicator_outputs["RSI"][9] < 30 and indicator_outputs["EMA"][9] < indicator_outputs["EMA"][21] and indicator_outputs["MACD"][(5, 35, 5)][0] > indicator_outputs["MACD"][(5, 35, 5)][1] :
        return 2

#EXIT STRATEGIES

def exit1() :
    pass

def exit2() :
    pass

#######################################################################################################################################################################################

#Dictionary to pass to calculateIndicators.calculate_indicators that signals which values of which indicators to calculate
indicator_inputs_required = {
    "RSI":[9, 14],
    "EMA":[9, 20, 21, 50],
    "MACD":[(12, 26, 29),(5, 35, 5)]
}


#List of strategies to log performance data for

stock_selection_strategies = [selection1, selection2]

strategies = [
    [entrance1, exit1],
    [entrance2, exit2],
]

#######################################################################################################################################################################################

#List to track what stocks each strategy is currently holding
strategies_currently_holding = [[]]*(len(strategies)*len(stock_selection_strategies))

stock_selections = [[]]*len(stock_selection_strategies)

def stock_exchanges_are_open() :
    tz = timezone('EST')
    split_by_colon = str(datetime.now(tz)).split(" ")[1].split(":")
    hour, minutes = int(split_by_colon[0]), int(split_by_colon[1])
    minutes_elapsed = (hour*60)+minutes
    return minutes_elapsed >= 570 and minutes_elapsed <= 960

#Main function that will run every strategy
def main() :
    global indicator_outputs
    while True :
        if not stock_exchanges_are_open() :
            print("Stock exchanges are closed")
            break

        for stock_selection_strategy_index, stock_selection_strategy in enumerate(stock_selection_strategies) :
            stock_selections[stock_selection_strategy_index] = stock_selection_strategy()

        for stock_selections_index, stock_selections in enumerate(stock_selections) :
            for ticker in stock_selections :
                indicator_outputs = calculateIndicators.calculate_indicators(ticker, indicator_inputs_required, 1000)
                for strategy_index, strategy in enumerate(strategies) :

                    if not ticker in #IF NOT TICKER ALREADY CURRENTLY HOLDED 

                    
                    enter_result = enter_strategy()
                    if enter_result == 1 :
                        pass
                    elif enter_result == 2 :
                        pass



main()
