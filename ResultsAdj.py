import yfinance as yf #to pull financial data
import pandas as pd # to display screener results later in program
import sys # to allow program to be ended based on user preference
import os # to automatically display the line graph created 
import statistics # to calculate medians 

#determine whether or not user wants to use the screening tool after explaining what it does
def startProgram():
    print("Hello. The following program predominantly uses fundamental analysis to rank companies based on qualities commonly associated with attractive investment opportunities.\n")
    print("The screener calculates an overall score across company health and valuation-related metrics for each stock with the required data from a predetermined list of mega-cap tech stocks. It then displays an ordered table showing each stock’s ticker symbol and rank. This allows the screener to cater to Buffett-like investors who prioritise value and company health when trying to identify potentially profitable investments.\n")
    print("The screener also displays an ordered table showing the ranking when momentum is taken into consideration during the calculation of each stock’s overall score. This allows the screener to cater to investors who prefer a Stockopedia-like approach to investing. In allocating each company a StockRank, Stockopedia accounts for momentum alongside value and quality before determining an overall score, believing these are the three key drivers of returns.")

    start=input("\nYou have now been informed of the function of this program. Would you like to proceed (Y/N)? ").strip().upper() # Determine if the user wants to try the screening tool or not
    while start not in ["Y", "N"]:
        start=input("\nError. Please ensure you are only inputting a 'Y' or an 'N'. Try again: ").strip().upper() # input validation
    if start=="N": # if they dont, exit program. If they do, program proceeds
        sys.exit(0)
        
#get stock information. Remove any stocks with missing relevant data. Get the individual scores contributing to the health, valuation and momentum scores. Get the health and valuation scores for the Buffett-like approach as well as the health, valuation, and momentum scores for the Stockopedia-like approach. Get the final score for each stock for both investing approaches
def getScores(oldStocks):
    allStockInfo, stocks=GetTickerInfo(oldStocks) #get the available stock information dictionaries
    allStockInfo, stocks=checkInfo(allStockInfo, stocks) #remove any stocks with missing relevant data in their information dictionaries

    #define arrays to store the health, valulation and momentum scores. The '...Improving' scores refer to those for the Stockopedia-like approach and the '...Value' scores refer to those for the Buffett-like approach
    healthScoreValue=[]
    healthScoreImproving=[]
    momentumScore=[]
    valuationScoreValue=[]
    valuationScoreImproving=[]
    finalStockScoresImproving=[]
    finalStockScoresValue=[]

    #get value score components:
    peScores=peAndPsScore(['trailingPE', 'forwardPE'], allStockInfo, [True, True])
    priceToFcfScore=priceToFcf(allStockInfo, 'marketCap', 'freeCashflow', True)
    pegScores=pegScore('trailingPE', 'trailingPegRatio', allStockInfo, True)
    evToEbitda=evToEbitdaScore(allStockInfo, 'enterpriseValue', 'ebitda', 'enterpriseToEbitda', True)#evToEbitda, priceToFcfScore, pegScores and peScores store scores based on metrics assessing valuation relative to free cashflow, earnings, and EBITDA,  meaning young and growing companies are less likely to score highly
    evToRevenue=evToRevenueScore(allStockInfo, 'enterpriseToRevenue', 'enterpriseValue', True)
    psScores=peAndPsScore(['priceToSalesTrailing12Months'], allStockInfo, [True]) # psScores and evToRevenue store valuation scores based on metrics assessing valuation relative to top-line performance, meaning they are likely more favourable for young and growing companies 
   
    #get health score components:
    epsGrowthScore=epsGrowth(allStockInfo, 'forwardEps', 'trailingEps', False) 
    revAndEarnGrowth=getScore(['earningsQuarterlyGrowth', 'revenueGrowth'], allStockInfo, [False, False]) # revAndEarnGrowth and epsGrowthScore store scores associated with earnings growth and revenue growth
    profitScore=getScore(['returnOnAssets', 'profitMargins','operatingMargins'], allStockInfo, [False, False, False]) # profitScore stores scores associated with company profitability
    currentRatioScores=currentRatioScore(allStockInfo, 'currentRatio') # currentRatioScores stores scores associated with company liquidity
    cfoToDebtScore=cfoToDebt(allStockInfo, 'operatingCashflow', 'totalDebt', False)  # cfoToDebtScore stores scores associated with each company's debt burden relative to the cash-generating ability of operations
  
    #get momentum score components:
    proxToHighScores=proxToHighScore(allStockInfo, 'previousClose', 'fiftyTwoWeekHigh', False) # proxToHighScores stores scores associated with the proximity of the current share price for each stock to its peak over the last year  
    oneYearPerformanceScore=getScore(['52WeekChange'], allStockInfo, [False]) # oneYearPerformanceScore stores scores associated the fractional change in share price for each stock over the past year
    goldenCrossScore=signalScore(allStockInfo, 'fiftyDayAverage', 'twoHundredDayAverage') #goldenCrossScore stores scores associated with whether or not there is currently a positive trend signal for each stock
    trendIntensityScore=getScore(['twoHundredDayAverageChangePercent'], allStockInfo, [False]) # trendIntensityScore stores scores based on each stock's current share price trend

    for i in range(len(allStockInfo)): #get the valuation and health scores for the Buffett-like approach and the valuation, health and momentum scores for the Stockopedia-like approach
            valuationScoreValue.append((peScores[i]+priceToFcfScore[i]+evToEbitda[i]+pegScores[i]+psScores[i]+evToRevenue[i])/7) # logic for each non-weighted score calculation: get average score across all metrics contributing to the subcategory of the overall score
            healthScoreValue.append(((epsGrowthScore[i]+revAndEarnGrowth[i])/3)*(0.25) + currentRatioScores[i]*(0.25) + (profitScore[i]/3)*(0.25)+((cfoToDebtScore[i])*(0.25))) # logic for each weighted score calculation: get average score in each subsection of the subcategory of the overall score, apply chosen weighting and sum to get overall score for the subcategory of the overall score
            valuationScoreImproving.append(((peScores[i]+priceToFcfScore[i]+evToEbitda[i]+pegScores[i])/5)*(0.6)+((psScores[i]+evToRevenue[i])/2)*(0.4)) 
            healthScoreImproving.append(((epsGrowthScore[i]+revAndEarnGrowth[i])/3)*(0.35) + currentRatioScores[i]*(0.25)+(profitScore[i]/3)*(0.15)+((cfoToDebtScore[i])*(0.25)))
            momentumScore.append((proxToHighScores[i]+oneYearPerformanceScore[i]+goldenCrossScore[i]+trendIntensityScore[i])/4)

    for i in range(len(valuationScoreValue)): # using the valuation, health, and momentum scores get the final score for each stock for both investing approaches
        finalStockScoresImproving.append((valuationScoreImproving[i])*(1/3)+(healthScoreImproving[i])*(1/3)+momentumScore[i]*(1/3))
        finalStockScoresValue.append((valuationScoreValue[i])*(0.5)+(healthScoreValue[i])*(0.5))

    return finalStockScoresImproving, finalStockScoresValue, stocks


#display the ranking tables. If the tables create subsequent user interest in a particular company, display a line graph showing the adjusted closing price, 50DMA and 200DMA over the past year for this company in excel
def displayToUser(finalStockScoresImproving, finalStockScoresValue, stocks):
    displayResults(finalStockScoresValue, "Buffett-like", stocks) # displays ranking table for Buffett-like approach
    displayResults(finalStockScoresImproving, "Stockopedia-like", stocks) # displays ranking table for Stockopedia-like approach

    #determine whether or not user is interested in a company and would like to see a line graph for it
    choice=input("Given these results, you may want to investigate one of the stocks ranked by the screener further. This program can help kickstart your subsequent research by displaying in excel a line graph showing the adjusted closing price, the 50DMA and the 200DMA over the last year for the stock you are interested in. Would you like the program to do this (Y/N)? ").strip().upper() 
    while choice not in ['Y', 'N']:
        choice=input("\nError. Please ensure you are only entering 'Y' or 'N'. Try again: ").strip().upper() # input validation
    if choice=='N':
        sys.exit(0) # exit program if user isnt interested 
    else:
        stock=input("\nWhich stock from the displayed tables would you like to further research? ").strip().upper() # if user is interested, determine which stock they would like to investigate further
        while stock not in stocks:
            stock=input("\nError. Please ensure you have entered the ticker symbol for a company in the tables provided. Try again: ").strip().upper() # input validation
  
    #Note: subsequent code only runs if user is interested in seeing a line graph because, otherwise, program will have ended already
    dataForChoice=yf.download(stock, period="2y") #download market data for the user's chosen stock over the past 2 years
    dataForChoice["50DMA"]=dataForChoice['Close'].rolling(50).mean() # add a column called '50DMA' to the downloaded table storing the 50DMA on each trading day over the last 2 years (except the first 49 trading days which are NaN)
    dataForChoice["200DMA"]=dataForChoice['Close'].rolling(200).mean() # add a column called '200DMA' to the downloaded table storing the 200DMA on each trading day over the last 2 years (except the first 199 trading days which are NaN)
    relevantDataForChoice=dataForChoice[["Close", "50DMA", "200DMA"]].tail(252) # create a new table called 'relevantDataForChoice' storing the 50DMA, 200DMA and adjusted closing price for the chosen stock over the last 252 trading days


    with pd.ExcelWriter("results.xlsx", engine="xlsxwriter") as writer: #set the output file to 'results.xlsx' and prepare to write the data to it
        relevantDataForChoice.to_excel(writer, sheet_name="Data Sheet") # write the new table created to a sheet called 'Data Sheet' in 'results.xlsx'
        workbook=writer.book #get the underlying xlsxwriter workbook object for the file
        workbook.add_worksheet("Results") # add a worksheet to the excel file for the graph to be displayed on called 'Results'
        chartSheet=writer.sheets["Results"] #assign chartSheet to the new worksheet created
        writer.sheets["Results"].activate() # change the default sheet displayed when file is opened from 'Data Sheet' to 'Results'
        writer.sheets["Data Sheet"].hide() # hide from user, but dont delete, the 'Data Sheet' sheet
        chart=workbook.add_chart({'type':'line'}) # create a line graph 
        chart.add_series({'name':'Closing Price (adj) ', 'categories':['Data Sheet', 3, 0, len(relevantDataForChoice)+2, 0], 'values':['Data Sheet', 3, 1, len(relevantDataForChoice)+2, 1]}) # add line to graph representing the closing prices for the chosen stock over the last 252 trading days
        chart.add_series({'name':'50DMA', 'categories':['Data Sheet', 3, 0, len(relevantDataForChoice)+2, 0], 'values': ['Data Sheet', 3, 2, len(relevantDataForChoice)+2, 2]}) # add line to graph representing the 50DMA for the chosen stock over the last 252 trading days
        chart.add_series({'name':'200DMA', 'categories':['Data Sheet', 3, 0, len(relevantDataForChoice)+2, 0], 'values': ['Data Sheet', 3, 3, len(relevantDataForChoice)+2, 3]}) # add line to graph representing the 200DMA for the chosen stock over the last 252 trading days
        chart.set_x_axis({'name': 'Date and Time', 'name_font':{'size':15}, 'num_font':{'size':11}, 'major_gridlines': {'visible':True}, 'minor_gridlines': {'visible':True}}) #add x-axis label and increase its size, adjust the size of the numbers on the x-axis, turn on major and minor gridlines.
        chart.set_y_axis({'name':'Price ($)', 'name_font':{'size':15}, 'num_font':{'size':11}, 'major_gridlines': {'visible':True}, 'minor_gridlines': {'visible':True}}) #add y-axis label and increase its size, adjust the size of the numbers on the y-axis, turn on major and minor gridlines.
        chart.set_size({'width':1500, 'height':1000}) # increase the size of the chart on the 'Results' sheet
        chart.set_title({'name': f"50DMA, 200DMA and Closing Price (adj) Over Past Year for {stock}"}) # set title for chart
        chartSheet.insert_chart('A1', chart) # insert line graph into the top left of the 'Results' sheet 
        os.startfile('results.xlsx') # display the excel file created to the user

    




















#Getting data for analysis
def GetTickerInfo(oldStocks):
    allStockInfo=[]
    stocks=[]
    
    for s in oldStocks: # loop for initial list of stocks
        try:
            stock=yf.Ticker(s) #get the yfinance ticker object for each stock
            allStockInfo.append(stock.info) #store each dictionary of stock information obtained from the ticker object in an array
            stocks.append(s) # store the name of the stock in the array 'stocks' after confirming it's information dictionary is retrievable. This array will replace 'oldStocks'
        except Exception: # if an error occurs in retrieving the dictionary of information for a stock, it is not added to 'stocks' meaning it will no longer be considered by the screening tool
            print(f"Error. No data can be pulled for {s}. It will be removed from the list of stocks analysed by the screener.") 
    
    return allStockInfo, stocks


#This function will be called after GetTickerInfo(), meaning each stock in 'stocks' can be assumed to have a retrieveable information dictionary. However, any stock which has missing relevant data in their information dictionary must be identified and removed, which is what this function does. If this sifting process leaves less than 5 stocks, exit program 
def checkInfo(allStockInfo, stocks):
    #create array storing the metrics that the screener uses when comparing stocks
    metrics=['ebitda', 'enterpriseValue', 'fiftyDayAverage', 'twoHundredDayAverage', 'trailingPE', 'forwardPE', 'priceToSalesTrailing12Months', 'enterpriseToRevenue', 'enterpriseToEbitda', 'trailingPegRatio', 'marketCap', 'freeCashflow', 'earningsQuarterlyGrowth', 'revenueGrowth', 'returnOnAssets', 'profitMargins', 'currentRatio', 'operatingMargins', 'forwardEps', 'trailingEps', 'previousClose', '52WeekChange', 'fiftyTwoWeekHigh', 'twoHundredDayAverageChangePercent', 'operatingCashflow', 'totalDebt']

    for i in range(len(metrics)): # loop for each metric that the screener uses when comparing stocks
        for y in range(len(allStockInfo)-1, -1, -1): # reverse loop through stocks to prevent index out of bounds error after deleting
            if allStockInfo[y].get(metrics[i]) is None: #if the metric is missing from the stock information dictionary for a stock
                del allStockInfo[y] #delete the stock's information dictionary from the array of information dictionaries analysed by the screener, preventing the stock from being considered further by the screening tool
                del stocks[y] #delete the stock's name from the array of stock names used by the screener, preventing the stock from being considered further by the screening tool

    if len(allStockInfo)<5: #if this sifting process leaves less than 5 stocks, exit program
        print("Error. Due to a lack of data on too many of the stocks that the screener was going to analyse, the program cannot fulfill its function and will now end.")
        sys.exit(0)
    else:
        return allStockInfo, stocks  #return all the stocks which have all the metrics analysed by the screener available in their stock information dictionaries (provided there is atleast 5 such stocks)       


#allocate a score to each stock based on how a specific financial metric varies across them. Inverting the scoring system allows for a financial metric where a lower value corresponds to a higher score
def normalisePoints(metricsArray, invert):
    points=[]
    maxVal=max(metricsArray) # get the maximum metric value across the stocks
    minVal=min(metricsArray) # get the minimum metric value across the stocks

    if minVal==maxVal: # if division by zero will occur
        return [0]*len(metricsArray) # skip this metric
    elif not(invert): # if a higher value means a higher score
        for m in metricsArray:
            points.append((m-minVal)/(maxVal-minVal)) # min-max normalisation applied
    else: # if a lower value means a higher score
        for m in metricsArray:
            points.append(1-((m-minVal)/(maxVal-minVal))) # apply and invert the min-max normalisation
            
    return points


#getting the points for each stock for the directly comparable metrics. These metrics do not require extra scoring system considerations or edge case handling after the data is pulled from yfinance, so they can all be scored by this general function
def getScore(metrics, allStockInfo, inverts):
    truePointAllocation=[0]*len(allStockInfo)

    for i in range(len(metrics)): # loop for each of the directly comparable metrics
        metricValues=[] 
        for y in range(len(allStockInfo)): #loop for each stock
            metricValues.append(allStockInfo[y].get(metrics[i])) # store the metric values for each stock

        proxyPointsAllocation=normalisePoints(metricValues, inverts[i])# get score for each stock for the metric based on relative performance of its metric value
        for z in range(len(allStockInfo)): #loop for each stock
            truePointAllocation[z]+=proxyPointsAllocation[z] # increment the overall score for each stock for this function call instance based on its score for the metric
           
    return truePointAllocation


#getting the points for each stock based on their P/E or P/S. Although the negative case consideration is not necessary for P/S, it doesnt affect the scoring and allows function reuse
def peAndPsScore(metrics, allStockInfo, inverts):
    truePointAllocation=[0]*len(allStockInfo) # initially set each stock's score to zero

    for i in range(len(metrics)): # loop for each metric
        metricValues=[]
        validIndexes=[]
        for y in range(len(allStockInfo)): # loop for each stock
            if allStockInfo[y].get(metrics[i])>0: # if metric value is positive
                validIndexes.append(y) # store position of stock in allStockInfo
                metricValues.append(allStockInfo[y].get(metrics[i])) # store metric value for stock
        #Note: if a stock has a negative metric value, it will receive the minimum score because its score is initially set to zero and it will not have its score changed

        if len(metricValues)>1: # provided there is atleast two positive values for the metric
            proxyPointsAllocation=normalisePoints(metricValues, inverts[i]) # get scores for the stocks with positive metric values for the metric
            for z in range(len(validIndexes)):
                truePointAllocation[validIndexes[z]]+=proxyPointsAllocation[z] #increment the overall score for this function call instance for each stock with a positive metric value
        elif len(metricValues)==1: # if there is only one positive value for this metric
            truePointAllocation[validIndexes[0]]+=0.5 # give the stock with the positive value 0.5 points
        #Note: if there is no positive values for the metric, each stock gets zero score for it.

    return truePointAllocation


#getting the points for each stock based on their PEG
def pegScore(trailingPe, trailingPeg, allStockInfo, invert):
    truePointAllocation=[0]*len(allStockInfo) # initially set each stock's score to zero
    pegValues=[]
    validIndexes=[]
    
    for i in range(len(allStockInfo)): # loop for each stock
        if allStockInfo[i].get(trailingPe)<0 and allStockInfo[i].get(trailingPeg)>0: # if P/E<0 and PEG>0 for stock
            truePointAllocation[i]=0.5 # stock gets 0.5 points
        elif allStockInfo[i].get(trailingPeg)>0: # if PEG is positive for stock
            validIndexes.append(i) # store position of stock in allStockInfo
            pegValues.append(allStockInfo[i].get(trailingPeg)) # store PEG value for stock
        #Note: If a stock has a negative PEG, it gets minimum score

    if len(pegValues)>1: # given there is atleast two stocks with positive PEG 
        proxyPointAllocation=normalisePoints(pegValues, invert) # get scores for stocks with positive PEG
        for i in range(len(pegValues)): # loop for each stock with positive PEG
            truePointAllocation[validIndexes[i]]=proxyPointAllocation[i] # award score for each stock with positive PEG
    elif len(pegValues)==1: # if there is only one positive PEG value
            truePointAllocation[validIndexes[0]]=0.5 # give the stock with the positive PEG 0.5 points
                           
    return truePointAllocation


#getting the points for each stock based on their EV/EBITDA values
def evToEbitdaScore(allStockInfo, enterpriseValue, Ebitda, enterpriseToEbitda, invert):
    enterpriseToEbitdaValues=[]
    validIndexes=[]
    totalScores=[0]*len(allStockInfo) # initially set each stock's score to zero
    
    for i in range(len(allStockInfo)): # loop for each stock
        if allStockInfo[i].get(enterpriseValue)>0 and allStockInfo[i].get(Ebitda)>0: # if EV>0 and EBITDA>0
            enterpriseToEbitdaValues.append(allStockInfo[i].get(enterpriseToEbitda)) # store EV/EBITDA for stock
            validIndexes.append(i) # Store position of stock in allStockInfo
        elif allStockInfo[i].get(enterpriseValue)<=0 and allStockInfo[i].get(Ebitda)>0: # if EV<=0 and EBITDA>0 for stock
            totalScores[i]+=1 # give stock the maximum score
        elif allStockInfo[i].get(enterpriseValue)<=0 and allStockInfo[i].get(Ebitda)<0: # if EV <=0 and EBITDA<0 for stock
            totalScores[i]=0.5
    #Note: if a stock has EV>0 and EBITDA<0, it will receive the minimum score of zero because its score is initially set to zero and it will not have its score changed

    if len(enterpriseToEbitdaValues)>1: # provided there is atleast two stocks with positive values for EV/EBITDA
        validScores=normalisePoints(enterpriseToEbitdaValues, invert) # get scores for stocks with positive EV/EBITDA
        for i in range(len(validScores)): # loop for each stock with positive EV/EBITDA
            totalScores[validIndexes[i]]+=validScores[i] #allocate score awarded to each stock with positive EV/EBITDA
    elif len(enterpriseToEbitdaValues)==1: # if there is only one stock with positive EV/EBITDA
            totalScores[validIndexes[0]]=0.5 # give the stock with the positive EV/EBITDA 0.5 points

    return totalScores

        
#getting the points for each stock based on their EV/R values     
def evToRevenueScore(allStockInfo, enterpriseToRevenue, enterpriseValue, invert):
    enterpriseToRevenueValues=[]
    validIndexes=[]
    totalScores=[0]*len(allStockInfo) # initially set each stock's score to zero
    
    for i in range(len(allStockInfo)): # loop for each stock
        if allStockInfo[i].get(enterpriseValue)>0 : # if EV>0 for stock
            enterpriseToRevenueValues.append(allStockInfo[i].get(enterpriseToRevenue)) # store EV/R for stock
            validIndexes.append(i)  # store position of stock in allStockInfo
        else: # if EV<=0 for stock
            totalScores[i]+=1 # give stock the maximum score

    if len(enterpriseToRevenueValues)>1: # provided there is atleast two stocks with positive values for EV/R
        validScores=normalisePoints(enterpriseToRevenueValues, invert) # get scores for stocks with positive EV/R
        for i in range(len(validScores)): # loop for each stock with positive EV/R
            totalScores[validIndexes[i]]=validScores[i] #allocate score awarded to each stock with positive EV/R
    elif len(enterpriseToRevenueValues)==1: # if there is only one stock with positive EV/R
        totalScores[validIndexes[0]]=0.5 # give the stock with the positive EV/R 0.5 points
        
    return totalScores


#Get the scores for each stock based on their P/FCF values. This function is similar to peAndPsScores function except calculation of P/FCF is completed
def priceToFcf(allStockInfo, marketCap, freeCashflow, invert):
    truePointAllocation=[0]*len(allStockInfo) # initially set each stock's score to zero
    fcfValues=[]
    validIndexes=[]

    for i in range(len(allStockInfo)): # loop for each stock
        if allStockInfo[i].get(freeCashflow)>0: # if fcf is positive
            fcfValues.append(allStockInfo[i].get(marketCap)/allStockInfo[i].get(freeCashflow)) #store the value of p/fcf for the stock
            validIndexes.append(i) # store the position of the stock in allStockInfo
        #Note: if a stock has a non-positive fcf, it will receive the minimum score because its score is initially set to zero and it will not have its score changed

    if len(fcfValues)>1: # provided there is atleast two stocks with positive fcf
        proxyPointAllocation=normalisePoints(fcfValues, invert) # get scores for the stocks with positive fcf
        for i in range(len(validIndexes)): # loop for each stock with positive fcf
            truePointAllocation[validIndexes[i]]=proxyPointAllocation[i] # allocate score for each stock with positive fcf
    elif len(fcfValues)==1: # if there is only one stock with positive P/FCF
        truePointAllocation[validIndexes[0]]=0.5 #give the stock with positive P/FCF 0.5 points
        
    return truePointAllocation


#get the points for each stock based on their CFO/totalDebt values
def cfoToDebt(allStockInfo, operatingCashflow, totalDebt, invert):
    truePointAllocation=[0]*len(allStockInfo) # initially set each stock's score to zero
    cfoToDebtValues=[]
    validIndexes=[]

    for y in range(len(allStockInfo)): # loop for each stock
        if allStockInfo[y].get(totalDebt)>0: # if totaldebt!=0 for stock
            cfoToDebtValues.append(allStockInfo[y].get(operatingCashflow)/allStockInfo[y].get(totalDebt)) # store cfo/debt for stock
            validIndexes.append(y) # store position of stock in allStockInfo
        else: # if totaldebt=0 for stock
            if allStockInfo[y].get(operatingCashflow)>0: # if the stock has positive CFO
                truePointAllocation[y]=1 # stock receives 1 point
                #note: if the stock has non-positive CFO and zero total debt, it receives the minimum score of zero.
            
            
    if len(validIndexes)>1: # if atleast two stocks have a valid CFO/totalDebt   
        proxyPointAllocation=normalisePoints(cfoToDebtValues, invert) # get scores for each stock with valid CFO/totalDebt
        for i in range(len(validIndexes)): # loop for each stock with valid CFO/totalDebt
            truePointAllocation[validIndexes[i]]=proxyPointAllocation[i] # allocate scores for stocks with valid CFO/totalDebt
    elif len(validIndexes)==1: #if exactly one stock has valid CFO/totalDebt
        truePointAllocation[validIndexes[0]]=0.5 # allocate stock with valid CFO/totalDebt 0.5 points
        
    return truePointAllocation


#This function is used to get the points for each stock based on their EPS growth values
def epsGrowth(allStockInfo, forwardEps, trailingEps, invert):
    truePointAllocation=[0]*len(allStockInfo) # initially set each stock's score to zero
    epsGrowthValues=[]
    validIndexes=[]
    
    for i in range(len(allStockInfo)): # loop for each stock
        if allStockInfo[i].get(trailingEps)!=0: # if trailingEPS is not zero for the stock
            epsGrowthValues.append((allStockInfo[i].get(forwardEps)-allStockInfo[i].get(trailingEps))/abs(allStockInfo[i].get(trailingEps))) #get the EPS growth for the stock
            validIndexes.append(i) # store the position of the stock in allStockInfo
        else: # if trailingEPS is zero for the stock
            if allStockInfo[i].get(forwardEps)>0: # if the stock has positive forecast EPS
                truePointAllocation[i]=1 # give the stock 1 point
                #note: if the stock has non-positive forecast EPS and zero trailing EPS, it will be given the minimum score of zero.

    if len(validIndexes)>1: # if atleast two stocks have a valid EPS growth    
        proxyPointAllocation=normalisePoints(epsGrowthValues, invert) # get scores for each stock with valid EPS growth
        for i in range(len(validIndexes)): # loop for each stock with valid EPS growth
            truePointAllocation[validIndexes[i]]=proxyPointAllocation[i] # allocate scores for stocks with valid EPS growth
    elif len(validIndexes)==1: #if exactly one stock has valid EPS growth
        truePointAllocation[validIndexes[0]]=0.5 # allocate stock with valid EPS growth 0.5 points
   
    return truePointAllocation


#getting the points for each stock based on the proximity of its current share price to its peak over the last year
def proxToHighScore(allStockInfo, previousClose, fiftyTwoWeekHigh, invert):
    proximityValues=[]
    
    for y in range(len(allStockInfo)): # loop for each stock
        proximityValues.append(allStockInfo[y].get(previousClose)/allStockInfo[y].get(fiftyTwoWeekHigh)) # store ratio of previous closing price to 52-week peak price for each stock
        
    truePointAllocation=normalisePoints(proximityValues, invert) # get points for each stock based on how their proximity to 52-week high values compare
    
    return truePointAllocation


#get the scores for each stock based on their current ratio values
def currentRatioScore(allStockInfo, currentRatio):
    currentRatioScores=[0]*len(allStockInfo) # initially set each stock's score to zero
    currentRatioValues=[]
   
    for i in range(len(allStockInfo)): # loop for each stock
        currentRatioValues.append(allStockInfo[i].get(currentRatio)) # store the stock's current ratio

    medianCurrentRatio=statistics.median(currentRatioValues) # get the median current ratio across the stocks

    for i in range(len(allStockInfo)): # loop for each stock
        if currentRatioValues[i]<(medianCurrentRatio*0.5) or currentRatioValues[i]>(medianCurrentRatio*2.5): # if the stock's current ratio is less than half of the median or more than 250% of the median
            currentRatioScores[i]-=0.5 # stock loses 0.5 points

    return currentRatioScores
    
    
#the stocks for which 50DMA>200DMA are awarded 0.5 points
def signalScore(allStockInfo, fiftyDayAverage, twoHundredDayAverage):
    signalScores=[0]*len(allStockInfo)
   
    for i in range(len(allStockInfo)): # loop for each stock
        if allStockInfo[i].get(fiftyDayAverage)>allStockInfo[i].get(twoHundredDayAverage): # if the 50DMA for the stock is above the 200DMA
            signalScores[i]+=0.5 # award 0.5 points to stock
            
    return signalScores


#for each investing approach, get and display the 1224 ranking based on the final stock scores 
def displayResults(finalScores, approach, stocks):
    print(f"\nThe screener ranking for the {approach} approach to investing is:") # inform user which investing approach this ranking is associated with
    stockDictionary={}
    
    rankedScores=sorted(finalScores, reverse=True) # sort the final stock scores for the investing approach from highest to lowest 
    roundedRankedScores=[round(r,4) for r in rankedScores] #round each final ranked score to 4dp to increase the chances of a draw

    for i in range(len(finalScores)): # loop for each stock
        stockDictionary[stocks[i]]=roundedRankedScores.index(round(finalScores[i],4))+1 # store in a dictionary the stock name and associated rank. Since .index() retrieves the first occurence of the final score in roundedRankedScores, 1224 ranking is applied in the event of a draw

    stocksSorted=sorted(stockDictionary, key=stockDictionary.get) # create an array where the order of the stocks corresponds to the ranking order, not accounting for draws
    results={s: stockDictionary[s] for s in stocksSorted} #create a new dictionary which stores stock tickers as keys in the same order as stocksSorted. The rank for each stock is stored alongside its ticker. The rank is taken from 'stockDictionary' to ensure 1224 ranking is applied in the event of a draw
    resultsFormatted=pd.Series(results) # create a pandas Series where each index is a stock ticker, each corresponding value is the stock rank, and the position of the tickers in the Series aligns with their ranking
    print(resultsFormatted, "\n") # display the pandas Series created




#main
oldStocks=["AAPL","MSFT","NVDA","INTC","ORCL","AVGO","AMD","QCOM","TXN","ADBE",'CRM',"TSM","MU","NOW","ADSK","ASML"]
startProgram()
finalStockScoresImproving, finalStockScoresValue, stocks=getScores(oldStocks)
displayToUser(finalStockScoresImproving, finalStockScoresValue, stocks)


