#!/usr/bin/env python3

from pyparsing import Word, Literal, alphas, alphanums, nums, ParseException
from pyparsing import Suppress, QuotedString, oneOf, stringEnd

# A subset of the C primitive types:
type = Literal("float")|Literal("double")|Literal("int")|Literal("unsigned")
# We could also write this as:
type = oneOf(["float", "double", "int", "unsigned"])

# Rules for identifiers in C
identifier=Word(alphas, alphanums+'_')

# The assignment statement is '=' in C (sigh . . .)
assignment=Literal("=")

# Match a character representation of a real number:
number=Word(nums+".")

# End of statement:
eos=Literal(";")

# A C assignment statement is a type, identifier, '=', number or identifier, and then a semicolon.
c_assignment=type + identifier + assignment + (number|identifier) + eos

# Note that this could be parsed with str.split() and then some further manipulations.
parse_result = c_assignment.parseString('double x = 7;')

# prints:
# ['double', 'x', '=', '7', ';']
print(parse_result)

# But using regexes get awkward for free format languages like C.
# Your str.split() would choke here:
parse_result = c_assignment.parseString(' double x=7; ')

# prints:
# ['double', 'x', '=', '7', ';']
print(parse_result)

# What happens when we try to parse a python assignment with our C parser?

try:
    parse_result = c_assignment.parseString('x=7')
except ParseException as e:
    # Will print:
    # Expected {"float" | "double" | "int" | "unsigned"} (at char 0), (line:1, col:1)
    print(e)


# We allow the rhs to be a number or another identifier, so this'll parse:
parse_result = c_assignment.parseString('double x= y;')


# We're so far from an honest-to-God C parser:
try:
    # This is valid c:
    valid_c = 'double x = 7, y = 9;'
    parse_result = c_assignment.parseString(valid_c)
except ParseException as e:
    # Will print:
    # Expected ";" (at char 12), (line:1, col:13)
    print(e)


# Explicitly tokenize the lexemes by use of 'setResultsName'!
c_assignment = type.setResultsName("type") + identifier.setResultsName("new_identifier") + assignment
c_assignment += (number|identifier).setResultsName("rhs") + eos
parse_result = c_assignment.parseString("double x = 7;")
# Will print 'double'
print(parse_result.type)

# Will print 'x':
print(parse_result.new_identifier)

# Will print '7':
print(parse_result.rhs)


# Suppress characters your don't care about with 'Suppress':

assignment = Suppress(Literal("="))
eos = Suppress(Literal(";"))
cstatement=type + identifier + assignment + (number|identifier) + eos
t, id, rhs = cstatement.parseString("double x = 7;")

# Will print 'double'
print(t)

# Will print 'x'
print(id)

# Will print '7'
print(rhs)

# Parse a C string assignment with nested double quotes:
type_specifier = Literal("char*")
identifier = Word(alphas, alphanums+"_")
assignment = Suppress(Literal("="))
# Let C-strings have double quotes in them if they are properly escaped:
string = QuotedString('"', escChar='\\')
eos = Suppress(Literal(";"))
cstringdef = type_specifier + identifier + assignment + string + eos
s = r'''char* s="he said \"hello friend!\"";'''
keyword, id, string = cstringdef.parseString(s)

# Will print 'char*'
print(keyword)

# Will print 's'
print(id)

# Will print 'he said "hello friend!"'
print(string)


'''
Defining parse actions (passing callbacks to the parser)
'''

# The parse action is to convert the number to a float when it is found.
number = Word(nums+'.').setParseAction(lambda t:float(t[0]))
cstatement= type + identifier + assignment + (number|identifier) + eos
t, id, rhs = cstatement.parseString("double x = 3.14;")

# Will print 3.14 and 6.28:
# rhs is now the proper type.
print(rhs)
print(rhs*2.0)


'''
Debugging: If we use setResultsName, then we have key/value access to the parse results,
via dump(), items(), keys().
'''


type = oneOf(["float", "double", "int", "unsigned"]).setResultsName("type")
identifier=Word(alphas, alphanums+'_').setResultsName("identifier")
number = Word(nums+'.').setParseAction(lambda t:float(t[0])).setResultsName("number")
cstatement= type + identifier + assignment + (number|identifier) + eos
parse_result = cstatement.parseString("double x = 3.14;")


'''
Will print:
- identifier: 'x'
- number: 3.14
- type: 'double'
'''
print(parse_result.dump())


# But uh-oh: Random garbage shouldn't parse!
parse_result = cstatement.parseString("double x = 3.14; random syntactically incorrect garbage")


try:
    parse_result = (cstatement + stringEnd).parseString("double x = 3.14; random garbage")
except ParseException as e:
    # Will print:
    # pyparsing.ParseException: Expected stringEnd (at char 17), (line:1, col:18)
    print(e)
