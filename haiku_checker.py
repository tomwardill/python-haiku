import simplejson as json
import sys, re, string,os

# load the cmu dict
try:
    path = os.path.join(os.path.dirname(__file__), 'cmu_dict.json')
    cmu = json.load(open(path))
except:
    print "Converted CMU dict not found"
    sys.exit(0) 

SubSyl = [
       'cial',
       'tia',
       'cius',
       'cious',
       'giu',              # belgium!
       'ion',
       'iou',
       'sia$',
       '.ely$',             # absolutely! (but not ely!)
      ]

AddSyl = [ 
       'ia',
       'riet',
       'dien',
       'iu',
       'io',
       'ii',
       '[aeiouym]bl$',     # -Vble, plus -mble
       '[aeiou]{3}',       # agreeable
       '^mc',
       'ism$',             # -isms
       '([^aeiouy])\1l$',  # middle twiddle battle bottle, etc.
       '[^l]lien',         # alien, salient [1]
           '^coa[dglx].',      # [2]
       '[^gq]ua[^auieo]',  # i think this fixes more than it breaks
       'dnt$',           # couldn't
      ]

def _guess_sy_count(word):
    """If we can't lookup the word, then guess its syllables count. This is
    (heavily) based on Greg Fast's Perl module Lingua::EN::Syllables. But
    the bugs are mine."""
    mungedword = re.sub('e$','',word.lower())
    splitword = re.split(r'[^aeiouy]+', mungedword)
    splitword = [ x for x in splitword if (x != '') ] # hmm
    syllables = 0
    for i in SubSyl:
        if re.search(i,mungedword):
            syllables -= 1
    for i in AddSyl:
        if re.search(i,mungedword):
            syllables += 1
    if len(mungedword) == 1: syllables =+ 1
    syllables += len(splitword)
    if syllables == 0: syllables = 1
    return syllables

def _count_syllables(word):
    if cmu.has_key(word):
        return cmu[word]
    else:
        return _guess_sy_count(word)

def check_string(to_check):
    
    haiku_form = [5,12,17]
    
    upper = to_check.upper()
    split = upper.split(' ')
    
    
    for count in haiku_form:
        syllable_count = 0
        haiku_line = 0
        for word in split:
            syllable_count += _count_syllables(word)
            if syllable_count == haiku_form[haiku_line]:
                haiku_line += 1
                if haiku_line >= len(haiku_form):
                    return True
            elif syllable_count > haiku_form[haiku_line]:
                return False
               
def find_haiku(to_check):
    split = to_check.split(' ')

    haiku_list = []

    for i in range(0, len(split) - 2):
        for j in range(i + 3, len(split) + 1):
            final = string.join(split[i:j], ' ')
            if final and check_string(final):
                haiku_list.append(final)

    return haiku_list

if __name__ == '__main__':
    print find_haiku('As the wind does blow Across the trees, I see the Buds blooming in May')
