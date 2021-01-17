import json
import datetime
import pandas as pd
import matplotlib.pyplot as plt
import scipy.interpolate as intp
import numpy as np
from matplotlib import cm

if __name__ == '__main__':

    f = open("result.json", "r")

    text = f.read()

    text = text.replace("۱", "1")\
        .replace("۲", "2")\
        .replace("۳", "3")\
        .replace("۴", "4")\
        .replace("۵", "5")\
        .replace("۶", "6")\
        .replace("۷", "7")\
        .replace("۸", "8")\
        .replace("۹", "9")\
        .replace("۰", "0")

    textJson = json.loads(text)

    messageNumByDateDict = {}

    firstDate = None
    gotFirstDate = False
    lastDate = None

    # for message in textJson['messages']:
    #     if 'actor' in message:
    #         if message['action'] == 'invite_members' or \
    #                 message['action'] == 'remove_members' or \
    #                 message['action'] == 'join_group_by_link':
    #             print(message)

    for message in textJson['messages']:
        lastDate = datetime.datetime.fromisoformat(message['date']).date()

        if not gotFirstDate:
            firstDate = lastDate
            gotFirstDate = True

        if "from" in message:
            user = message['from']
        else:
            user = message['actor']

        if user in messageNumByDateDict:
            if lastDate in messageNumByDateDict[user]:
                messageNumByDateDict[user][lastDate] += 1
            else:
                messageNumByDateDict[user][lastDate] = 1
        else:
            messageNumByDateDict[user] = {}
            messageNumByDateDict[user][lastDate] = 1

    allDates = [firstDate + datetime.timedelta(x) for x in range((lastDate - firstDate).days + 1)]

    for user in messageNumByDateDict:
        for date in allDates:
            if date not in messageNumByDateDict[user]:
                messageNumByDateDict[user][date] = 0
        messageNumByDateDict[user] = {key: messageNumByDateDict[user][key] for key in sorted(messageNumByDateDict[user])}

    # print(messageNumByDateDict)

    data = {'Date': allDates}
    for user in messageNumByDateDict:
        data[user] = [messageNumByDateDict[user][entry] for entry in messageNumByDateDict[user]]

    df = pd.DataFrame(data)

    with open('Analysis.csv', 'w') as f:
        df.to_csv(f)

    interpolationCoeff = 10
    x = [i for i in range(len(allDates))]
    xNew = np.linspace(0, len(allDates) - 1, interpolationCoeff * (len(allDates) - 1))

    groupActivityPlot = plt
    y = []
    for index, row in df.iterrows():
        totalMessages = sum(row[1:])
        y.append(totalMessages)

    windowSize = 14
    pdYNew = pd.Series(y)
    window = pdYNew.rolling(windowSize)
    movingAverage = window.mean()
    movingAverageList = movingAverage.tolist()
    yMvg = movingAverageList[windowSize - 1:]
    xMvg = [i for i in range(len(yMvg))]
    xMvgNew = np.linspace(0, len(xMvg) - 1, interpolationCoeff * (len(xMvg) - 1))

    yNew = intp.pchip_interpolate(x, y, xNew)
    yMvgNew = intp.pchip_interpolate(xMvg, yMvg, xMvgNew)

    # groupActivityPlot.plot(xNew, yNew)
    step = np.ceil(len(xMvg) / 10)
    tickLocs = [int(i) for i in np.arange(0, xMvg[-1], step)]
    tickLabels = [allDates[i + windowSize - 1] for i in tickLocs]

    groupActivityPlot.xticks(tickLocs, tickLabels, rotation=45)
    # print(len(xMvgNew))
    # print(tickLocs)
    # print(tickLabels)
    groupActivityPlot.grid()
    groupActivityPlot.plot(xMvgNew, yMvgNew)
    groupActivityPlot.show()

    userActivityPlot = plt
    for column in df.columns:
        if column != "Date":
            name = column
            y = list(df[column])
            yNew = intp.pchip_interpolate(x, y, xNew)
            groupActivityPlot.plot(xNew, yNew)

    # activityPlot.get_cmap(cm.get_cmap("Sequential"))
    # activityPlot.xticks(range(), ['a', 'a', 'a', 'a', 'a'])
    userActivityPlot.legend(list(df.columns[1:]))
    userActivityPlot.show()

    for column in df.columns:
        if column != "Date":
            name = column
            y = list(df[column])
            yNew = intp.pchip_interpolate(x, y, xNew)

            plt.plot(xNew, yNew)
            plt.title(column)
            plt.grid()
            plt.show()