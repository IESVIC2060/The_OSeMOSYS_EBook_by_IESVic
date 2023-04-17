# 1 Introduction to Energy Modelling and OSeMOSYS

## 1.1 Energy Sector Modelling

The energy industry is a vital part of our everyday lives. It is responsible for powering our house appliances, our communication systems, producing heat during the winter and powering AC units during the summer. It is also a structural component of a country’s supply chain, without it, the logistics and execution of transporting goods across drastically less efficient and time consuming.

Energy systems models aim at representing all components and processes in energy systems in a mathematical manner, through equations. These models provide useful insights into the dynamics of the energy system but can never truly predict the future of the energy grid. Additionally, it is important to note that energy will follow the path described by the diagram below inside any energy system.

![](https://github.com/IESVIC2060/Storage-Master/blob/Working_Branch/Wiki/Images/Energy%20System%20Representation.jpg)

Energy resources are either domestically extracted or imported; then they are converted into electricity inside powerplants. Finally, this electricity is transported to the end-user   via the energy grid, where it is consumed. 

To better study an energy system, it is often desired to represent it using a Reference Energy System (RES). A RES is a simplified graphical representation of the energy system under analysis and can cover possible policy development paths. Reference Energy Systems should be a minimum representation of reality needed to answer the relevant policy questions being addressed.

## 1.2 Motivation: Why Model Energy Systems?

“A sustainable energy system can lift people out of poverty around the world” [1].  In a rapidly evolving world, energy systems continue to get increasingly complex and capital intensive, requiring evermore comprehensive planning and analysis. 

A comprehensive energy system analysis denotes the inexistence of a “one size fits all” solution [1], since this analysis will vary depending on the country’s infrastructure, current environmental policies that dictate the established energy system, economic profile of the country, and many other region-specific factors. 

Often, we see short-term necessities taking precedence over long-term investments on policies that dictate the energy system which could lead the path towards a sustainable energy grid if given the deserved priorities.  Energy modelling can benefit both engineers and policy makers, as it helps mitigate uncertainty of future scenarios while accounting for necessities, available resources and demands of the local population. Moreover, if grounded with sound project economics, modelling can have a majorly positive impact on the environment and bring with it economic prosperity [1].  

## 1.3 Reference Energy System (RES) Design

A reference energy system (RES) is a simplified graphical representation of the real energy system under analysis. A RES is useful for exploring different research and development paths (scenarios) for the real system.

A RES should be a minimum representation that sufficiently answers all policy questions being asked. In order to create a RES there are two primary factors which need to be identified: the energy carriers and their energy levels (primary, secondary, consumer, etc.), and the available facilities to the system (technologies, storage units).

The following figures (1 and 2) each contain a reference energy system with storage implementation. Note there is no standard way to label the elements in the drawings, so each author conceived their own legend to go with the RES. Figure 1 shows the OSeMOSYS training case study RES, while figure 2 displays a simple toy model developed by the IESVic team.

<figure>
    <img src= "https://github.com/OSeMOSYS/OSeMOSYS/blob/master/Training_Case_Studies/RES_storage.png?raw=true" alt="">
    <figcaption align="center"><b> Figure 1: OSeMOSYS training case study RES </b>
    </figcaption>
</figure>

<figure>
    <img src= "https://github.com/criscfer/Personal_Storage_Folder/blob/main/Images/Toy_Model_Simplified_RES.jpg?raw=true">
    <figcaption align="center"><b> Figure 2: IESVic toy model RES </b>
    </figcaption>
</figure>


## 1.4 What is OSeMOSYS?

“OSeMOSYS is an open source modelling system for long-run integrated assessment and energy planning” [2]. OSeMOSYS has been used to develop and document over 60 (sixty) national energy models and is available in three different programming languages:

* GNU MathProg
* Python (Pyomo)
* GAMS

The MathProg and Pyomo implementations are able to “run free and openly from source to solver” [2].  OSeMOSYS allows us to run models from a  region-based analysis all the way to a national, continental, or even global scale outlook, adjusting its scope according to the researcher, engineer, or policy maker’s necessity.

## 1.5 References

[1] [Energy and Flexibility Modelling: OSeMOSYS & FlexTool - Open University Course](https://www.open.edu/openlearncreate/course/view.php?id=6817)
 
[2] [OSeMOSYS - Home Page](http://www.osemosys.org/)

[3] [OSeMOSYS Documentation](https://osemosys.readthedocs.io/en/latest/)

[4] [OSeMOSYS User Manual - 2015](https://archive.org/details/manualzilla-id-5811946/mode/2up)

[5] [UCL Energy Institute Models - OSeMOSYS](https://www.ucl.ac.uk/energy-models/models/osemosys)