"""

In this code I have implementd the functions to generate the nodal analysis matrix and solve it using the 
np.linalg library available in Numerical python

Author : Deenabandhan N
Roll number : EE23B021
Version : 1.0.1
Date : 30/08/2024

"""

from collections import defaultdict  # This module is used to store a default value
import numpy as np  # This is used to solve the matrix equations


def read(filename: str) -> list:
    """Function to read the contents in the file"""
    with open(filename, encoding="utf-8") as file:
        lst_ = file.readlines()  # This will generate a list of lines stored in the file
    check = 0  # This variable will check for the presence of <.circuit>  <.end> in the file
    lst = [i.replace("\n", "") for i in lst_]  # To remove the newline character at the end of the line
    elements = []
    for i in lst:
        ckt = i.split(" ")
        if ckt[0] == ".circuit":
            check = 1  # It will start taking in the values when check=1
            continue
        if ckt[0] == ".end":
            check = 0  # It will stop taking values when check=0
        if not check:
            continue
        _ = []
        for i in ckt:
            if (i == "#"):  # We should neglect the commented lines which will start with #
                break
            if not (len(i) == 0 or i.isspace()):  # Each element should have a finite length and it should not be a whitespace character
                _.append(i)
        elements.append(_)
    if len(elements) == 0:
        raise ValueError("Malformed circuit file")  
        # Condition to check if the circuit has valid circuital elements
    if check == 1:
        raise ValueError("Malformed circuit file")
        # Condition to check if the circuit has .end

    return elements


def eval_mat(elements: list) -> tuple[dict[str, int], dict]:
    """Function to generate the nodal analysis matrix and solve it"""
    nodes = defaultdict(lambda: -1)
    # This dictionary will contain the name of the node/voltage source corresponding to a number
    names=defaultdict(lambda: -1) #To check the repeating names
    name_v = {}  # Voltage nodes
    name_i = {}  # Voltage sources to find current through them
    c = 0
    vc = 0
    z_node=defaultdict(lambda: -1) # To check the multiple zero resistor nodes
    rm_elem = []
    for i in elements:
        if len(i) == 0:  # If there is any element of length 0 it will remove it
            elements.remove(i)
            continue
        if (i[0][0].upper() == "R" or i[0][0].upper() == "I" or i[0][0].upper() == "V"): 
            # The elements should be either V or I or R
            if (i[0][0].upper() == "R"):  # The case where resistance value equal to zero
                try:
                    val=float(i[3]) # It also checks if the given resistance is a valid number
                except:
                    raise ValueError("Give a valid resistance value")
                if(val==0):
                    lst_=f"{i[1]},{i[2]}"
                    if(z_node[lst_]!=-1): #To check if there is multiple zero resistors connected between same nodes
                        rm_elem.append(i)
                        continue
                    z_node[lst_]=1
                    _ = list(i)
                    _[0] = f"v#{vc}"  # Creating a voltage source with the name v# with voltage=0
                    vc += 1
                    _.insert(3, "dc")
                    rm_elem.append(i)  # Appending all the resistor elements with resistance=0
                    elements.append(_)  # Appending the voltage element with v=0
                    continue
            if(names[i[0]]!=-1):
                raise ValueError("Names cannot be repeated") #To check if the names are repeated
            names[i[0]]=1
            if i[1] != "GND":
                if(nodes[i[1]]==-1):
                    nodes[i[1]] = c  # Naming the nodes with matrix index
                    name_v[c] = i[1]
                    c = c + 1
            if i[2] != "GND":
                if(nodes[i[2]]==-1):
                    nodes[i[2]] = c  # Naming the nodes with matrix index
                    name_v[c] = i[2]
                    c += 1
            if i[0][0].upper() == "V":
                nodes[i[0]] = c  # Naming the current through the voltage
                name_i[c] = i[0]
                c += 1
        else:
            raise ValueError("Only V, I, R elements are permitted")
            # If there are any other elements, error is raised
    n = len(nodes)
    mat = np.zeros((n, n))  # N by N matrix to create matrix
    sol = np.zeros(n)  # The constants of the equations

    _ = [i for i in elements if i not in rm_elem]  # Removing the elements where the resistance is zero
    elements = _


    for i in elements:
        if(i[0][0].upper() == "R"):
            if i[1] != "GND":
                mat[nodes[i[1]], nodes[i[1]]] += 1 / float(i[3])
                # Adding the admittance of resistor connected between node and GND at the position (node,node)
            if i[2] != "GND":
                mat[nodes[i[2]], nodes[i[2]]] += 1 / float(i[3])
                # Adding the admittance of resistor connected between node and GND at the position (node,node)
            if i[1] != "GND" and i[2] != "GND":
                mat[nodes[i[1]], nodes[i[2]]] -= 1 / float(i[3])
                # Adding the admittance of resistor connected between node1 and node2 at the position (node1,node2)
                mat[nodes[i[2]], nodes[i[1]]] -= 1 / float(i[3])
                # Adding the admittance of resistor connected between node1 and node2 at the position (node1,node2)
        if i[0][0].upper() == "I":
            try:
                val=float(i[4]) # It also checks if the given resistance is a valid number
            except:
            	raise ValueError("Give a valid current value")
            if i[1] != "GND":
                sol[nodes[i[1]]] -= val  
                # Subtracting the current from the first node as it comes out of the node
            if i[2] != "GND":
                sol[nodes[i[2]]] += val
                # Adding the current to the second node as it gets into the node
        if i[0][0].upper() == "V":
            try:
                val=float(i[4]) # It also checks if the given resistance is a valid number
            except:
                raise ValueError("Give a valid voltage value")
            if i[1] != "GND":
                mat[nodes[i[0]], nodes[i[1]]] = 1
                # The voltage difference between first node and second will be V so we have that element to be +1
                mat[nodes[i[1]], nodes[i[0]]] = 1
                # The current from voltage source will come out of the first node so we make the element to be +1
            if i[2] != "GND":
                mat[nodes[i[0]], nodes[i[2]]] = -1
                # The voltage difference between first node and second will be V so we assign element to be (-1)
                mat[nodes[i[2]], nodes[i[0]]] = -1
                # The current from voltage source will get into the second node so we assign element to be (-1)
            sol[nodes[i[0]]] = val
    det = np.linalg.det(mat)  # Finding the determinant of the matrix
    if det == 0:
        raise ValueError("Circuit error: no solution")
        # If determinant=0 then the KCL equations cannot be used i.e it is an invalid circuit
    eq = np.linalg.solve(mat, sol)

    ans_v = {"GND": 0}  # Dictionary to store the nodal voltages
    ans_i = {}  # Dictionary to store the current through the voltage sources
    for i, j in enumerate(eq):
        if i in name_v:
            ans_v[name_v[i]] = j
        else:
            if (name_i[i][1] == "#"):  
            # We should not include the current through the temporary voltage source that we have created
                continue
            ans_i[name_i[i]] = j
    return (ans_v, ans_i)


def evalSpice(filename: str) -> tuple[dict[str, int], dict[str, int]]:
    """Function to solve the circuit given in the file"""
    try:
        ans = read(filename)
    except FileNotFoundError as error:
        raise FileNotFoundError("Please give the name of a valid SPICE file as input") from error
        # Test to check the availability of the file
    return eval_mat(ans)


