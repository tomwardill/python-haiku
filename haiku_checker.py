import simplejson as json
import sys, re

# load the cmu dict
try:
    cmu = json.load(open('cmu_dict.json'))
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
    upper = to_check.upper()
    split = upper.split(' ')
    syllable_count = 0
    
    for word in split:
        word_count = _count_syllables(word)
        print word
        print word_count
        syllable_count += word_count
        if syllable_count > 17:
            return False
    print syllable_count
    
    
    
if __name__ == '__main__':
    check_string('this is a quackable test')