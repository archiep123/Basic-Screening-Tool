
## Introduction

Fundamental analysis is a common investing technique where the strength of a company’s fundamentals is used to assess whether investing today could prove profitable in the future. This approach is distinct from technical analysis, which relies on price movements to determine when to buy and sell rather than focussing on underlying company characteristics.

The following report discusses a PIP in which I coded a basic screening tool that ranks a predefined list of mega-cap tech companies based on qualities commonly associated with attractive investment opportunities. The tool predominantly uses fundamental analysis. However, the methods used to determine each company’s momentum score are more closely aligned with technical analysis.

The screener’s ranking of each company is based on the overall score it allocates to it. Each company’s overall score is composed of subcategories, and the score for each subcategory is the sum of the scores of all the metrics contributing to it. For example, health is a component of each company’s overall score, and the health score is the sum of the individual scores for the health-related metrics contributing to it.

By and large, the screener calculates the score to award for each individual metric by retrieving the metric value for each company and applying min-max normalisation to reward companies based on their relative performance. However, a small number of metrics are evaluated using threshold-based rules rather than peer comparison. Additionally, certain edge cases where peer comparison is not meaningful are handled via manual point allocation. This means that the rankings displayed by the screener should be interpreted as a combination of comparative and rule-based scoring instead of being purely based on relative performance.

###### Caveat:

It should be made clear that while the metrics used in the scoring system were chosen with the intention of filtering for potentially attractive investments, companies near the top of the ranking cannot be interpreted as those more likely to provide strong returns. Strictly, all that can be deduced from high-ranking companies is that they most closely satisfy the criteria the screener uses to identify attractive investments. Whether these criteria are valid and meet the user’s standards of rigour is up to them to decide.



## Context

#### Screener Logic:

The screener calculates a valuation, health, and momentum score for each company based on metric values pulled from Yahoo! Finance. The valuation score aims to identify cheap companies, the health score aims to identify fundamentally sound companies, and the momentum score aims to identify improving companies.

The screener applies the following basic logic: a company with a high overall score after combining the valuation and health scores may be both inexpensive and fundamentally sound. If a company is inexpensive and fundamentally sound, its cheapness could indicate undervaluation rather than a weak underlying business. A company with a high overall score after combining the valuation, health, and momentum scores may therefore be both undervalued and improving.

#### Screener Output:

The screener outputs two separate tables. The first ranks the companies based on the results from combining their valuation and health scores. The second ranks the companies after adjusting for their momentum scores. The user is then given the option to view a line graph showing the 50DMA, 200DMA, and adjusted closing price over the past trading year for a company of their choice from the ranking tables.

Note: After the user inputs the company that they would like to see a line graph for, an excel file with the graph displayed on the active page should automatically open. However, this feature is platform-dependent and implemented for Windows using os.startfile()

#### Categorisation of Outputs:

Scoring based purely on valuation and health-related metrics is described by the screener as a “Buffett-like approach” because prioritising the value and health of a company loosely aligns with Warren Buffett’s investing philosophy. However, it should be noted that the specific metrics likely to be analysed by Buffett will differ from those used by the screener to obtain the valuation and health scores. The screener adopts Buffett’s broad approach rather than its nuances.

Accounting for momentum alongside valuation and company health-related metrics is described by the screener as a “Stockopedia-like approach”. This is because focussing on value, quality, and momentum reflects the approach used by Stockopedia to create their StockRank. Viewing these three factors as key drivers of returns, Stockopedia combines them to try to find undervalued and improving companies.



## General Comments on Screener Metrics and Weighting

#### Metrics:

Certain metrics the screener uses may disproportionately benefit specific companies depending on their stage of progression and subsector. For example, EBITDA-based metrics may favour capital-intensive companies such as TSMC by excluding D&A. This can be a significant expense for businesses with large bases of depreciable or amortisable assets, leading to lower EV/EBITDA values.

The metrics used by the screener are not intended to be unbiased across all companies. Instead, the screener aims to use a broad enough range of metrics to smooth out any resulting inequalities. This is why it pulls over 25 different data points for each stock from Yahoo! Finance.

#### Weighting:

For the Buffett-like approach, the weighting of the valuation and health scores gives each valuation metric and health subsection equal influence. This weighting was chosen to benefit well-rounded companies. However, for the Stockopedia-like approach, the weighting is slightly adjusted to put more emphasis on top-line-based metrics and growth metrics relative to bottom-line-based metrics. This adjustment was made to try to reward young, expanding companies more generously, since companies at this stage typically prioritise capturing market share over cost control, meaning they will likely receive higher scores from revenue- and growth-based metrics compared to earnings-based metrics.

A scoring system which rewards young, expanding companies slightly more favourably is used for the Stockopedia-like approach on the basis that they often exhibit strong momentum, which is one of the three key factors that this approach focusses on. However, metrics assessing profitability, liquidity, and debt-servicing ability are still accounted for after the weighting is adjusted. This helps prevent companies pursuing growth at any cost from being rewarded too generously by the screener.



## Metric Insights

#### Trailing P/E, Forward P/E:

Intention: reward companies trading at low valuations relative to their current and forecast earnings. This may seem counterintuitive because a low P/E can imply that the market has low expectations for future company growth. However, when combined with strong company health (and, for the Stockopedia-like approach, current momentum), it is possible that a company has a low P/E because its growth has not yet been fully priced by the market.

#### PEG Ratio:

Intention: reward companies trading at low valuations relative to their current earnings, adjusting for expected earnings growth. Using this metric reinforces the attempt to find companies whose valuations do not yet fully reflect their growth prospects.

#### P/S, EV/R:

Intention: reward companies trading at low valuations relative to their total annual revenue. Using revenue-based metrics in addition to earnings-based metrics like P/E helps remove bias against young, growing companies that aren’t yet focussed on their bottom line.

Note: EV/R is used distinctly from P/S because it incorporates debt and cash positions to assess valuation in terms of the company’s total value, rather than just the market value of equity.

#### EV/EBITDA:

Intention: reward companies whose enterprise value is low relative to their EBITDA. When calculating EBITDA, core operating costs such as SG&A and COGS are accounted for, but financing, taxation, and D&A are not. As a result, EV/EBITDA assesses valuation relative to operating performance before the impact of depreciation and amortisation. However, as previously touched on, differences in EV/EBITDA between companies can reflect variation in the size of their depreciable or amortisable asset bases as much as differences in operating performance.

#### P/FCF:

Intention: reward companies trading at low valuations relative to their FCF. Free cash flow can be used by companies to repay debt, provide returns to shareholders, reinvest in growth, and much more. Thus, a high FCF (relative to market capitalisation) potentially indicates the company is in a strong financial position.

#### EPS Growth:

EPS measures the company earnings available to shareholders per outstanding share. Companies with high EPS growth, typically, are those which analysts expect will have a significant increase in earnings. Therefore, the EPS growth metric is used to reward companies that are forecast to have a strong earnings rise.

#### YoY Quarterly Revenue Growth, YoY Quarterly Earnings Growth:

Intention: reward companies with strong top-line and bottom-line growth relative to the same quarter last year. These metrics credit companies that are actively improving their sales performance and/or overall profitability, irrespective of prior success.

Note: YoY quarterly earnings growth is used distinctly from EPS growth since it’s rewarding current performance relative to past performance instead of expected future performance relative to current performance.

#### ROA:

Intention: reward companies with high annual net income relative to their total assets. This allows companies to be held accountable based on their asset efficiency. For example, a company requiring a very large asset base to generate substantial earnings will have a lower ROA than one achieving the same level of annual net income without relying so heavily on assets.

#### Net Profit Margins, Operating Margins:

Intention: reward companies that efficiently convert revenue into net/operating profit. The operating and net profit margins are distinct because the operating margin assesses operational profitability alone, whereas the net profit margin assesses overall profitability after financing and tax effects. Using both metrics allows companies that have strong cost control but significant non-operational expenses to be recognised for their operational efficiency while still being held accountable for overall profitability.

#### CFO/Total Debt:

Intention: reward companies whose net cash generated from operations is large relative to their total debt. Comparing CFO to total debt helps assess how well-positioned a company is to manage its debt burden based on the cash-generating ability of its operations. However, it should be noted that investment required to maintain operations, such as capital expenditure, must first be covered, and free cash flow, rather than CFO, is ultimately used to repay debt.

#### Current Ratio:

Intention: penalise companies whose current ratio is less than half or greater than 2.5 times the median. Since current ratio measures the size of current assets relative to current liabilities, it can indicate whether a company has the liquidity to comfortably meet its short-term obligations. Thus, companies with current ratios significantly below the median may have risky short-term financial positions. A company with a current ratio significantly above the median can also be a negative sign. For example, this could indicate overly conservative use of short-term financing or lack of reinvestment leading to large cash reserves.

#### Proximity to 52-Week High:

Intention: reward companies whose current price per share is high relative to their peak over the past year. This metric uses the idea that if a company’s current price per share is close to its annual peak, it may imply the company’s recent share price performance has been strong relative to its performance over the year. However, it should be recognised that companies whose share prices have been stagnant across the year will be scored highly by this metric. Likewise, a company whose recent share price performance is strong but is still recovering from a decline earlier in the year will not receive a high score using this metric despite its current momentum.

#### 1-Year Price Performance:

Intention: reward companies whose fractional change in share price over the past year is high. While this metric can help to filter for companies with strong share price performances over the past year, it should be noted that 52-week change looks solely at the share prices at the start and end of the period, meaning it does not capture price movements within the year.

#### 50DMA>200DMA:

Intention: reward companies whose 50DMA is above their 200DMA. This suggests a stronger recent share price performance (over the medium-term) relative to longer-term movement and, if sustained, may indicate future growth. The main issue with moving averages is their delayed response to changes in the short-term share price trend. However, using the 200-day average change % helps incorporate short-term share price movement into the overall momentum score.

Note: the variable storing the scores for this metric is called ‘goldenCrossScore’. This refers to the point where an upward-trending 50DMA crosses above the 200DMA, known as the golden cross. It is interpreted by some investors as a buy signal depending on the circumstances of the crossover.

#### 200-Day Average Change %:

Intention: reward companies whose current share prices are significantly above their 200DMA. This metric will generously score early breakouts, as well as more established share price trends. However, due to the lag in the moving average, it is sensitive to the current share price. Consequently, it can be vulnerable to misleading signals caused by short-term, intense current share price changes that quickly reverse.

## Program Logic Comments

Note: For the list of mega-cap tech stocks that the screener analyses, most of the edge case adjustments are unlikely to be necessary and are simply added for practice.

#### Structure of Program

The program is arranged to have functions that get user inputs, add up scores, and display results first. The functions used to calculate individual scores and analyse the results come next, separated by a large section of white space. The 'main' section at the end of the program defines the list of mega-cap tech stocks analysed by the screener and makes the function calls required for the program to run.

#### Adjusting for Negatives during Scoring System Inversion

###### Explanation of Reason for Implementation:

The valuation metrics that require the scores allocated by the min-max normalisation function to be inverted and may take negative values are PEG, P/E, EV/EBITDA, EV/R and P/FCF. Negative values break the logic used when inverting the allocated scores. For example, if a company has a negative P/E, it will receive a higher score than the company with the smallest positive P/E. However, economically, the negative P/E company is likely in a financial position closer to the company with the highest P/E, which receives the minimum score. Therefore, separate treatment of negative values is necessary in the functions used to calculate scores for these valuation metrics.

For each of these valuation metrics, the screener treats negative cases by extending the existing scoring logic. For example, the score for P/E depends on the magnitude of P and E. When E is negative, it can be treated as an extreme case of a company with very low but positive E. Such a company would likely have a very high P/E and, hence, receive a very low score. Accordingly, companies with negative E are assigned the minimum score.

It could be argued that this treatment is too lenient and that companies with negative E should receive a point deduction. In the previous example, the companies with negative E are potentially in an even weaker financial position than those with very low but positive E (which will receive the minimum or a very low score). Therefore, it is reasonable to suggest that companies with negative E should be penalised. This treatment was not applied because the score also depends on P. If penalisation were used, a company with a slightly negative E and low P would lose points relative to a company with a very low but positive E and very high P. However, based on an economic interpretation of the situation, the company with negative E is likely the more attractive valuation opportunity.

###### Breakdown of Logic for each Function’s Handling of Negatives: 
In evToRevenueScore(), the following logic is applied when handling non-positive EV/R: <br>If the ratio is non-positive, then EV is non-positive since R can be assumed positive. The ratio is treated as a very low but positive EV/R and receives the maximum score.

It should be noted that, in this case, inverting the scores allocated by the min-max normalisation function without adjustment for negatives does not completely contradict the scoring trend, unlike with the P/E. By default, the negative ratios would be allocated the highest scores, greater than those allocated to companies with the smallest positive EV/R. The main issue with this treatment, from an economic perspective, is that a negative EV/R does not always merit a higher score than a positive EV/R. For example, if a company has a slightly negative EV and very small R, it will receive more points than a company with a slightly positive EV and very large R.

However, the treatment that the screener uses instead of inverting the allocated scores without further adjustment is also flawed. Two companies with non-positive EV will both receive the maximum score of 1, even if one has a much larger R than the other.

<br>
In evToEbitdaScore(), the following logic is applied when handling non-positive EV/EBITDA:

If EV is non-positive and EBITDA is positive, then the ratio is treated as a very low EV/EBITDA and receives the maximum score. If EV is positive and EBITDA is negative, then the ratio is treated as a very high EV/EBITDA and receives the minimum score. If EV is non-positive and EBITDA is negative, then the company receives a score of 0.5 points. Manual point allocation is required in this case because the EV/EBITDA value obtained when both components are negative is not economically meaningful. Therefore, it must be ignored, leaving the company with nothing to be scored on for this metric. Awarding the company 0.5 points was viewed as a balanced score to allocate considering its relative performance under this metric cannot be assessed.

An alternative approach would be to skip scoring for companies with non-positive EV and negative EBITDA. However, this would allow other companies to receive scores that the skipped companies cannot access, placing them at a scoring disadvantage despite the absence of information suggesting they do or do not merit it.

<br>
In pegScore(), the following logic is applied when handling negative PEG:

If PEG is negative, then exactly one of earnings or expected earnings growth is negative, since the numerator can be assumed to be positive. The ratio is treated as a very high value and receives the minimum score. If PEG is positive and P/E is negative, then both earnings and expected earnings growth are negative, making the economic interpretation of the positive PEG unclear. In this case, the company receives 0.5 points. As discussed in evToEbitdaScore(), 0.5 points is considered a reasonable score to allocate to companies whose relative performance under the metric cannot be assessed.

<br>
In peAndPsScore(), the following logic is applied when handling negative P/E:

If P/E is negative, then earnings are negative, since the numerator can be assumed to be positive. The ratio is treated as a very high value and receives the minimum score.

<br>
In priceToFcfScore(), the following logic is applied when handling non-positive P/FCF:

If FCF is non-positive, then the ratio is negative or undefined, since the numerator can be assumed to be positive. The ratio is treated as a very high value and receives the minimum score.

#### Division by Zero Comments

Some metrics, like CFO/totalDebt, must be calculated by the screener using data retrieved from the stock information dictionaries whereas other metrics, like P/E and P/S, can be directly retrieved from the dictionaries. Division by zero is not accounted for in the functions which score metrics that are directly retrieved. This is because invalid calculations are typically handled upstream by the data provider, and, in response, yfinance will likely return null or missing data when this occurs. Any company missing any of the data necessary for analysis is removed before scoring begins.

In normalisePoints(), division by zero occurs when minVal equals maxVal. If this happens, the function skips the scoring calculations and assigns each company zero points for the metric. This is justified by the fact that they all have the same metric value in this case, meaning none of them has a comparative advantage.

The function proxToHighScore() awards points based on the proximity of a company’s current share price to its peak over the last year. It can safely be assumed that the peak share price over the last year for each company analysed will be non-zero, meaning the function does not need to account for division by zero.

In epsGrowth(), division by zero is handled using the technique of extending the scoring logic: <br> If trailing EPS is zero and forecast EPS is positive, the undefined EPS growth is treated as an extreme case of a company with a very small positive trailing EPS and positive forecast EPS. Such a company would likely have a very high EPS growth and, therefore, receive a high score. Accordingly, companies with zero trailing EPS and positive forecast EPS are assigned the maximum score. If trailing EPS is zero and forecast EPS is non-positive, then, applying the same idea, the undefined EPS growth is treated as a very low value and receives the minimum score.

Note: the same logic, using total debt and operating cashflow instead of trailing EPS and forecast EPS, is applied in cfoToDebt().

#### Cases with One Positive/Defined Value

In functions where division by zero or scoring system inversion is handled, invalid metric values are manually awarded points. This means they are not stored in the array passed into normalisePoints() for relative scoring. Consequently, if only one company has a valid value, normalisePoints() allocates it zero points because only one value is passed into the function. This was considered an unfair treatment of the company, so the scoring in this case was adjusted. The company now receives 0.5 points, chosen as a balanced score to allocate given that its relative performance under the metric cannot be assessed because there are no other valid values to compare it against.

#### Ranking Stocks

To obtain the final stock ranking in displayResults(), the position of the first occurrence of each rounded stock score in the sorted array ‘roundedRankedScores’ is used instead of the position of each stock in 'stocksSorted'. This ensures 1224 ranking is applied in the event of a draw.

#### Adjusted Closing Price Clarification

In displayToUser(), the code specifies 'Close' when retrieving prices for the user's chosen stock but uses 'Closing Price (adj)' to label the corresponding line on the chart. This is because newer versions of yfinance retrieve adjusted closing prices by default.

#### Absolute Values

The use of the absolute value of trailingEPS in the epsGrowth() function ensures the calculation remains usable when trailingEPS is negative.

#### Median Usage

In the currentRatioScore() function, the median is used instead of the mean to estimate the central value of the dataset. This is because there may be significant outliers across the companies’ current ratios, which would pull the mean further away from the centre of the dataset than the median.



## Addressing Potential Screener Issues

1) For certain stocks, some metrics used by the screener may be missing from their stock information dictionaries. However, the program includes measures to handle this scenario without crashing. The stocks this occurs for are identified and removed from the list of stocks analysed by the screener before scoring begins. Depending on the number of stocks with missing data, this has the potential to limit the range of different tech companies compared by the screener.
2) It is possible that issues with yfinance prevent stock information from being retrieved for any company. However, in the two months I have spent on this project, this has happened once and it didn’t last long. If this issue occurs again, the program uses a try/except block to handle it without crashing.
3) The normalised scoring system is sensitive to outliers. However, keeping the cross-company comparison within the technology sector attempts to reduce both the number and extent of outlying data.



## Results

On April 9th 2026, Micron Technology was ranked as the top stock in both of the two tables displayed. Over the following month, its share price nearly doubled.


