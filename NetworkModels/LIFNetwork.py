from __future__ import division

from NeuronNetwork import NeuronNetwork

import numpy as numpy

class LIFNetwork(NeuronNetwork):

	def __init__(self):

		NeuronNetwork.__init__(self)

		#################################
		# LIF NEURON PARAMETER VECTORS: #
		#################################
		# The following attributes are vectors that hold a list of the designated parameter values for all neurons in the network.
		# - The ith element in the vector is the value of that parameter for the ith neuron in the network.

		#--------------------------------
		# Voltage & Related parameters: -
		#--------------------------------
		self.V 				= numpy.empty(shape=[0])

		self.V_init 		= numpy.empty(shape=[0])
		self.V_thresh 		= numpy.empty(shape=[0])
		self.V_reset 		= numpy.empty(shape=[0])
		self.V_eqLeak 		= numpy.empty(shape=[0])
		self.V_eqExcit 		= numpy.empty(shape=[0])
		self.V_eqInhib 		= numpy.empty(shape=[0])

		self.R_membrane		= numpy.empty(shape=[0])

		#----------------
		# Conductances: -
		#----------------
		self.g_leak 		= numpy.empty(shape=[0])
		self.g_excit		= numpy.empty(shape=[0])
		self.g_inhib 		= numpy.empty(shape=[0])
		self.g_gap 			= numpy.empty(shape=[0])

		#------------------
		# Time constants: -
		#------------------
		self.tau_g_excit 	= numpy.empty(shape=[0])
		self.tau_g_inhib 	= numpy.empty(shape=[0])

		#------------------
		# Spiking events: -
		#------------------
		self.spikeEvents		= numpy.empty(shape=[0])

		#--------------------
		# Refractory period -
		#--------------------
		self.refracPeriod	= numpy.empty(shape=[0])
		self.timeSinceSpike	= numpy.empty(shape=[0])

		#-------------------------
		# Integration constants: -
		#-------------------------
		# Terms in the dynamics update rule of a parameter that consist of only constant parameters
		# and can be pre-calculated at initialization to save computation time in the simulation loop.
		# For LIF, different integration methods can be put in same form differing only by these constant terms,
		# which can be pre-calculated according to a specified integration method allowing for a common update expression in the sim loop.
		# (Initialized to None to raise error if used without being explicitly computed)
		self.constAlpha_g_excit	= None
		self.constBeta_g_excit	= None
		self.constAlpha_g_inhib	= None
		self.constBeta_g_inhib	= None

		
		############################
		# INPUT PARAMETER VECTORS: #
		############################
		self.inputVals 	= numpy.empty(shape=[0])

		#----------------------------
		#############################

		self.neuronLogVariables = ['neuron_id', 't', 'g_leak', 'g_excit', 'g_inhib', 'g_gap', 'V', 'spike', 'synapse_type', 'label']
		for variable in self.neuronLogVariables:
			self.neuronLogs[variable]	= {'data': None, 'enabled': True}	# The data data structure will be initialized in initialize_simulation() when numTimePoints is known.

		self.inputLogVariables = ['input_id', 't', 'input_val', 'input_type', 'label']
		for variable in self.inputLogVariables:
			self.inputLogs[variable]	= {'data': None, 'enabled': True}	# The data data structure will be initialized in initialize_simulation() when numTimePoints is known.


	def add_neurons(self, numNeuronsToAdd,
					V_init, V_thresh, V_reset, V_eqLeak, V_eqExcit, V_eqInhib, R_membrane,
					g_leak, g_excit_init, g_inhib_init, g_gap,
					tau_g_excit, tau_g_inhib, refracPeriod,
					synapse_type, label='', position=None):

		#--------------------
		# Add the given parameters for this set of neuron(s) to the network's neuron parameter vectors:
		#--------------------
		self.V 				= numpy.concatenate([self.V, [V_init for n in range(numNeuronsToAdd)]])

		self.V_init 		= numpy.concatenate([self.V_init, [V_init for n in range(numNeuronsToAdd)]])
		self.V_thresh 		= numpy.concatenate([self.V_thresh, [V_thresh for n in range(numNeuronsToAdd)]])
		self.V_reset 		= numpy.concatenate([self.V_reset, [V_reset for n in range(numNeuronsToAdd)]])
		self.V_eqLeak 		= numpy.concatenate([self.V_eqLeak, [V_eqLeak for n in range(numNeuronsToAdd)]])
		self.V_eqExcit 		= numpy.concatenate([self.V_eqExcit, [V_eqExcit for n in range(numNeuronsToAdd)]])
		self.V_eqInhib 		= numpy.concatenate([self.V_eqInhib, [V_eqInhib for n in range(numNeuronsToAdd)]])

		self.R_membrane		= numpy.concatenate([self.R_membrane, [R_membrane for n in range(numNeuronsToAdd)]])

		self.g_leak 		= numpy.concatenate([self.g_leak, [g_leak for n in range(numNeuronsToAdd)]])
		self.g_excit 		= numpy.concatenate([self.g_excit, [g_excit_init for n in range(numNeuronsToAdd)]])
		self.g_inhib 		= numpy.concatenate([self.g_inhib, [g_inhib_init for n in range(numNeuronsToAdd)]])
		self.g_gap			= numpy.concatenate([self.g_gap, [g_gap for n in range(numNeuronsToAdd)]])

		self.tau_g_excit 	= numpy.concatenate([self.tau_g_excit, [tau_g_excit for n in range(numNeuronsToAdd)]])
		self.tau_g_inhib 	= numpy.concatenate([self.tau_g_inhib, [tau_g_inhib for n in range(numNeuronsToAdd)]])

		self.refracPeriod	= numpy.concatenate([self.refracPeriod, [refracPeriod for n in range(numNeuronsToAdd)]])
		self.timeSinceSpike	= numpy.concatenate([self.timeSinceSpike, [float('inf') for n in range(numNeuronsToAdd)]]) # Initialize time since last spike to inifinity so newly added neurons are definitely not refractory

		self.neuronIDs			= numpy.concatenate([self.neuronIDs, [self.N+n for n in range(numNeuronsToAdd)]])
		self.neuronSynapseTypes	= numpy.concatenate([self.neuronSynapseTypes, [synapse_type for n in range(numNeuronsToAdd)]])
		self.neuronLabels		= numpy.concatenate([self.neuronLabels, [label for n in range(numNeuronsToAdd)]])

		self.spikeEvents	= numpy.concatenate([self.spikeEvents, [0 for n in range(numNeuronsToAdd)]])

		#--------------------
		# Increment the count of total neurons in the network:
		#--------------------
		self.N 	+= numNeuronsToAdd

		#--------------------
		# Expand the connectivity matrices to accomodate the added nuerons.
		# (initialize all connections for newly added neurons to 0 weight)
		#--------------------
		Wts_temp	= numpy.zeros(shape=(self.N, self.N))
		Wts_temp[:(self.N-numNeuronsToAdd), :(self.N-numNeuronsToAdd)] = self.connectionWeights_synExcit
		self.connectionWeights_synExcit = Wts_temp

		Wts_temp	= numpy.zeros(shape=(self.N, self.N))
		Wts_temp[:(self.N-numNeuronsToAdd), :(self.N-numNeuronsToAdd)] = self.connectionWeights_synInhib
		self.connectionWeights_synInhib = Wts_temp

		Wts_temp	= numpy.zeros(shape=(self.N, self.N))
		Wts_temp[:(self.N-numNeuronsToAdd), :(self.N-numNeuronsToAdd)] = self.connectionWeights_gap
		self.connectionWeights_gap = Wts_temp

		#--------------------
		# If the simulation has already been initialized (i.e. variable logs already initialized,
		# such as when adding neuron(s) in middle of simulation), add list(s) to the logs for the neuron(s) being added.
		# If the simulation hasn't yet been initialized, logs will be allocated for all previously added neurons at that time.
		#--------------------
		if(self.simulationInitialized):
			for variable in self.neuronLogVariables:
				self.neuronLogs[variable]['data'] += [[numpy.nan for t in range(self.numTimeSteps)] for n in range(numNeuronsToAdd)]

		#--------------------
		# If the network has an established geometry, add these new neurons to that geometry:
		#--------------------
		# TODO: Make sure this function call is justified
		if(self.geometry is not None):
			self.geometry.addNeurons(numNeuronsToAdd)

		return

	def add_inputs(self, numInputsToAdd, inputType='excitatory'):

		self.inputVals 	= numpy.concatenate([self.inputVals, [0.0 for n in range(numInputsToAdd)]])

		#--------------------
		# Increment the count of total inputs in the network:
		#--------------------
		self.numInputs 	+= numInputsToAdd

		#--------------------
		# Expand the connectivity matrices to accomodate the added nuerons.
		# (initialize all connections for newly added inputs to 0 weight)
		#--------------------
		Wts_temp	= numpy.zeros(shape=(self.numInputs, self.numNeurons))
		Wts_temp[:(self.N-numInputsToAdd), :(self.N)] = self.connectionWeights_inpExcit
		self.connectionWeights_inpExcit = Wts_temp

		Wts_temp	= numpy.zeros(shape=(self.numInputs, self.numNeurons))
		Wts_temp[:(self.N-numInputsToAdd), :(self.N)] = self.connectionWeights_inpInhib
		self.connectionWeights_inpInhib = Wts_temp

		#--------------------
		# If the simulation has already been initialized (i.e. variable logs already initialized,
		# such as when adding neuron(s) in middle of simulation), add list(s) to the logs for the neuron(s) being added.
		# If the simulation hasn't yet been initialized, logs will be allocated for all previously added neurons at that time.
		#--------------------
		if(self.simulationInitialized):
			for variable in self.inputLogVariables:
				self.inputLogs[variable]['data'] += [[numpy.nan for t in range(self.numTimeSteps)] for n in range(numInputsToAdd)]

		return



	def log_current_variable_values(self):
		#~~~~~~~~~~~~~~~~~~~~
		# Log the current values of variables for which logging is enabled:
		#~~~~~~~~~~~~~~~~~~~~
		for n in range(self.N):
			if(self.neuronLogs['neuron_id']['enabled']):
				self.neuronLogs['neuron_id'][n][self.timeStepIndex]	= self.neuronIDs[n]
			if(self.neuronLogs['t']['enabled']):
				self.neuronLogs['t'][n][self.timeStepIndex]	= self.T
			if(self.neuronLogs['spike']['enabled']):
				self.neuronLogs['spike'][n][self.timeStepIndex]	= self.spikeEvents[n]
			if(self.neuronLogs['V']['enabled']):
				self.neuronLogs['V'][n][self.timeStepIndex]	= self.V[n]
			if(self.neuronLogs['g_leak']['enabled']):
				self.neuronLogs['g_leak'][n][self.timeStepIndex]	= self.g_leak[n]
			if(self.neuronLogs['g_excit']['enabled']):
				self.neuronLogs['g_excit'][n][self.timeStepIndex]	= self.g_excit[n]
			if(self.neuronLogs['g_inhib']['enabled']):
				self.neuronLogs['g_inhib'][n][self.timeStepIndex]	= self.g_inhib[n]
			if(self.neuronLogs['g_gap']['enabled']):
				self.neuronLogs['g_gap'][n][self.timeStepIndex]	= self.g_gap[n]
			if(self.neuronLogs['synapse_type']['enabled']):
				self.neuronLogs['synapse_type'][n][self.timeStepIndex]	= self.neuronSynapseTypes[n]
			if(self.neuronLogs['label']['enabled']):
				self.neuronLogs['label'][n][self.timeStepIndex]	= self.neuronLabels[n]

		for i in range(self.numInputs):
			if(self.inputLogs['input_id']['enabled']):
				self.inputLogs['input_id'][n][self.timeStepIndex]	= self.inputIDs[n]
			if(self.inputLogs['t']['enabled']):
				self.inputLogs['t'][n][self.timeStepIndex]	= self.T
			if(self.inputLogs['inpput_val']['enabled']):
				self.inputLogs['input_val'][n][self.timeStepIndex]	= self.inputVals[n]
			if(self.inputLogs['inpput_type']['enabled']):
				self.inputLogs['input_type'][n][self.timeStepIndex]	= self.inputTypes[n]
			if(self.inputLogs['label']['enabled']):
				self.inputLogs['label'][n][self.timeStepIndex]	= self.inputLabels[n]

		return
		

	def initialize_simulation(self, T_max=None, deltaT=None, integrationMethod=None):
		# Call the standard network simulation initialization:
		NeuronNetwork.initialize_simulation(T_max, deltaT, integrationMethod)

		########################################
		# LIFNetwork-specific initializations: #
		########################################

		#~~~~~~~~~~~~~~~~~~~~
		# Pre-calculate numerical integration constants according to the given integration method:
		#~~~~~~~~~~~~~~~~~~~~
		self.integrationMethod	= self.integrationMethod.lower()

		if(self.integrationMethod == 'euler' or self.integrationMethod == 'forwardeuler' or self.integrationMethod == 'rk1'):
			# print('+++ INTEGRATION <eul> +++')
			self.constAlpha_g_excit	= 1.0 - self.deltaT/self.tau_g_excit
			self.constBeta_g_excit	= self.deltaT/self.tau_g_excit
			self.constAlpha_g_inhib	= 1.0 - self.deltaT/self.tau_g_inhib
			self.constBeta_g_inhib	= self.deltaT/self.tau_g_inhib


		elif(self.integrationMethod == 'trapezoid' or self.integrationMethod == 'trapezoidal'):
			pass

		elif(self.integrationMethod == 'rk2'):
			pass

		elif(self.integrationMethod == 'rk4'):
			pass

		else:
			print("The given integration method, \'"+self.integrationMethod+"\' is not recognized. Forward euler integration will be used by default.")

		return


	def network_update(self):

		#**********************
		# Update Conductances *
		#**********************
		#----------------------
		# No need to have if statements for integration method because we're putting all update rules in the same form (g(t+1) = alpha*g(t) + beta*Ws)
		# where the only difference between the integration methods are the values of constants alpha and beta,
		# which are pre-calculated at network initialization according to integration method
		synpaseInducedConductanceChange_excit 	= self.connectionWeights_synExcit.T.dot(self.spikeEvents*self.diracDeltaValue())
		synpaseInducedConductanceChange_inhib 	= self.connectionWeights_synInhib.T.dot(self.spikeEvents*self.diracDeltaValue())
		inputInducedConductanceChange_excit 	= self.connectionWeights_inpExcit.T.dot(self.inputValues_excit) if self.numInputs_excit() > 0 else numpy.zeros(self.N)	
		inputInducedConductanceChange_inhib 	= self.connectionWeights_inpInhib.T.dot(self.inputValues_inhib) if self.numInputs_inhib() > 0 else numpy.zeros(self.N) 	
		
		self.g_excit 	= self.constAlpha_g_excit*self.g_excit + self.constBeta_g_excit*(synpaseInducedConductanceChange_excit  + inputInducedConductanceChange_excit) 
		self.g_inhib 	= self.constAlpha_g_inhib*self.g_inhib + self.constBeta_g_inhib*(synpaseInducedConductanceChange_inhib  + inputInducedConductanceChange_inhib)

		#******************
		# Update Voltages *
		#******************
		#------------------
		# Voltage update rules depend on primarily non-constant variable terms, so there's not really anything to pre-calculate.
		# Therfore, we case the integration method and calculate the updated voltage accordingly every sim step.

		# This is one term that appears in multiple integration methods
		# that we can compute now for syntactic concision below (little performance savings here):
		R_dt 	= self.R_membrane * self.deltaT

		if(self.integrationMethod == 'euler' or self.integrationMethod == 'forwardeuler' or self.integrationMethod == 'rk1'):

			self.V 	= R_dt*( ((1/R_dt)-(self.g_leak + self.g_excit + self.g_inhib + self.g_gap*self.connectionWeights_gap.sum(axis=0)))*self.V
						+ self.g_leak*self.V_eqLeak + self.g_excit*self.V_eqExcit + self.g_inhib*self.V_eqInhib + self.g_gap*self.connectionWeights_gap.T.dot(self.V) 
						#+ (self.connectionWeights_inpExcit.T.dot(self.inputValues_excit) if self.numInputs_excit() > 0 else numpy.zeros(self.N)	) 
						) #[incomplete edit 13sept17]

		elif(self.integrationMethod == 'trapezoid' or self.integrationMethod == 'trapezoidal'):
			pass

		elif(self.integrationMethod == 'rk2'):
			pass

		elif(self.integrationMethod == 'rk4'):
			pass

		else:
			print("LIFError: Unrecognized integration method, \'"+self.integrationMethod+"\', referenced in simStep().")
			exit()

		for n in range(self.N):
			#****************************
			# Enforce Refractory Period *
			#****************************
			#----------------------------
			# Before checking for threshold-crossing, reset to resting voltage any neurons that are still refractory:
			if(self.timeSinceSpike[n] < self.refracPeriod[n]):
				self.V[n] 	= self.V_reset[n]

			#**********************
			# Update Spike Events *
			#**********************
			#----------------------
			# Record which neurons have crossed threshold voltage and have thus spiked:
			# self.spikeEvents 	= (self.V >= self.V_thresh).astype(int)
			if(self.V[n] >= self.V_thresh[n]):
				# Reset neurons that have spiked to their reset voltage:
				self.spikeEvents[n]		= 1
				self.V[n]				= self.V_reset[n]
				self.timeSinceSpike[n]	= 0
				print "spike @ " +str(self.t)
			else:
				self.spikeEvents[n]		= 0
				self.timeSinceSpike[n]	+= self.deltaT
	

