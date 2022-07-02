"""HFNLPpy_biologicalSimulationPropagateStandard.py

# Author:
Richard Bruce Baxter - Copyright (c) 2020-2022 Baxter AI (baxterai.com)

# License:
MIT License

# Installation:
see HFNLPpy_main.py

# Usage:
see HFNLPpy_main.py

# Description:
HFNLP Biological Simulation Propagate Standard

"""


import numpy as np

from HFNLPpy_hopfieldNodeClass import *
from HFNLPpy_hopfieldConnectionClass import *
from HFNLPpy_biologicalSimulationNode import *


printVerbose = False

#if(biologicalSimulationForward):	#required for drawBiologicalSimulationDendriticTreeSentenceDynamic/drawBiologicalSimulationDendriticTreeNetworkDynamic?
drawBiologicalSimulationDynamic = False	#draw dynamic activation levels of biological simulation
if(drawBiologicalSimulationDynamic):
	drawBiologicalSimulationDynamicPlot = True	#default: False
	drawBiologicalSimulationDynamicSave = False	#default: True	#save to file
	drawBiologicalSimulationDendriticTreeSentenceDynamic = True	#default: True	#draw graph for sentence neurons and their dendritic tree
	if(drawBiologicalSimulationDendriticTreeSentenceDynamic):
		import HFNLPpy_biologicalSimulationDraw as HFNLPpy_biologicalSimulationDrawSentenceDynamic
	drawBiologicalSimulationDendriticTreeNetworkDynamic = False	#default: True	#draw graph for entire network (not just sentence)
	if(drawBiologicalSimulationDendriticTreeNetworkDynamic):
		import HFNLPpy_biologicalSimulationDraw as HFNLPpy_biologicalSimulationDrawNetworkDynamic


def simulateBiologicalHFnetworkSequenceNodePropagateStandard(networkConceptNodeDict, sentenceIndex, sentenceConceptNodeList, activationTime, wSource, conceptNeuronSource, w, conceptNeuron, connectionTargetNeuronSet):

	#if(printVerbose):
	print("simulateBiologicalHFnetworkSequenceNodePropagateStandard: wSource = ", wSource, ", conceptNeuronSource = ", conceptNeuronSource.nodeName)
			
	somaActivationFound = False	#is conceptNeuronTarget activated by its prior context?
	conceptNeuronSource.activationLevel = objectAreaActivationLevelOn
	
	for targetConnectionConceptName, connectionList in conceptNeuronSource.targetConnectionDict.items():
		conceptNeuronTarget = networkConceptNodeDict[targetConnectionConceptName] #or connectionList[ANY].nodeTarget
		connectionTargetNeuronSet.add(conceptNeuronTarget)
		for connection in connectionList:
			connection.activationLevel = objectAreaActivationLevelOn
			if(calculateNeuronActivationStandard(connection, 0, conceptNeuronTarget.dendriticTree, activationTime, wSource, networkConceptNodeDict, sentenceIndex, sentenceConceptNodeList)[0]):
				if(conceptNeuronTarget == conceptNeuron):
					somaActivationFound = True
				conceptNeuronTarget.activationLevel = objectAreaActivationLevelOn

			drawBiologicalSimulationDynamicNeuronActivation(wSource, networkConceptNodeDict, sentenceIndex, sentenceConceptNodeList)	
	
	resetAxonsActivation(conceptNeuronSource)
	if(resetWsourceNeuronDendriteAfterActivation):
		resetDendriticTreeActivation(conceptNeuronSource)
			
	return somaActivationFound
	
	
#orig method;
def simulateBiologicalHFnetworkSequenceNodePropagateReverseLookup(networkConceptNodeDict, sentenceIndex, sentenceConceptNodeList, w, conceptNeuron):

	#if(printVerbose):
	print("simulateBiologicalHFnetworkSequenceNodePropagateReverseLookup: w = ", w, ", conceptNeuron = ", conceptNeuron.nodeName)
	
	somaActivationFound = False	#is conceptNeuron activated by its prior context?
	
	#support for simulateBiologicalHFnetworkSequenceSyntacticalBranchDPTrain:!biologicalSimulationEncodeSyntaxInDendriticBranchStructure
	for wSource, conceptNeuronSource in enumerate(sentenceConceptNodeList):
	#orig: for wSource in range(0, w):
		#conceptNeuronSource = sentenceConceptNodeList[wSource]	#source neuron
		activationTime = calculateActivationTimeSequence(wSource)
		if(simulateBiologicalHFnetworkSequenceNodeTrainPropagateSpecificTarget(networkConceptNodeDict, sentenceIndex, sentenceConceptNodeList, activationTime, wSource, conceptNeuronSource, w, conceptNeuron)):
			somaActivationFound = True
			
	resetDendriticTreeActivation(conceptNeuron)
	
	return somaActivationFound

#only calculateNeuronActivation for specific target
#parameters only used for drawBiologicalSimulationDynamic: wSource, w
def simulateBiologicalHFnetworkSequenceNodeTrainPropagateSpecificTarget(networkConceptNodeDict, sentenceIndex, sentenceConceptNodeList, activationTime, wSource, conceptNeuronSource, w, conceptNeuron):

	somaActivationFound = False
	
	#if(printVerbose):
	#print("simulateBiologicalHFnetworkSequenceNodeTrainPropagateSpecificTarget: w = ", w, ", conceptNeuron = ", conceptNeuron.nodeName)

	if(conceptNeuron.nodeName in conceptNeuronSource.targetConnectionDict):
		conceptNeuronSource.activationLevel = objectAreaActivationLevelOn
		connectionList = conceptNeuronSource.targetConnectionDict[conceptNeuron.nodeName]	#only trace connections between source neuron and target neuron
		for connection in connectionList:
			connection.activationLevel = objectAreaActivationLevelOn
			targetNeuron = connection.nodeTarget	#targetNeuron will be the same for all connection in connectionList (if targetConnectionConceptName == conceptNeuron)
			if(targetNeuron != conceptNeuron):
				print("simulateBiologicalHFnetworkSequenceNodeTrainPropagateSpecificTarget error: (targetNeuron != conceptNeuron)")
				exit()

			if(calculateNeuronActivationStandard(connection, 0, targetNeuron.dendriticTree, activationTime, wSource, networkConceptNodeDict, sentenceIndex, sentenceConceptNodeList)[0]):
				somaActivationFound = True
				targetNeuron.activationLevel = objectAreaActivationLevelOn
				#if(printVerbose):
				#print("somaActivationFound")

			drawBiologicalSimulationDynamicNeuronActivation(wSource, networkConceptNodeDict, sentenceIndex, sentenceConceptNodeList)	

		resetAxonsActivationConnectionList(connectionList)
		conceptNeuronSource.activationLevel = objectAreaActivationLevelOff
			
	return somaActivationFound
					
										

#parameters only used for drawBiologicalSimulationDynamic: wSource, networkConceptNodeDict, sentenceIndex, sentenceConceptNodeList
def calculateNeuronActivationStandard(connection, currentBranchIndex1, currentBranch, activationTime, wSource=None, networkConceptNodeDict=None, sentenceIndex=None, sentenceConceptNodeList=None):
	
	connection.activationLevel = objectAreaActivationLevelOn
	
	#activationFound = False
	targetConceptNeuron = connection.nodeTarget
		
	#calculate subbranch activations:
	subbranchesActive = objectAreaActivationLevelOff
	subbranchesActivationTimeMax = minimumActivationTime
	if(len(currentBranch.subbranches) > 0):
		if(performSummationOfSequentialSegmentInputsAcrossBranch):
			branch2activationSum = 0.0		
		else:
			numberOfBranch2active = 0
		for subbranch in currentBranch.subbranches:	
			subbranchActive = False
			subbranchActiveLevel, subbranchActivationTime = calculateNeuronActivationStandard(connection, currentBranchIndex1+1, subbranch, activationTime, wSource, networkConceptNodeDict, sentenceIndex, sentenceConceptNodeList)
			if(performSummationOfSequentialSegmentInputsAcrossBranch):
				if(subbranchActiveLevel > objectLocalActivationLevelOff):
					subbranchActive = objectAreaActivationLevelOn
					branch2activationSum = branch2activationSum + subbranchActiveLevel
			else:
				if(subbranchActiveLevel):
					subbranchActive = objectAreaActivationLevelOn
					numberOfBranch2active += 1
			if(subbranchActive):
				if(subbranchActivationTime > subbranchesActivationTimeMax):
					subbranchesActivationTimeMax = subbranchActivationTime
		if(performSummationOfSequentialSegmentInputsAcrossBranch):
			#print("Subbranches: currentBranchIndex1 = ", currentBranchIndex1, ", connection.nodeTarget = ", connection.nodeTarget.nodeName, ", connection.nodeSource = ", connection.nodeSource.nodeName, ", branch2activationSum = ", branch2activationSum, ", subbranchesActivationTimeMax = ", subbranchesActivationTimeMax, ", activationTime = ", activationTime)
			if(branch2activationSum >= numberOfHorizontalSubBranchesRequiredForActivation):
				subbranchesActive = objectAreaActivationLevelOn
		else:
			if(numberOfBranch2active >= numberOfHorizontalSubBranchesRequiredForActivation):	#must conform with branch merge method *
				subbranchesActive = objectAreaActivationLevelOn
	else:
		subbranchesActive = objectAreaActivationLevelOn
		#subbranchesActivationTimeMax = 0
		
	sequentialSegmentActivationLevelPrior = objectLocalActivationLevelOff
	sequentialSegmentActivationStatePrior = subbranchesActive	#initialise prior sequential segment activation state to subbranchesActive
	sequentialSegmentActivationTimePrior = subbranchesActivationTimeMax
	
	for currentSequentialSegmentIndex, currentSequentialSegment in reversed(list(enumerate(currentBranch.sequentialSegments))):
		if((currentBranchIndex1 > 0) or expectFirstBranchSequentialSegmentConnection):
			#calculate branch segment activations:

			sequentialSegmentActivationState = objectAreaActivationLevelOff
			sequentialSegmentActivationLevel = objectLocalActivationLevelOff	#current activation level
			sequentialSegmentActivationTime = None	#current activation time

			sequentialSegmentAlreadyActive = False
			if(sequentialSegmentActivationLevelAboveZero(currentSequentialSegment.activationLevel)):	#required to ensure currentSequentialSegment.activationTime is valid
				#if(not(sequentialSegmentActivationStatePrior) or verifySequentialActivationTime(currentSequentialSegment.activationTime, sequentialSegmentActivationTimePrior)):	#ignore existing activation level if it occured at an earlier/same time than/as sequentialSegmentActivationTimePrior	#this test should not be required with preventReactivationOfSequentialSegments
				if(calculateSequentialSegmentActivationState(currentSequentialSegment.activationLevel)):
					sequentialSegmentAlreadyActive = True
					sequentialSegmentActivationState = objectAreaActivationLevelOn
				sequentialSegmentActivationLevel = currentSequentialSegment.activationLevel
				sequentialSegmentActivationTime = currentSequentialSegment.activationTime

			if(not preventReactivationOfSequentialSegments or not sequentialSegmentAlreadyActive):
				foundConnectionSynapse, currentSequentialSegmentInput = findConnectionSynapseInSequentialSegment(currentSequentialSegment, connection)
				if(foundConnectionSynapse):
					inputActivationLevel = calculateInputActivationLevel(connection)
					if(recordSequentialSegmentInputActivationLevels):
						currentSequentialSegmentInput.activationLevel = inputActivationLevel
						currentSequentialSegmentInput.activationTime = activationTime
					if(printVerbose):
						printIndentation(currentBranchIndex1+1)
						print("activate currentSequentialSegmentInput, connection.nodeSource = ", connection.nodeSource.nodeName, ", connection.nodeTarget = ", connection.nodeTarget.nodeName)

					passSegmentActivationTimeTests = False
					if(currentSequentialSegmentInput.firstInputInSequence):
						#print("passSegmentActivationTimeTests")
						passSegmentActivationTimeTests = True	#if input corresponds to first in sequence, then enforce no previous dendritic activation requirements
					else:
						if(sequentialSegmentActivationStatePrior):	#previous sequential segment/subbranch was activated		#only accept sequential segment activation if previous was activated
							if(verifySequentialActivationTime(activationTime, sequentialSegmentActivationTimePrior)):	#ignore existing activation level if it occured at an earlier/same time than/as sequentialSegmentActivationTimePrior
								#if(verifyRepolarised(currentSequentialSegment, activationTime)):	#ensure that the segment isnt in a repolarisation state (ie it can be activated)
								passSegmentActivationTimeTests = True	#sequentialSegmentActivationLevel implies subbranchesActive: previous (ie more distal) branch was active

					if(passSegmentActivationTimeTests):
						if(performSummationOfSequentialSegmentInputs):
							sequentialSegmentActivationLevel = sequentialSegmentActivationLevel + inputActivationLevel
							sequentialSegmentActivationTime = activationTime	#CHECKTHIS: always record latest activation time for sequential segment activation
							sequentialSegmentActivationState = calculateSequentialSegmentActivationState(sequentialSegmentActivationLevel)
						else:
							#printIndentation(currentBranchIndex1+1)
							#print("passSegmentActivationTimeTests: activate currentSequentialSegmentInput, connection.nodeSource = ", connection.nodeSource.nodeName, ", connection.nodeTarget = ", connection.nodeTarget.nodeName, ", inputActivationLevel = ", inputActivationLevel, ", activationTime = ", activationTime)
							sequentialSegmentActivationLevel = inputActivationLevel
							sequentialSegmentActivationTime = activationTime
							sequentialSegmentActivationState = objectAreaActivationLevelOn
						currentSequentialSegment.activationLevel = sequentialSegmentActivationLevel
						currentSequentialSegment.activationTime = sequentialSegmentActivationTime

						drawBiologicalSimulationDynamicSequentialSegmentActivation(wSource, networkConceptNodeDict, sentenceIndex, sentenceConceptNodeList, currentBranchIndex1, currentSequentialSegmentIndex)
		else:
			sequentialSegmentActivationState = sequentialSegmentActivationStatePrior
			sequentialSegmentActivationLevel = calculateSequentialSegmentActivationState(sequentialSegmentActivationState)
			sequentialSegmentActivationTime = sequentialSegmentActivationTimePrior
			currentSequentialSegment.activationLevel = sequentialSegmentActivationLevel
			currentSequentialSegment.activationTime = sequentialSegmentActivationTime

		sequentialSegmentActivationLevelPrior = sequentialSegmentActivationLevel		
		sequentialSegmentActivationStatePrior = sequentialSegmentActivationState
		sequentialSegmentActivationTimePrior = sequentialSegmentActivationTime

	#	print("branch: currentBranchIndex1 = ", currentBranchIndex1, ", connection.nodeTarget = ", connection.nodeTarget.nodeName, ", connection.nodeSource = ", connection.nodeSource.nodeName, ", sequentialSegmentActivationLevelPrior = ", sequentialSegmentActivationLevelPrior)

	if(performSummationOfSequentialSegmentInputsAcrossBranch):
		branchActivationLevel = sequentialSegmentActivationLevelPrior
	else:
		branchActivationLevel = sequentialSegmentActivationStatePrior	#activate branch2	#activate whole currentSequentialSegment
	branchActivationTime = sequentialSegmentActivationTimePrior
	currentBranch.activationLevel = branchActivationLevel
	currentBranch.activationTime = branchActivationTime
	#sequentialSegmentsActive = True

	if(branchActivationLevel):
		if(printVerbose):
			printIndentation(currentBranchIndex1+1)
			print("branchActivationLevel: activate currentBranch, connection.nodeSource = ", connection.nodeSource.nodeName, ", connection.nodeTarget = ", connection.nodeTarget.nodeName)
			#print("activationFound")
	return branchActivationLevel, branchActivationTime							
	
def findConnectionSynapseInSequentialSegment(currentSequentialSegment, connection):
	foundConnectionSynapse = False
	currentSequentialSegmentInput = None
	if(preventGenerationOfDuplicateConnections):
		foundSequentialSegmentInput, currentSequentialSegmentInput = findSequentialSegmentInputBySourceNode(currentSequentialSegment, connection.nodeSource)
		#if(connection.nodeSource.nodeName in currentSequentialSegment.inputs):
		#	currentSequentialSegmentInput = currentSequentialSegment.inputs[connection.nodeSource.nodeName]
		if(foundSequentialSegmentInput):
			if(connection.nodeTargetSequentialSegmentInput == currentSequentialSegmentInput):
				foundConnectionSynapse = True
	else:
		#for currentSequentialSegmentInputTest in currentSequentialSegment.inputs:
		for currentSequentialSegmentInputTest in currentSequentialSegment.inputs.values():
			if(connection.nodeTargetSequentialSegmentInput == currentSequentialSegmentInputTest):
				#print("foundConnectionSynapse")
				foundConnectionSynapse = True
				currentSequentialSegmentInput = currentSequentialSegmentInputTest
	return foundConnectionSynapse, currentSequentialSegmentInput	
	
def drawBiologicalSimulationDynamicSequentialSegmentActivation(wSource, networkConceptNodeDict, sentenceIndex, sentenceConceptNodeList, branchIndex1, sequentialSegmentIndex):
	if(drawBiologicalSimulationDynamic):
		#if(sentenceIndex == 3):	#temp debug requirement	#and wTarget==15
		if(drawBiologicalSimulationDendriticTreeSentenceDynamic):
			fileName = generateBiologicalSimulationDynamicFileName(True, wSource, branchIndex1, sequentialSegmentIndex, sentenceIndex)
			HFNLPpy_biologicalSimulationDrawSentenceDynamic.clearHopfieldGraph()
			HFNLPpy_biologicalSimulationDrawSentenceDynamic.drawHopfieldGraphSentence(sentenceConceptNodeList)
			HFNLPpy_biologicalSimulationDrawSentenceDynamic.displayHopfieldGraph(drawBiologicalSimulationDynamicPlot, drawBiologicalSimulationDynamicSave, fileName)
		if(drawBiologicalSimulationDendriticTreeNetworkDynamic):
			fileName = generateBiologicalSimulationDynamicFileName(False, wSource, branchIndex1, sequentialSegmentIndex, sentenceIndex)
			HFNLPpy_biologicalSimulationDrawNetworkDynamic.clearHopfieldGraph()
			HFNLPpy_biologicalSimulationDrawNetworkDynamic.drawHopfieldGraphNetwork(networkConceptNodeDict)
			HFNLPpy_biologicalSimulationDrawNetworkDynamic.displayHopfieldGraph(drawBiologicalSimulationDynamicPlot, drawBiologicalSimulationDynamicSave, fileName)				

def drawBiologicalSimulationDynamicNeuronActivation(wSource, networkConceptNodeDict, sentenceIndex, sentenceConceptNodeList):
	if(drawBiologicalSimulationDynamic):
		#if(sentenceIndex == 3):	#temp debug requirement	#and wTarget==15
		if(drawBiologicalSimulationDendriticTreeSentenceDynamic):
			fileName = generateBiologicalSimulationFileName(True, wSource, sentenceIndex)
			HFNLPpy_biologicalSimulationDrawSentenceDynamic.clearHopfieldGraph()
			HFNLPpy_biologicalSimulationDrawSentenceDynamic.drawHopfieldGraphSentence(sentenceConceptNodeList)
			HFNLPpy_biologicalSimulationDrawSentenceDynamic.displayHopfieldGraph(drawBiologicalSimulationDynamicPlot, drawBiologicalSimulationDynamicSave, fileName)
		if(drawBiologicalSimulationDendriticTreeNetworkDynamic):
			generateBiologicalSimulationFileName(False, wSource, sentenceIndex)
			HFNLPpy_biologicalSimulationDrawNetworkDynamic.clearHopfieldGraph()
			HFNLPpy_biologicalSimulationDrawNetworkDynamic.drawHopfieldGraphNetwork(networkConceptNodeDict)
			HFNLPpy_biologicalSimulationDrawNetworkDynamic.displayHopfieldGraph(drawBiologicalSimulationDynamicPlot, drawBiologicalSimulationDynamicSave, fileName)	
			