# CDMO 1 Project (VLSI Design) 

## Overview
The CDMO project involves the solving of a VLSI (Very Large Scale Integration) problem using (i) Constraint Programming (CP), and (ii) propositional SATisfiability (SAT) and/or its extension to Satisfiability Modulo Theories (SMT). VLSI refers to the trend of integrating circuits into silicon chips.

A report was written and submitted as part of the project and may be viewed [here]().

### Dataset
The dataset consist of 40 VLSI instances, where each instance is a text file containing the following:
- The first line gives w, which is the width of the silicon plate.
- The following line gives n, which is the number of necessary circuits to place inside the plate. 
- Then n lines follow, each with x<sub>i</sub> and y<sub>i</sub> , representing the horizontal and vertical dimensions of the i-th circuit.

## Results
The images below show the visualisations of different solved instances using either CP, SAT or SMT.

<p float="left">
  <img src="https://github.com/LeonidasY/vlsi-design/blob/main/output/CP%20(Normal)/images/out-5.png" width="300" />
  <img src="https://github.com/LeonidasY/vlsi-design/blob/main/output/CP%20(Rotation)/images/out-10.png" width="300" /> 
  <img src="https://github.com/LeonidasY/vlsi-design/blob/main/output/SAT/images/out-15.png" width="300" /> 
  <img src="https://github.com/LeonidasY/vlsi-design/blob/main/output/SMT/images/out-30.png" width="300" />
</p>
