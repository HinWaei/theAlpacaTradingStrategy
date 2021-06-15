'''
A demo of the Alpaca trading strategies
@author Hinux Chau
@date 12 Jun 2021
'''

import json
import datetime
import random
#------------------------------------------------------------
def dbg(content:str):
    print(content)
    exit()

def getSingleKeyFromDict(stockDict:dict)->str:
    return ''.join([key for key in stockDict.keys()])

def readJson(filePath:str)->dict:
    with open(filePath,"r+") as f:
        jsonData:dict = json.load(f)
    return jsonData
#------------------------------------------------------------
def date(dateString:str)->datetime:
    return datetime.datetime.strptime(dateString,"%Y-%m-%d")

#The *end* is not included
#Only one stock can be queried
def returnDataWithinDays(Sheet:dict,stockNumber:str,start:str,end:str)->list:
    #get the list of the stocks numbers
    aYearList = list()
    end = date(end)
    for stock in Sheet:
        if stockNumber == stock['Stkcd'] and date(stock["Trddt"])>=date(start) and date(stock["Trddt"])<=end:
            aYearList.append({
                "date":stock["Trddt"],
                "benefit":str(stock["benefit"]),
            })
        else:
            continue
    return aYearList

def getKeySet(Sheet:dict)->list:
    stockNumberSet = set()
    for stock in Sheet:
        stockNumberSet.add(stock['Stkcd'])
    '''with open("stockNumber.txt","w+") as f:
        json.dump(obj=list(stockNumberSet),fp=f)'''
    return list(stockNumberSet)

def dbgWriteFileInJSON(filePath:str,jsonObj:dict):
    with open(filePath,"w+") as f:
        json.dump(obj=jsonObj,fp=f)
    exit()

def convertListOfItemsToDict(d:list)->dict:
    tmpd = {}
    for item in d:
        tmpd[item[0]] = item[1]
    return tmpd

def kickAndPurchase(stockNumber:str,sortedYourShares:list,pool:dict)->dict:
    tmpSortedYourShares = convertListOfItemsToDict(sortedYourShares)
    
    if sortedYourShares.__len__()!=10:
        print(f"[KICK_AND_PURCHASE] ERR:{sortedYourShares.__len__()}")
        exit()
    #sync poolKeyList to avoid repeated purchase
    poolKeyList=[poolKey for poolKey in pool.keys()]
    
    #Kick    
    shitStock = sortedYourShares.pop()
    tmpSortedYourShares.pop(shitStock[0])
    print(f"[KICK_AND_PURCHASE] {shitStock} has been popped")
    print(f"[KICK] sortedYourShares:{sortedYourShares.__len__()} remaining, tmpSortedYourShares:{tmpSortedYourShares.__len__()} remaining")
    #sync pool
    poolPreviousLen=pool.__len__()
    pool[shitStockNumber] = shitStock[1]
    print(f"[KICK_AND_PURCHASE] Previous pool:{poolPreviousLen}, Current pool:{pool.__len__()}")
    
    
    #Purchase
    while True:
        random.seed(datetime.datetime.now())
        index = int(random.random()*poolKeyList.__len__())
        keyName = poolKeyList[index]
        stockBenefit:float = pool[keyName]
        if (keyName,stockBenefit) not in sortedYourShares:
            sortedYourShares.append((keyName,stockBenefit))
            tmpSortedYourShares[keyName] = stockBenefit                     #purchase
            pool.pop(keyName)
            break      

    print(f"*[PURCHASE] {keyName} purchased!")
    #sync poolKeyList
    poolKeyList=[poolKey for poolKey in pool.keys()]
    print(f"[PURCHASE] sortedYourShares:{sortedYourShares.__len__()} remaining, tmpSortedYourShares:{tmpSortedYourShares.__len__()} remaining")
    print(f"[OKAY] pool remaining:{pool.__len__()}. poolKeyList remaining:{poolKeyList.__len__()}")
    return sorted(tmpSortedYourShares.items(),key=lambda x:float(x[1]),reverse=True)

def averageBenefitEveryDay(sortedYourShares:list)->float:
    averageBenefit:float = 0
    for i in sortedYourShares:
        averageBenefit += float(i[1])
    return averageBenefit/sortedYourShares.__len__()

def updatePoolAndYourShares(Sheet:dict,day:int,start:str,end:str,sortedYourShares:list,pool:dict):
    tmpSortedYourShares = convertListOfItemsToDict(sortedYourShares)

    poolKeyList:list = getKeySet(Sheet)
    print(f"[INIT_POOL] Initializing poolKeyList:{poolKeyList.__len__()}")
    for keyName in poolKeyList:
        keyData = returnDataWithinDays(Sheet,keyName,start,end)
        if keyData.__len__()>day:
            if keyName not in tmpSortedYourShares:
                pool[keyName]=keyData[day]['benefit']
        else:
            print(f"*[POOL_UPDATE] {keyName} is invalid")
    
    poolKeyList = [poolKey for poolKey in pool]             #sync poolKeyList
    print(f"[POOL_UPDATE] poolKeyList:{poolKeyList.__len__()} pool:{pool.__len__()}\n")

    #update the packet
    c = 0
    for yourShare in sortedYourShares:
        yourShareKey = yourShare[0]                                 #('60000','-0.5535')
        yourShareData = returnDataWithinDays(Sheet,yourShareKey,start,end)
        today = str(date(start)+datetime.timedelta(days=day)).rsplit(' ')[0]
        for benefitData in yourShareData:
            if benefitData['date'] == today:
                sortedYourShares[c] = (yourShareKey,benefitData['benefit'])
                break
        c+=1
    sortedYourShares.sort(key=lambda x:float(x[1]),reverse=True)
    print(f"[POOL_UPDATE] There are {poolKeyList.__len__()} remaining\n")

    return pool,sortedYourShares


if __name__ == "__main__":

    # Input the Interval
    interval = input("Pls input the interval(days):")
    start = input("Start from (example:2016-06-15):")
    end = input("End on (example:2017-06-14):")
    # useless_上证50成分股日度数据.json    上证50成分股日度收益率.json  上证50日度数据.json
    # The days calculated by subtracting start from end
    if not start or not end or not interval:
        start = "2016-06-15"
        end = "2017-06-14"
        interval = "3"
    days = (date(end)-date(start)).days+1

    # Read Json Data from the given json files
    jsonData = readJson("上证50成分股日度收益率.json")
    Sheet = jsonData['Sheet2']
    
    # Initialize the pool
    poolKeyList:list = getKeySet(Sheet)
    print(f"[INIT_POOL] Initializing poolKeyList:{poolKeyList.__len__()}")
    pool = {}
    for keyName in poolKeyList:
        keyData = returnDataWithinDays(Sheet,keyName,start,end)
        if keyData.__len__()>1 and keyData[0]['date']==start:
            pool[keyName]=keyData[0]['benefit']
        else:
            print(f"*[POOL_UPDATE] {keyName} is invalid")
    
    poolKeyList = [poolKey for poolKey in pool]             #sync poolKeyList
    print(f"[POOL_UPDATE] poolKeyList:{poolKeyList.__len__()} pool:{pool.__len__()}\n")
    #dbgWriteFileInJSON("stocksInOneYear.txt",pool)
        
    # Purchase 10 stocks randomly as the initial ones
    yourShares = dict()
    random.seed(datetime.datetime.now())
    count = 10
    while count:
        index = int(random.random()*poolKeyList.__len__())

        keyName = poolKeyList[index]
        if keyName in pool.keys():
            stockBenefit:float = pool[keyName]
            yourShares[keyName] = stockBenefit                     #purchase
            pool.pop(keyName)
            poolKeyList.remove(keyName)
            print(f"*[PURCHASE] {keyName} purchased!")
            count-=1
        else:
            poolKeyList.remove(keyName)
    
    print(f"[OKAY] pool remaining:{pool.__len__()}. poolKeyList remaining:{poolKeyList.__len__()}")
    sortedYourShares:list=sorted(yourShares.items(),key=lambda x:float(x[1]),reverse=True)

    yourSharesSum:float = 0
    poolSumEveryday:float = 0
    poolAverage:float = 0
    for day in range(0,days):
        # Calculate the accumulated profit of them for each day
        # ----------------------------------------------------
        yourSharesEverydayAverageBenefit:float = averageBenefitEveryDay(sortedYourShares)
        yourSharesSum += yourSharesEverydayAverageBenefit
        for item in pool:
            poolSumEveryday += float(pool[item])
        poolAverageEveryday = poolSumEveryday/pool.__len__()
        difference = yourSharesEverydayAverageBenefit - poolAverageEveryday
        print(f"""
        [SUM] the averageBenefitEveryDay of your shares:    {round(yourSharesEverydayAverageBenefit,6)}
        [SUM] the SUM of your shares:    {round(yourSharesSum,6)}
        [SUM] the difference between averageBenefitEveryday and poolAverage:    {round(difference,6)}
        """)
        # ----------------------------------------------------
        # Calculate the profit for each stock (done) and sort them by their profits
        print(f"\n[PURCHASE] Purchased {sortedYourShares.__len__()} stocks:{sortedYourShares}\n")    
        # Randomly pick a stock from the remaining ones(i.e. the non-purchased ones) and f*ck the last one off from the pool
        shitStockNumber:str = sortedYourShares[-1][0]
        if day and not day%int(interval):
            sortedYourShares = kickAndPurchase(shitStockNumber,sortedYourShares,pool)

        # Update the pool and repeat
        today = date(start)+datetime.timedelta(days=day)
        print("\nPOOL UPDATED--------------------------------------\n")
        print(f"[update] Today is {str(today).rsplit(' ')[0]}")
        previousPool = pool.keys()
        pool,sortedYourShares = updatePoolAndYourShares(Sheet,day,start,end,sortedYourShares,pool)
        currentPool = pool.keys()
        if(previousPool.__len__() != currentPool.__len__()):
            print(f"[update] ERR: previousPoolLen and currentPoolLen is not equal!")

        addedStocks = []
        for current in currentPool:
            if current not in previousPool:
                addedStocks.append(current+" ")
        print(f"[update] {[''.join(addedStocks)]} are added")

