# convert the CMU dictionary into something that can be used for haiku detection in python

import re
import simplejson as json

f = open('c06d')

words = {}

lines = f.read()

for line in lines.split('\n'):
    if line:
        if re.match('[A-Z]', line[0]):
            split = line.partition(' ')
            words[split[0]] = len(re.findall("\d+", split[2]))
        
        
encoded =  json.dumps(words)

output_file = open('cmu_dict.json', 'w')
output_file.write(encoded)
output_file.close()