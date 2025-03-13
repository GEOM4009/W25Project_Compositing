# -*- coding: utf-8 -*-
"""
Created on Thu Feb 27  2025
Modified on Wed Mar 12 2025

@author: 
"""


from statistics import stdev

#printStatus = True
#gridSpacing = 5000
#numSamples = 500


def makeGrid(sampleBand,lineSpace,cellSize):
    grid= {}
    
    # Get spatial data
    
    aoiHeight = len(sampleBand)*cellSize
    aoiWidth = len(sampleBand[0])*cellSize
    
    
    
    grdHorzLns = []
    for lnHeight in range(0,aoiHeight,lineSpace):
        grdHorzLns.append(lnHeight)
    
    grdVertLns = []
    for lnDist in range(0,aoiWidth,lineSpace):
        grdVertLns.append(lnDist)
    
    grid["lineSpace"]=lineSpace
    grid["horzLns"]=grdHorzLns
    grid["vertLns"]=grdVertLns
    grid["cPoinOffset"]=lineSpace/2
    
    
    return grid


def grabRegionStats(imageLayer, x, y, rSize):
    halfRSize = rSize//2
    values=[]
    valSum = 0
    cellCount = 0
    for i in range(0-halfRSize,halfRSize,1):
        if i+y >= len(imageLayer):
            break
        for j in range(0-halfRSize,halfRSize,1):
            if j+x >= len(imageLayer[0]):
                break
            values.append(imageLayer[i+y][j+x])
            valSum+=imageLayer[i+y][j+x]
            cellCount+=1
    
    stDiv = stdev(values)
    mean = valSum/cellCount
    cv = stDiv/mean
    
    return cv
        


def getStatsGrid(bandGroup, grid, cellSize):
    stats = {
        "Mins": [],
        "Maxs": [],
        "StDivs": [],
        "Vals": [],
        "CoeffVars": []
        }

    rowIndexG = 0 
    
    #gridToCell = grid["lineSpace"]/cellSize
    
    while rowIndexG < len(grid["horzLns"]):
        rowIndexR = (rowIndexG * grid["lineSpace"] + grid["cPoinOffset"]) //cellSize
        if rowIndexR >= len(bandGroup[0]):
            break
        cvRow = []
        rowMins = []
        rowMaxs = []
        rowVals = []
        rowStDivs = []
        colIndexG = 0
        while colIndexG < len(grid["vertLns"]):
            colIndexR = (colIndexG * grid["lineSpace"] + grid["cPoinOffset"]) //cellSize
            if colIndexR >= len(bandGroup[0][0]):
                break
            cvCell = []
            cellVals=[]
            for layer in bandGroup:
                cellVals.append(layer[rowIndexR,colIndexR])
                cvCell.append(grabRegionStats(layer, colIndexR, rowIndexR, REGION_SIZE))
            
            cvRow.append(cvCell)
            rowVals.append(cellVals)
            rowMins.append(min(cellVals))
            rowMaxs.append(max(cellVals))
            rowStDivs.append(stdev(cellVals))
        
        stats["Mins"].append(rowMins)
        stats["Maxs"].append(rowMaxs)
        stats["StDivs"].append(rowStDivs)
        stats["Vals"].append(rowVals)
        stats["CoeffVars"].append(cvRow)
    
    return stats


def gridStats(sortedBands,lineSpace):
    REGION_SIZE = 5

    cellSizes = {
        "B01": 20,
        "B02": 10,
        "B03": 10,
        "B04": 10,
        "B05": 20,
        "B08": 10,
        "B11": 20,
        "B12": 20,
        }
    
    
    grid = makeGrid(sortedBands["B01"][0], lineSpace,cellSizes["B01"])
    bandStats={}
    for bandKey in sortedBands:
        bandStats[bandKey] = getStatsGrid(sortedBands[bandKey], grid, cellSizes[bandKey])
    
    return bandStats
    
    
    
    
