#!/usr/bin/python2.2
###
# haiku - finds accidental 5-7-5 syllable constructs in free text
#i##
# $Id: haiku,v 1.17 2003/02/10 03:39:30 danny Exp $
###
# 
# Based on idea (and, sadly, lost implementation) by Don Marti.
# Requires the c06d file from  http://www.speech.cs.cmu.edu/cgi-bin/cmudict
#
# This code lives at http://www.oblomovka.com/code/ - please check there
# for full documentation, and latest versions.
#
#     Copyright 2002 Danny O'Brien <danny@spesh.com>
# 
#     This program is free software; you can redistribute it and/or modify
#     it under the terms of the GNU General Public License as published by
#     the Free Software Foundation; either version 2 of the License, or
#     (at your option) any later version.
# 
#     This program is distributed in the hope that it will be useful,
#     but WITHOUT ANY WARRANTY; without even the implied warranty of
#     MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#     GNU General Public License for more details.
# 
#     You should be able to view the GNU General Public License at
#     http://www.gnu.org/copyleft/gpl.html ; if not, write to the Free
#     Software Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA
#     02111-1307  USA
#
#     "One person gains one
#     dollar by destroying two
#     dollars' worth of wealth."

from __future__ import generators
import sys, os, re, fileinput, getopt

def get_sy(word):
    """Return of syllables in word/syllable tuple"""
    return word[1]

def get_word(word):
    """Return word text from word/syllable tuple"""
    return word[0]
    
sy_dict = {}
def get_sy_count(word):
    """Return the number of syllables in word, 0 if word not recognised """
    uword = re.sub('[^A-Z\']','',word.upper())
    if (uword == ''): return 0
    if uword in sy_dict: return sy_dict[uword] # memoize
    if cmudict:
        cdu = re.split(r'\s+', os.popen('/bin/egrep "^%s " %s' % (uword,cmudict)).readline(), 1)
        if (cdu[0] != uword):
            sy_count = 0
        else:
            sy_count = len(re.findall("\d+", cdu[1]))
        if sy_count == 0 and (not '-p' in options):
            sy_count = guess_sy_count(word)
    else:
        sy_count = guess_sy_count(word)
    sy_dict[uword] = sy_count
    return sy_count
    

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

def guess_sy_count(word):
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

def generate_sy_file():
    """Return a generator that iterates through file, returning word and
    syllable count tuples"""
    text = fileinput.input()
    while 1:
        l = text.readline()
        if not l: break
        w = re.split(r'\s+',l)
        for word in w:
            sy = get_sy_count(word)
            if (sy == 0):
                continue 
            yield (word,sy)
    return


def generate_window(file_iterator, window):
    """Return a generator that iterates from the start of the current file
    window, onward until the end of the file, loading from the file
    iterator when necessary"""
    window_index=-1
    while 1:
        window_index+=1
        try:
            yield window[window_index]
        except IndexError:
            window.append(file_iterator.next())
            yield window[window_index]

def pp_haiku(list):
    """Pretty-print a list made up lists of lists of word syllable pairs as a
    human-readable verse. Refuses to print verses that don't reach the high
    standards of either the -c or -s options"""
    # does it end with a full stop? Did we *want* it to end with a fullstop?
    if ('-s' in options and not get_word(list[-1][-1])[-1] == '.'):
        return
    if ('-c' in options and not re.match('[A-Z]',get_word(list[0][0])[0])):
        print "this shouldn't happen"
        return
    for a in list:
        for b in a:
            print get_word(b),
        print 
    print

trycmu = ['/usr/local/share/c06d', '/usr/share/dict/c06d', 'c06d' ]
version = 0.05

prog_name = re.sub(".*/", "", sys.argv[0])
usage = """haiku %s
usage: %s [ -c ] [ -s ] [ -p ] [ -h ] [ -d filename ] file...

Finds 5-7-5 syllable constructs in text files. Needs the %s file from
http://www.speech.cs.cmu.edu/cgi-bin/cmudict

-c  List only verses that begin with a capital letter
-s  List only verses that end with a fullstop
-p  Be precise: don't try and guess syllable count of unknown words
-d  Specify filename of %s dictionary
""" % (version, prog_name, trycmu[-1], trycmu[-1])

try:
   opts, newargv = getopt.getopt(sys.argv[1:], 'chspd:', ['help'])
except getopt.GetoptError:
   print usage
   raise SystemExit
sys.argv=sys.argv[0:1] + newargv
options={}
for (a,b) in opts:
    options[a]=b

if ('-h' in options or '--help' in options):
    print usage
    raise SystemExit

if ('-d' in options):
    trycmu= [ options['-d'] ] 

cmudict=''
for i in trycmu:
    if (os.path.exists(i)):
        cmudict = i
        break
if (cmudict == ''):
    print >> sys.stderr,  'Could not find %s the Carnegie Mellon Pronunciation Dictionary' % trycmu[-1]
    print >> sys.stderr,  'Will try and guess syllable counts instead. No guarantees!'

haiku_form = ( 5, 7, 5 )

sy_file = generate_sy_file() # iterator for walking through file
window = []                  # window into file


while 1: # do a verse 
    full_haiku = []              # verse composed so far
    form_iter = iter(haiku_form) # iter for walking through verse template 
    window_iter = generate_window(sy_file, window) # iter for file window
    if ('-c' in options):
        check_case = 1
    else:
        check_case =0

    sy_max = form_iter.next()
    while 1: # build a line
        haiku_line = []
        sy_count = 0
        while (sy_count < sy_max): # suck up enough syllables
            try:
                new_sy = window_iter.next()
            except StopIteration: # run out of file?
                raise SystemExit  # then finish
            if check_case:
                if (re.match('[^A-Z]',get_word(new_sy))):
                    break
                check_case = 0
            sy_count = sy_count + get_sy(new_sy)
            haiku_line.append(new_sy)

        if (sy_count == sy_max):   # have line?
            full_haiku.append(haiku_line)
            try:
                sy_max = form_iter.next()
            except StopIteration:
                pass 
            else:
                continue
            # we're at the end of the haiku
            pp_haiku(full_haiku) 
        # haiku completed or aborted, let's
        # backtrack to beginning, but start with next word in file
        window.pop(0)
        break
