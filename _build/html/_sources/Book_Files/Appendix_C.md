# Appendix C: Model Development Timeline

The OSeMOSYS model in this repository wa developed in a modular fashion, with 6 (six) different phases of upgrades. This appendix describes theses phases in detail, as well as show their reference energy systems.

This model is based off of the "toy model" by Cristiano Fernandes which can be found in [this folder](https://github.com/IESVIC2060/Storage-Master/tree/Working_Branch/Model-Data/Cristiano_Toy_Model) inside this GitHub repository.

## C.1 Phase 1 - Electricity Demand and Hydro Production

The additions made to this mopdel for phase 1, ontop of the toy model were the following:

* Hydro as a production technology
* Electricity distribution network
* Electricity demand
* 1 dummy technology as an electricity consumer (i.e any kitchen applience, or any other electric device connected to the grid)

The figure below represents the reference energy system for this stage of development.

![](../Images/Kevin_RES_V1.drawio.png)

## C.2 Phase 2 - Adding Water Heat Demand and Technologies

In this phase the following additions have been made:

* Water heat demand
* Electric and gas water heaters as consumer technologies

The figure below represents the reference energy system for this stage of development.

![](../Images/Kevin_RES_V2.png)

## C.3 Phase 3 - Heat Pump

In this phase the following additions have been made:

* Heat pump as a space heater

The figure below represents the reference energy system for this stage of development.

![](../Images/Kevin_RES_V3.png)

## C.4 Phase 4 - Simplified Hydrogen and Electric Storages 

In this phase the following additions have been made:

* Electricity Storage
* Hydrogen Storage at a third mode of operation and outputing into the gas distribution pipeline (forming a gas mixturein the pipeline)
* Electrolyzer as input to the hydrogen storage (simplified version for hydogen storage)

The figure below represents the reference energy system for this stage of development.

![](../Images/Kevin_RES_V4.png)

## C.5 Phase 5 - Splitting Hydro Production

In this phase the following additions have been made:

* Hydro flexible production technology
* Hydrogen storage operating at the second mode of operation
* Electrolyzer as hydrogen production only (no longer inputting into hydrogen storage) 

The figure below represents the reference energy system for this stage of development.

![](../Images/Kevin_RES_V5.png)