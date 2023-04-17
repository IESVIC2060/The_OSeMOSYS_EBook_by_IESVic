# Appendix B: OSeMOSYS Storage Dynamics

Storage is an important part of any energy system model spanning through multiple seasons. As such, it is essential that any modeler understands the dynamics of the flow of energy through a reference energy system (RES) when storage is envolved. The OSeMOSYS interpretation of storage in a RES is quite convoluted and can lead to a few misunderstandings of how storage works. This appendix aims at clarifying these common misunderstandings and presenting the storage dynamics in OSeMOSYS as a powerful tool to model real world systems.  

As was explained in chapters 2 and 3 of this wiki, OSeMOSYS makes use of parameters to capture the different aspects of the RES which have a direct impact over system performance, a few of which are linked to storage dynamics. That is, if your model implementation is correct, then storage can be included, or excluded from your model by simply turning its related parameters on, or off.

## B.1 Modes of Operation

A "mode of operation" in OSeMOSYS is a set which defines the operating regime of a technology in the model. A technology can assume many roles over the time span of a model, some examples being producing different kinds of energy (heat, or electricity), contributing to, or taking energy from storage, and outputing different types of fuels into the energy grid (contributing to gas mixtures). All of these activities will have a different mode of operation assigned to each one of them.

For the scope of this appendix, the mode of operation business can be quite useful for making sure that a technology will never interact with storage facilities, if your RES determines it to be the case. This is possible because the `Mode_of_Operation` set is a part of both the `Input` and `Output` activity ratio parameters, as well as the `Variable_Cost` parameter. These parameters will define the ratio of fuels being contributed to, and by the technology, and the variable operation and maintenance (O&M) costs to each technology, respectively.

Assignment of a wrong mode of operation to in any given parameter for a technology can lead to unexpected, or unwanted results. This topic will be re-addressed later when we approach some techniques for debugging storage.

## B.2 Turning Storage On and Off

The storage dynamics inside na OSeMOSYS model are controlled by the storage parameters, which are applied to each and every storage set. A storage set is a matrix index inside the linear program model that captures the facilities used to store energy for later use over the whole time period.

The following parameters are used by the Pyomo model to control the energy flux in the energy system and determine the use of storage facilities:

* Input activity ratio: "Rate of use of a commodity (fuel) by a technology, as a ratio of the rate of activity (use of a technology over the model year)." 
 
* Output activity ratio: "Rate of commodity (fuel) output from a technology, as a ratio of the rate of activity (use of a technology over the model year)."

* Variable cost: "Cost of a technology for a given mode of operation (Variable O&M cost), per unit of activity." If a given mode of operation is being used by the model to transmit energy from storage to a technology, then the variable cost for that technology at that mode of operation can act as a constraint to storage usage by that technology.

* Technology to storage and technology from storage: These two parameters assume binary values only (0 = off, 1 = on), which determine if the communication link between a technology and a storage unit exist for charging and discharging that storage facility, respectively.

* Storage Level Start: This is the total amount of energy (in MW) given to a storage facility at the start of the model execution.

* Storage Level Finish: This is the desired amount of energy (in MW) that a storage facility has to retain at the end of the model execution

* Min Storage Charge: This parameter sets the minimum amount of stored energy (in MW) to be present in a storage facility at any time slice as a fraction (percentage from 0 to 1) of the maximum set at the start (Storage Level Start).

* Storage Max Charge Rate: "Maximum charging rate for the storage, in units of activity per year."

* Storage Max Discharge Rate: "Maximum discharging rate for the storage, in units of activity per year."
	
	
From the list of parameters which control storage in OSeMOSYS, we see that this functionality can be "turned on" or "off" via different ways. For instance, storage can be deactivated by:

* Assigning a Min Storage Charge  of 1 (100%) to a storage facility, making it so storage never depleats
  
* Equating the Storage Level Start and Storage Level Finish parameters, essentially determining that storage won't change over time

* Turning off the output activity ratio of the extraction technologies, since this won't allow the extractors to supply the system with energy coming from storage (maintaining storage levels at storage level start)

* Giving the storage facility a Storage Max Discharge Rate of 0, essentially prohibiting it from discharging its contents into the system.

## B.3 Debugging Problems With Storage

In this section we will look into a few ways in which storage might not operate correctly inside the OSeMOSYS model and how to address those issues.
### B.3.1 Parameter Manipulations to Watch Out for

Changing a few parameters might not cause the intended effect on the model results. Here are some notable examples:

* Turning TechnologyToStorage and TechnologyFromStorage off (0) won't turn off storage, but will make the initial level for that storage unit depleat at the first time slice (going from time slice 1 to time slice 2 depleats the entire storage unit)

* Turning the Input Activity Ratio of a technology that feeds a storage facility off (0) won't turn off storage, if the storage level start is greater than 0, since the storage will have some energy to give to the extraction technologies.


## B.4 References

1. [OSeMOSYS Structure](https://osemosys.readthedocs.io/en/latest/manual/Structure%20of%20OSeMOSYS.html)