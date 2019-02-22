
# Here is a list of possible validations on the submission template:
# 1. I really like the structural validations, all of the ones that you suggested should be present
# 2. Strict enforcement of the 11 character md5 hash of the stateset, and having a value in each of the subsequent columns for each entry
# 3. Ensure that the values of name, _rxn_M_inorganic, and _rxn_M_organic, all correspond to the appropriate row in the state set
# 3 a. Based on the name of the row (0,1,2,3,etc) the _rxn_M* columns should be identical to those in the state set (the state set with the same crank number)

import pandas as pd
DELIMITER = ','
VALID_CATEGORIES = set([1,2,3,4])
BAD_DELIMITERS = set('\t, |.') - set(DELIMITER)  # common delimiters that are disallowed
COLUMNS = ['dataset','name','_rxn_M_inorganic','_rxn_M_organic','predicted_out','score']

def arr2html(arr):
    out="<ul>\n"
    out += "\n".join("<li>%s</li>" % x for x in arr)
    out += "\n</ul>\n"
    return out

def validate_submission(f,num_rows=10,statespace=None):
    
    arr = []

    #make sure file is comma  delimited
    with open(f, 'r') as fh:
        for header in fh:
            if header[0] != '#':
                break
    if any(d in header.split(DELIMITER)[0] for d in BAD_DELIMITERS):
        arr.append("file does not appear to be comma delimited. No tabs or spaces allowed")
        return arr2html(arr)

    #make sure columns match
    df = pd.read_csv(f,comment='#',sep=DELIMITER)
    cols = df.columns
    for i, col in enumerate(cols):
        if COLUMNS[i] != col:
            arr.append( "Wrong columns uploaded.<br/>Received '%s'<br/>expected '%s'" % (",".join(cols), ",".join(COLUMNS)))
            return arr2html(arr)

    # assert the number of rows
    if len(df) != num_rows:
        arr.append("Length of CSV (%d) is not equal to the target number of rows (%d)" % (len(df),num_rows))
        
    # validate each row
    num_errors = 0
    for i, row in df.iterrows():

        if num_errors > 10:
            arr.append("Stopping checks due to more than 10 errors")
            break

        if len(row) != len(COLUMNS):
            arr.append("Row %d, with %d columns, does not equal specified number (%d)" % ( i, len(row), len(COLUMNS)))
        
        if statespace and row['dataset'] != statespace:
            num_errors+=1
            arr.append("Row %d 'dataset' column (%s) is not 11 chars. Is it the state set hash?" % (i, row['dataset']))
        try:
            int(row['name'])
        except ValueError:
            num_errors+=1                
            arr.append("Row %d 'name' column (%s) is not an int. Is it the run number?" % (i, row['name']))                            
        try:
            float(row['_rxn_M_inorganic'])
        except ValueError:
            num_errors+=1                
            arr.append("Row %d '_rxn_M_inorganic' column (%s) is not a float. Did you use the values from the state set?" % (i, row['_rxn_M_inorganic']))                            
        try:
            float(row['_rxn_M_organic'])
        except ValueError:
            num_errors+=1                
            arr.append("Row %d '_rxn_M_organic' column (%s) is not a float. Did you use the values from the state set?" % (i, row['_rxn_M_organic']))                            
        if row['predicted_out'] not in VALID_CATEGORIES:
            num_errors+=1
            arr.append("Row %d 'predicted_out' column (%s) is not in %s" %(i,row['predicted_out'],",".join([str(x) for x in VALID_CATEGORIES])))
        try:
            x=float(row['score'])
            if x < 0 or x > 1:
                num_errors+=1
                arr.append("Row %d 'score' column (%s) is not a float within [0,1]" % (i,row['score']))
        except ValueError:
            num_errors+=1                
            arr.append("Row %d 'score' column (%s) is not a float. Did you use the values from the state set?" % (i, row['score']))                        
        
    if len(arr) > 0:
        return arr2html(arr)
    else:
        return None

if __name__ == '__main__':
    import sys
    print(validate_submission(sys.argv[1]))
