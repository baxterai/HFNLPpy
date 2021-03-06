"""HFNLPpy_biologicalSimulation.py

# Author:
Richard Bruce Baxter - Copyright (c) 2022 Baxter AI (baxterai.com)

# License:
MIT License

# Installation:
see HFNLPpy_main.py

# Usage:
see HFNLPpy_main.py

# Description:
HFNLP Biological Simulation - simulate training/inference of biological hopfield graph/network based on textual input

pseudo code;
for every time step/concept neuron (word w):
	for every branch in dendriticTree (2+, recursively parsed from outer to inner; sequentially dependent):
		for every sequential segment in branch (1+, sequentially dependent):
			for every non-sequential synapse (input) in segment (1+, sequentially independent):
				calculate local dendritic activation
					subject to readiness (repolarisation time at dendrite location)
	calculate neuron activation
		subject to readiness (repolarisation time)

training;
	activate concept neurons in order of sentence word order
	strengthen those synapses which directly precede/contribute to firing
		weaken those that do not
	this will enable neuron to fire when specific contextual instances are experienced
inference;
	calculate neuron firing exclusively from prior/contextual subsequence detections

"""


import numpy as np

from HFNLPpy_hopfieldNodeClass import *
from HFNLPpy_hopfieldConnectionClass import *
from HFNLPpy_biologicalSimulationGlobalDefs import *
from HFNLPpy_biologicalSimulationNode import *
import HFNLPpy_biologicalSimulationGenerate
if(vectoriseComputation):
	import HFNLPpy_biologicalSimulationPropagateVectorised
else:
	import HFNLPpy_biologicalSimulationPropagateStandard
import HFNLPpy_biologicalSimulationDraw

printVerbose = False


#alwaysAddPredictionInputFromPreviousConcept = False
#if(vectoriseComputation):
#	alwaysAddPredictionInputFromPreviousConcept = True #ensures that simulateBiologicalHFnetworkSequenceNodePropagateParallel:conceptNeuronBatchIndexFound



def seedBiologicalHFnetwork(networkConceptNodeDict, sentenceIndex, targetSentenceConceptNodeList, numberOfSentences):
	
	connectionTargetNeuronSet = set()	#for posthoc network deactivation
	if(not seedHFnetworkSubsequenceBasic):
		conceptNeuronSourceList = []

	for wSource in range(len(targetSentenceConceptNodeList)-1):
		wTarget = wSource+1
		conceptNeuronSource = targetSentenceConceptNodeList[wSource]
		conceptNeuronTarget = targetSentenceConceptNodeList[wTarget]
		print("seedBiologicalHFnetwork: wSource = ", wSource, ", conceptNeuronSource = ", conceptNeuronSource.nodeName, ", wTarget = ", wTarget, ", conceptNeuronTarget = ", conceptNeuronTarget.nodeName)
		
		if(seedHFnetworkSubsequenceBasic):
			activationTime = calculateActivationTimeSequence(wSource)
			somaActivationFound = simulateBiologicalHFnetworkSequenceNodePropagateForward(networkConceptNodeDict, sentenceIndex, targetSentenceConceptNodeList, wTarget, conceptNeuronTarget, activationTime, wSource, conceptNeuronSource, connectionTargetNeuronSet)
		else:
			connectionTargetNeuronSetLocal = set()
			activationTime = calculateActivationTimeSequence(wSource)
			if(wSource < seedHFnetworkSubsequenceLength):
				somaActivationFound = simulateBiologicalHFnetworkSequenceNodePropagateForward(networkConceptNodeDict, sentenceIndex, targetSentenceConceptNodeList, wTarget, conceptNeuronTarget, activationTime, wSource, conceptNeuronSource, connectionTargetNeuronSetLocal)
			else:
				somaActivationFound = simulateBiologicalHFnetworkSequenceNodesPropagateForward(networkConceptNodeDict, sentenceIndex, targetSentenceConceptNodeList, wTarget, conceptNeuronTarget, activationTime, wSource, conceptNeuronSourceList, connectionTargetNeuronSetLocal)
			
			conceptNeuronSourceList.clear()
			for connectionTargetNeuron in connectionTargetNeuronSetLocal:
				if(connectionTargetNeuron.activationLevel):
					#print("conceptNeuronSourceList.append connectionTargetNeuron = ", connectionTargetNeuron.nodeName)
					conceptNeuronSourceList.append(connectionTargetNeuron)
			connectionTargetNeuronSet = connectionTargetNeuronSet.union(connectionTargetNeuronSetLocal)
			resetConnectionTargetNeurons(connectionTargetNeuronSetLocal, True, conceptNeuronTarget)	

		expectPredictiveSequenceToBeFound = False
		if(enforceMinimumEncodedSequenceLength):
			if(wSource >= minimumEncodedSequenceLength-1):
				expectPredictiveSequenceToBeFound = True
		else:
			expectPredictiveSequenceToBeFound = True
		if(expectPredictiveSequenceToBeFound):
			if(somaActivationFound):
				#if(printVerbose):
				print("somaActivationFound")
			else:
				#if(printVerbose):
				print("!somaActivationFound: HFNLP algorithm error detected")
		else:
			print("!expectPredictiveSequenceToBeFound: wSource < minimumEncodedSequenceLength-1")
			
	resetConnectionTargetNeurons(connectionTargetNeuronSet, False)

	HFNLPpy_biologicalSimulationDraw.drawBiologicalSimulationStatic(networkConceptNodeDict, sentenceIndex, targetSentenceConceptNodeList, numberOfSentences)

def verifySeedSentenceIsReplicant(articles, numberOfSentences):
	result = False
	if(seedHFnetworkSubsequenceVerifySeedSentenceIsReplicant):
		seedSentence = articles[numberOfSentences-1]
		for sentenceIndex in range(numberOfSentences-1):
			sentence = articles[sentenceIndex]
			if(compareSentenceStrings(seedSentence, sentence)):
				result = True
		if(not result):
			print("verifySeedSentenceIsReplicant warning: seedSentence (last sentence in dataset) was not found eariler in dataset (sentences which are being trained)")
	return result
	
def compareSentenceStrings(sentence1, sentence2):
	result = True
	if(len(sentence1) == len(sentence2)):
		for wordIndex in range(len(sentence1)):
			word1 = sentence1[wordIndex]
			word2 = sentence1[wordIndex]
			if(word1 != word2):
				result = False
	else:
		result = False	
	return result
	

def trainBiologicalHFnetwork(networkConceptNodeDict, sentenceIndex, sentenceConceptNodeList, numberOfSentences):
	simulateBiologicalHFnetworkSequenceTrain(networkConceptNodeDict, sentenceIndex, sentenceConceptNodeList, numberOfSentences)	


#if (!biologicalSimulation:useDependencyParseTree):

def simulateBiologicalHFnetworkSequenceTrain(networkConceptNodeDict, sentenceIndex, sentenceConceptNodeList, numberOfSentences):

	#cannot clear now as HFNLPpy_biologicalSimulationDrawSentence/HFNLPpy_biologicalSimulationDrawNetwork memory structure is not independent (diagnose reason for this);
	
	sentenceLength = len(sentenceConceptNodeList)
	
	connectionTargetNeuronSet = set()	#for posthoc network deactivation
	
	for wTarget in range(1, sentenceLength):	#wTarget>=1: do not create (recursive) connection from conceptNode to conceptNode branchIndex1=0
		conceptNeuronTarget = sentenceConceptNodeList[wTarget]
		
		connectionTargetNeuronSetLocal = set()
		somaActivationFound = simulateBiologicalHFnetworkSequenceNodePropagateWrapper(networkConceptNodeDict, sentenceIndex, sentenceConceptNodeList, wTarget, connectionTargetNeuronSetLocal)
		
		connectionTargetNeuronSet = connectionTargetNeuronSet.union(connectionTargetNeuronSetLocal)
		resetConnectionTargetNeurons(connectionTargetNeuronSetLocal, True, conceptNeuronTarget)	
						
		if(somaActivationFound):
			#if(printVerbose):
			print("somaActivationFound")
		else:
			#if(printVerbose):
			print("!somaActivationFound: ", end='')
			predictiveSequenceLength = wTarget	#wSource+1
			dendriticBranchMaxW = wTarget-1
			expectFurtherSubbranches = True
			if(wTarget == 1):
				expectFurtherSubbranches = False
			
			addPredictiveSequenceToNeuron = False
			if(enforceMinimumEncodedSequenceLength):
				if(dendriticBranchMaxW+1 >= minimumEncodedSequenceLength):
					addPredictiveSequenceToNeuron = True
			else:
				addPredictiveSequenceToNeuron = True
			if(addPredictiveSequenceToNeuron):
				print("addPredictiveSequenceToNeuron")
				HFNLPpy_biologicalSimulationGenerate.addPredictiveSequenceToNeuron(conceptNeuronTarget, sentenceIndex, sentenceConceptNodeList, conceptNeuronTarget.dendriticTree, predictiveSequenceLength, dendriticBranchMaxW, 0, 0, expectFurtherSubbranches)
			else:
				print("")	#add new line
				
	#reset dendritic trees
	resetConnectionTargetNeurons(connectionTargetNeuronSet, False)

	HFNLPpy_biologicalSimulationDraw.drawBiologicalSimulationStatic(networkConceptNodeDict, sentenceIndex, sentenceConceptNodeList, numberOfSentences)

			
def simulateBiologicalHFnetworkSequenceNodePropagateWrapper(networkConceptNodeDict, sentenceIndex, sentenceConceptNodeList, wTarget, connectionTargetNeuronSet):
	somaActivationFound = False
	if(biologicalSimulationForward):
		wSource = wTarget-1
		conceptNeuronSource = sentenceConceptNodeList[wSource]
		conceptNeuronTarget = sentenceConceptNodeList[wTarget]
		activationTime = calculateActivationTimeSequence(wSource)
		somaActivationFound = simulateBiologicalHFnetworkSequenceNodePropagateForward(networkConceptNodeDict, sentenceIndex, sentenceConceptNodeList, wTarget, conceptNeuronTarget, activationTime, wSource, conceptNeuronSource, connectionTargetNeuronSet)
	else:
		conceptNeuronTarget = sentenceConceptNodeList[wTarget]
		somaActivationFound = simulateBiologicalHFnetworkSequenceNodePropagateReverseLookup(networkConceptNodeDict, sentenceIndex, sentenceConceptNodeList, wTarget, conceptNeuronTarget)
	
	return somaActivationFound


def simulateBiologicalHFnetworkSequenceNodePropagateForward(networkConceptNodeDict, sentenceIndex, sentenceConceptNodeList, wTarget, conceptNeuronTarget, activationTime, wSource, conceptNeuronSource, connectionTargetNeuronSet):
	print("simulateBiologicalHFnetworkSequenceNodePropagateForward: wSource = ", wSource, ", conceptNeuronSource = ", conceptNeuronSource.nodeName, ", wTarget = ", wTarget, ", conceptNeuronTarget = ", conceptNeuronTarget.nodeName)	
	if(vectoriseComputationCurrentDendriticInput):
		somaActivationFound = HFNLPpy_biologicalSimulationPropagateVectorised.simulateBiologicalHFnetworkSequenceNodePropagateParallel(networkConceptNodeDict, sentenceIndex, sentenceConceptNodeList, activationTime, wSource, conceptNeuronSource, wTarget, conceptNeuronTarget, connectionTargetNeuronSet)
	else:
		if(emulateVectorisedComputationOrder):
			somaActivationFound = HFNLPpy_biologicalSimulationPropagateStandard.simulateBiologicalHFnetworkSequenceNodePropagateStandardEmulateVectorisedComputationOrder(networkConceptNodeDict, sentenceIndex, sentenceConceptNodeList, activationTime, wSource, conceptNeuronSource, wTarget, conceptNeuronTarget, connectionTargetNeuronSet)					
		else:
			somaActivationFound = HFNLPpy_biologicalSimulationPropagateStandard.simulateBiologicalHFnetworkSequenceNodePropagateStandard(networkConceptNodeDict, sentenceIndex, sentenceConceptNodeList, activationTime, wSource, conceptNeuronSource, wTarget, conceptNeuronTarget, connectionTargetNeuronSet)			
	return somaActivationFound

def simulateBiologicalHFnetworkSequenceNodesPropagateForward(networkConceptNodeDict, sentenceIndex, sentenceConceptNodeList, wTarget, conceptNeuronTarget, activationTime, wSource, conceptNeuronSourceList, connectionTargetNeuronSet):
	if(vectoriseComputationCurrentDendriticInput):
		somaActivationFound = HFNLPpy_biologicalSimulationPropagateVectorised.simulateBiologicalHFnetworkSequenceNodesPropagateParallel(networkConceptNodeDict, sentenceIndex, sentenceConceptNodeList, activationTime, wSource, conceptNeuronSourceList, wTarget, conceptNeuronTarget, connectionTargetNeuronSet)
	else:
		if(emulateVectorisedComputationOrder):
			somaActivationFound = HFNLPpy_biologicalSimulationPropagateStandard.simulateBiologicalHFnetworkSequenceNodesPropagateStandardEmulateVectorisedComputationOrder(networkConceptNodeDict, sentenceIndex, sentenceConceptNodeList, activationTime, wSource, conceptNeuronSourceList, wTarget, conceptNeuronTarget, connectionTargetNeuronSet)				
		else:
			somaActivationFound = HFNLPpy_biologicalSimulationPropagateStandard.simulateBiologicalHFnetworkSequenceNodesPropagateStandard(networkConceptNodeDict, sentenceIndex, sentenceConceptNodeList, activationTime, wSource, conceptNeuronSourceList, wTarget, conceptNeuronTarget, connectionTargetNeuronSet)			
	return somaActivationFound
	
def simulateBiologicalHFnetworkSequenceNodePropagateReverseLookup(networkConceptNodeDict, sentenceIndex, sentenceConceptNodeList, wTarget, conceptNeuronTarget):
	somaActivationFound = HFNLPpy_biologicalSimulationPropagateStandard.simulateBiologicalHFnetworkSequenceNodePropagateReverseLookup(networkConceptNodeDict, sentenceIndex, sentenceConceptNodeList, wTarget, conceptNeuronTarget)
	return somaActivationFound
	
#independent method (does not need to be executed in order of wSource)
def simulateBiologicalHFnetworkSequenceNodePropagateForwardFull(networkConceptNodeDict, sentenceIndex, sentenceConceptNodeList, wTarget, conceptNeuronTarget):
	somaActivationFound = False
	connectionTargetNeuronSet = set()	#for posthoc network deactivation
	
	for wSource, conceptNeuronSource in enumerate(sentenceConceptNodeList):	#support for simulateBiologicalHFnetworkSequenceSyntacticalBranchDPTrain:!biologicalSimulationEncodeSyntaxInDendriticBranchStructureFormat
	#orig for wSource in range(0, wTarget):
		conceptNeuronSource = sentenceConceptNodeList[wSource]
		activationTime = calculateActivationTimeSequence(wSource)
		
		connectionTargetNeuronSetLocal = set()
		somaActivationFoundTemp = simulateBiologicalHFnetworkSequenceNodePropagateForward(networkConceptNodeDict, sentenceIndex, sentenceConceptNodeList, wTarget, conceptNeuronTarget, activationTime, wSource, conceptNeuronSource, connectionTargetNeuronSetLocal)
		
		if(wSource == len(sentenceConceptNodeList)-1):
			if(somaActivationFoundTemp):
				somaActivationFound = True
		
		connectionTargetNeuronSet = connectionTargetNeuronSet.union(connectionTargetNeuronSetLocal)
		resetConnectionTargetNeurons(connectionTargetNeuronSetLocal, True, conceptNeuronTarget)
	
	resetConnectionTargetNeurons(connectionTargetNeuronSet, False)
		
	return somaActivationFound

	
			
			
