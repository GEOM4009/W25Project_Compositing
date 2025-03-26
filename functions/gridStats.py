# -*- coding: utf-8 -*-
"""
Created on Thu Feb 27  2025
Last Modified on Wed Mar 26 2025 5PM

@author: 
"""


from statistics import stdev
#import numpy as np
import numpy.ma as ma

printStatus = True
#gridSpacing = 5000
#numSamples = 500
REGION_SIZE = 9

cellSizes = {
    "B01": 60,
    "B02": 10,
    "B03": 10,
    "B04": 10,
    "B05": 20,
    "B08": 10,
    "B11": 20,
    "B12": 20,
    }

def makeGrid(sampleBand,lineSpace,cellSize):
    grid= {}
    
    # Get spatial data
    
    aoiHeight = len(sampleBand)*cellSize
    aoiWidth = len(sampleBand[0])*cellSize
    
    if printStatus: print("aoiHeight ",aoiHeight,", aoiWidth ",aoiWidth, end=', ')
    
    
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
    values= []

    
    for i in range(0-halfRSize,halfRSize,1):
        if i+y >= len(imageLayer):
            break
        for j in range(0-halfRSize,halfRSize,1):
            if j+x >= len(imageLayer[0]):
                break
            if (not imageLayer[i+y][j+x] is ma.masked):
                ma.append(values, imageLayer[i+y][j+x])

    if(len(values)<2): return None
    mean = values.mean()
    if (mean==0): return None  
    stDiv = stdev(values)
    cv = stDiv/mean
    
    return cv
        


def getStatsGrid(bandGroup, grid, cellSize):
    stats = {
        "Mins": ma.array([]),
        "Maxs": ma.array([]),
        "StDivs": ma.array([]),
        "Vals": ma.array([]),
        "CoeffVars": ma.array([]),
        "NumValidVals": []
    }
    maskedDummy = ma.array([0],mask=[1])
    rowIndexG = 0 
    
    #gridToCell = grid["lineSpace"]/cellSize
    
    while rowIndexG < len(grid["horzLns"]):
        rowIndexR =int( (rowIndexG * grid["lineSpace"] + grid["cPoinOffset"]) 
                       //cellSize )
        if rowIndexR >= len(bandGroup[0]):
            break
        if printStatus: print("row ",rowIndexG+1,sep="", end=', ')
        cvRow = ma.array([])
        rowMins = ma.array([])
        rowMaxs = ma.array([])
        rowVals = ma.array([])
        rowStDivs = ma.array([])
        rNumValid = []
        colIndexG = 0
        while colIndexG < len(grid["vertLns"]):
            colIndexR = int( (colIndexG * grid["lineSpace"] + grid["cPoinOffset"]) 
                            //cellSize )
            if colIndexR >= len(bandGroup[0][0]):
                break
            
            cvCell = ma.array([])
            cellVals=ma.array([])
            #validCellVals =[]
            cNumValid =0
            for layer in bandGroup:
                if (not layer[rowIndexR][colIndexR] is ma.masked):
                    cellVal= ma.array([layer[rowIndexR][colIndexR]],mask=[0]) 
                    #validCellVals =validCellVals.append(cellVal[0])
                else: cellVal= ma.array([layer[rowIndexR][colIndexR]],mask=[1]) 
                cellVals=ma.append(cellVals,cellVal)
                cv = grabRegionStats(layer, colIndexR, rowIndexR, REGION_SIZE)
                if (cv==None):
                    cvma = maskedDummy
                else:
                    cvma = ma.array([cv],[0])
                cvCell=ma.append(cvCell, cvma)
                cNumValid +=1 
                
            
            cvRow= ma.append(cvRow,cvCell)
            rowVals = ma.append(rowVals,cellVals)
            rNumValid.append(cNumValid)
            if (cNumValid>1):
                rowMaxs = ma.append(rowMaxs,max(cellVals))
                rowMins = ma.append(rowMins,min(cellVals))
                if(cNumValid>2):
                    rowStDivs = ma.append(rowStDivs, stdev(cellVals))
                else:
                    rowStDivs = ma.append(rowStDivs, maskedDummy)
            else:
                rowMaxs = ma.append(rowMaxs,maskedDummy)
                rowMins = ma.append(rowMins,maskedDummy)
                rowStDivs = ma.append(rowStDivs, maskedDummy)
            colIndexG +=1
        
        stats["Mins"] = ma.append(stats["Mins"],rowMins)
        stats["Maxs"] = ma.append(stats["Maxs"],rowMaxs)
        stats["StDivs"] = ma.append(stats["StDivs"],rowStDivs)
        stats["Vals"] = ma.append(stats["Vals"],rowVals)
        stats["CoeffVars"] = ma.append(stats["CoeffVars"],cvRow)
        stats["NumValidVals"].append(rNumValid)
        rowIndexG +=1
    
    return stats


def gridStats(sortedBands,lineSpace):
    if printStatus: print("making grid")
    grid = makeGrid(sortedBands["B01"][0], lineSpace,cellSizes["B01"])
    bandStats={}
    for bandKey in sortedBands:
        if printStatus: print("\nlooking at ",bandKey)
        bandStats[bandKey] = getStatsGrid(sortedBands[bandKey], grid, cellSizes[bandKey])
    
    return bandStats
    
    
    
    
