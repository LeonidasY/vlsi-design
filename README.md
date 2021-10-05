# CDMO Project (VLSI Design) 

## Overview
The CDMO project involves the solving of a VLSI (Very Large Scale Integration) problem using (i) Constraint Programming (CP), and (ii) propositional SATisfiability (SAT) and/or its extension to Satisfiability Modulo Theories (SMT). VLSI refers to the trend of integrating circuits into silicon chips.

## Authors
- Leonidas Gee
- Anna Fabris

## Dataset
The dataset consist of 40 VLSI instances, where each instance is a text file containing the following:
- The first line gives w, which is the width of the silicon plate.
- The following line gives n, which is the number of necessary circuits to place inside the plate. 
- Then n lines follow, each with x<sub>i</sub> and y<sub>i</sub> , representing the horizontal and vertical dimensions of the i-th circuit.

## Methodologies
The steps taken for each method are described in a series of reports as follows:
- [CP Report](https://github.com/LeonidasY/vlsi-design/blob/main/CP/Report.pdf)
- [SAT Report](https://github.com/LeonidasY/vlsi-design/blob/main/SAT/Report.pdf)
- [SMT Report](https://github.com/LeonidasY/vlsi-design/blob/main/SMT/Report.pdf)

## Results
The images below show the visualisations of different solved instances using either CP, SAT or SMT.

<p float="left">
  <img src="https://github.com/LeonidasY/vlsi-design/blob/main/CP/CP (Normal)/out/images/out-5.png" width="300" />
  <img src="https://github.com/LeonidasY/vlsi-design/blob/main/CP/CP (Rotation)/out/images/out-10.png" width="300" /> 
  <img src="https://github.com/LeonidasY/vlsi-design/blob/main/SAT/out/images/out-15.png" width="300" /> 
  <img src="https://github.com/LeonidasY/vlsi-design/blob/main/SMT/out/images/out-30.png" width="300" />
</p>
