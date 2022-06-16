"""HFNLPpy_hopfieldGraphDraw.py

# Author:
Richard Bruce Baxter - Copyright (c) 2020-2022 Baxter AI (baxterai.com)

# License:
MIT License

# Installation:
see HFNLPpy_main.py

# Usage:
see HFNLPpy_main.py

# Description:
ATNLP Hopfield Graph Draw Class

"""

import networkx as nx
import matplotlib.pyplot as plt
from math import cos, sin, radians
from HFNLPpy_hopfieldNodeClass import *
from HFNLPpy_hopfieldConnectionClass import *

drawHopfieldGraphEdgeColoursWeights = True
drawHopfieldGraphNodeColours = False	#node colours not yet coded (pos type of concept node will be different depending on connectivity/instance context)
graphTransparency = 0.5

hopfieldGraph = nx.MultiDiGraph()	#Directed graphs with self loops and parallel edges	#https://networkx.org/documentation/stable/reference/classes/multidigraph.html
hopfieldGraphNodeColorMap = []
hopfieldGraphRadius = 100
hopfieldGraphCentre = [0, 0]

def setColourHopfieldNodes(value):
    global drawHopfieldGraphNodeColours
    drawHopfieldGraphNodeColours = value

def clearHopfieldGraph():
	hopfieldGraph.clear()	#only draw graph for single sentence
	if(drawHopfieldGraphNodeColours):
		hopfieldGraphNodeColorMap.clear()

def drawHopfieldGraphNode(node, networkSize, sentenceIndex=0):
	colorHtml = "NA"	#node colours yet coded (pos type of node will be different depending on connectivity/instance context)
	hopfieldGraphAngle = node.networkIndex/networkSize*360
	#print("hopfieldGraphAngle = ", hopfieldGraphAngle)
	posX, posY = pointOnCircle(hopfieldGraphRadius, hopfieldGraphAngle, hopfieldGraphCentre)	#generate circular graph
	hopfieldGraph.add_node(node.nodeName, pos=(posX, posY))
	if(drawHopfieldGraphNodeColours):
		hopfieldGraphNodeColorMap.append(colorHtml)

def drawHopfieldGraphConnection(connection):
	node1 = connection.nodeSource
	node2 = connection.nodeTarget
	spatioTemporalIndex = connection.spatioTemporalIndex
	if(drawHopfieldGraphEdgeColoursWeights):
		if(connection.biologicalPrototype):
			if(connection.contextConnection):
				color = 'blue'
			else:
				color = 'red'
			weight = connection.weight
		else:
			color = 'red'
			weight = 1.0
		hopfieldGraph.add_edge(node1.nodeName, node2.nodeName, color=color, weight=weight)	#FUTURE: consider setting color based on spatioTemporalIndex
	else:
		hopfieldGraph.add_edge(node1.nodeName, node2.nodeName)
	

def displayHopfieldGraph():
	pos = nx.get_node_attributes(hopfieldGraph, 'pos')
	if(drawHopfieldGraphEdgeColoursWeights):
		edges = hopfieldGraph.edges()
		#colors = [hopfieldGraph[u][v]['color'] for u,v in edges]
		#weights = [hopfieldGraph[u][v]['weight'] for u,v in edges]	
		colors = nx.get_edge_attributes(hopfieldGraph,'color').values()
		weights = nx.get_edge_attributes(hopfieldGraph,'weight').values()
		if(drawHopfieldGraphNodeColours):
			nx.draw(hopfieldGraph, pos, with_labels=True, alpha=graphTransparency, node_color=hopfieldGraphNodeColorMap, edge_color=colors, width=list(weights))
		else:
			nx.draw(hopfieldGraph, pos, with_labels=True, alpha=graphTransparency, edge_color=colors, width=list(weights))
	else:
		if(drawHopfieldGraphNodeColours):
			nx.draw(hopfieldGraph, pos, with_labels=True, alpha=graphTransparency, node_color=hopfieldGraphNodeColorMap)
		else:
			nx.draw(hopfieldGraph, pos, with_labels=True, alpha=graphTransparency)
	plt.show()

def drawHopfieldGraphNodeAndConnections(hopfieldGraphNode, networkSize, drawGraph=False):	
	#parse tree and generate nodes and connections
	drawHopfieldGraphNode(hopfieldGraphNode, networkSize)
	#for connection in hopfieldGraphNode.targetConnectionList:
	for connectionKey, connectionList in hopfieldGraphNode.targetConnectionDict.items():
		for connection in connectionList:
			drawHopfieldGraphConnection(connection)

def drawHopfieldGraphNetwork(networkConceptNodeDict):	
	#generate nodes and connections
	networkSize = len(networkConceptNodeDict)
	for conceptNodeKey, conceptNode in networkConceptNodeDict.items():
	#for conceptNode in conceptNodeList:
		#print("conceptNode.lemma = ", conceptNode.lemma)
		drawHopfieldGraphNodeAndConnections(conceptNode, networkSize, drawGraph=True)

def pointOnCircle(radius, angleDegrees, centre=[0,0]):
	angle = radians(angleDegrees)
	x = centre[0] + (radius * cos(angle))
	y = centre[1] + (radius * sin(angle))
	return x, y
	
