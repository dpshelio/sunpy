import numpy as np
#class vsop87(object):
#    def __init__(self, ephemerides_file):
#        
#        pass
def read_vsop87(filename='vsop87/VSOP87D.ear'):
    '''
    
    '''
    #filename = 'vsop87/VSOP87D.ear' #FIXME to any OS
    with open(filename) as vsop87:
        earth = vsop87.readlines()
    for i,line in enumerate(earth):
        line = line.splitlines()[0].split()
        if 'VSOP' in line[0]:
            if i == 0:
                # Extract automatically variables from file
                # so it works for any type of file.
                output = {var:{} for var in line[6][1:-1]}
                version = line[2]
                planet = line[3]
            variable = line[6][int(line[5])]
            factor = line[7]
            n_terms = int(line[8])
            start_factor = True
        else:
            if start_factor:
                output[variable][factor]={'A':[], 'B':[], 'C':[]}
                start_factor = False
            A,B,C = (float(value) for value in line[-3:])
            for subterm in 'ABC':
                output[variable][factor][subterm].append(eval(subterm))
    # Convert all to numpy arrays
    for variable in output.keys():
        for factor in output[variable].keys():
            for subterm in output[variable][factor].keys():
                output[variable][factor][subterm] = np.array(output[variable][factor][subterm])
    output['planet'] = planet
    output['version'] = version
    return output

# TAU = JDE - 2451... / 36520 (32.1)
# Each term: A * cos(B + C*tau)
# B and C in radians
# A in 1e-8 radians for long and lat
#      1e-8 AU for rad vector
# L = (L0 + L1*tau + L2*tau**2 ... L5*tau**5)/1e8 (32.2)

# to put it in FK5 reference
# T = 10*tau
# L' = L - 1.397(deg) * T - 0.00031(deg) * T**2
# Corrections for L and B  (32.3 pag 219)
# they should not be done if using book short version of VSOP87
#   (but I have a more detailed one).

# Accuracy of the results based on when the series is truncated (pag220)
