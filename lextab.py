﻿# lextab.py. This file automatically created by PLY (version 3.2). Don't edit!
_tabversion   = '3.2'
_lextokens    = {'RESET': 1, 'SETPOWER': 1, 'LBRACKET': 1, 'FASTSEND': 1, 'MINUS': 1, 'RPAREN': 1, 'TO': 1, 'RD': 1, 'ERASE': 1, 'PLUS': 1, 'SETDP': 1, 'LOWBYTE': 1, 'SVL': 1, 'OFF': 1, 'RANDOM': 1, 'THATWAY': 1, 'ONFOR': 1, 'SERIAL': 1, 'SVR': 1, 'ON': 1, 'SEND': 1, 'THISWAY': 1, 'OUTPUT': 1, 'OR': 1, 'LOOP': 1, 'SENSOR8': 1, 'SENSOR1': 1, 'SENSOR3': 1, 'SENSOR2': 1, 'SENSOR5': 1, 'SENSOR4': 1, 'SENSOR7': 1, 'SENSOR6': 1, 'SWITCH8': 1, 'SWITCH3': 1, 'SWITCH2': 1, 'SWITCH1': 1, 'SWITCH7': 1, 'SWITCH6': 1, 'SWITCH5': 1, 'SWITCH4': 1, 'BRAKE': 1, 'HIGHBYTE': 1, 'REPEAT': 1, 'END': 1, 'DIVIDE': 1, 'EQUALS': 1, 'GREATERTHAN': 1, 'I2C_WRITE': 1, 'AND': 1, 'RECALL': 1, 'I2C_READ': 1, 'BEEP': 1, 'NOT': 1, 'LEDON': 1, 'STOP': 1, 'FOREVER': 1, 'WHILE': 1, 'I2C_STOP': 1, 'BSR': 1, 'IFELSE': 1, 'REPORTER': 1, 'PERCENT': 1, 'WAIT': 1, 'BSEND': 1, 'WAITUNTIL': 1, 'NEWIRQ': 1, 'PROCEDURENAME': 1, 'LESSTHAN': 1, 'SETSVH': 1, 'TIMERMS': 1, 'WHEN': 1, 'RECORD': 1, 'RESETDP': 1, 'MOTORATTENTION': 1, 'XOR': 1, 'SHOW': 1, 'BYTES': 1, 'TIMER': 1, 'TIMES': 1, 'LPAREN': 1, 'IF': 1, 'NUMBERLITERAL': 1, 'WHENOFF': 1, 'MAKE': 1, 'I2C_START': 1, 'RECEIVER': 1, 'LEDOFF': 1, 'RBRACKET': 1}
_lexreflags   = 0
_lexliterals  = ''
_lexstateinfo = {'INITIAL': 'inclusive'}
_lexstatere   = {'INITIAL': [('(?P<t_MOTORATTENTION>(([a-d])+),)|(?P<t_PROCEDURENAME>(([a-zA-Z_])(([a-zA-Z0-9_]))*))|(?P<t_REPORTER>:(([a-zA-Z_])(([a-zA-Z0-9_]))*))|(?P<t_RECEIVER>"(([a-zA-Z_])(([a-zA-Z0-9_]))*))|(?P<t_BYTES>0x(([0-9]))+)|(?P<t_NUMBERLITERAL>(([0-9]))+)|(?P<t_ID>[a-zA-Z_][a-zA-Z0-9_]*)|(?P<t_COMMENT>(\\;*(.|\\n)*?\\*;)|(\\;.*))|(?P<t_newline>\\n+)|(?P<t_ignore_COMMENTLINE>\\;.*)|(?P<t_RBRACKET>\\])|(?P<t_LBRACKET>\\[)|(?P<t_PLUS>\\+)|(?P<t_LESSTHAN>\\<)|(?P<t_LPAREN>\\()|(?P<t_GREATERTHAN>\\>)|(?P<t_TIMES>\\*)|(?P<t_PERCENT>\\%)|(?P<t_EQUALS>\\=)|(?P<t_RPAREN>\\))|(?P<t_DIVIDE>/)|(?P<t_MINUS>-)', [None, ('t_MOTORATTENTION', 'MOTORATTENTION'), None, None, ('t_PROCEDURENAME', 'PROCEDURENAME'), None, None, None, None, ('t_REPORTER', 'REPORTER'), None, None, None, None, ('t_RECEIVER', 'RECEIVER'), None, None, None, None, ('t_BYTES', 'BYTES'), None, None, ('t_NUMBERLITERAL', 'NUMBERLITERAL'), None, None, ('t_ID', 'ID'), ('t_COMMENT', 'COMMENT'), None, None, None, ('t_newline', 'newline'), (None, None), (None, 'RBRACKET'), (None, 'LBRACKET'), (None, 'PLUS'), (None, 'LESSTHAN'), (None, 'LPAREN'), (None, 'GREATERTHAN'), (None, 'TIMES'), (None, 'PERCENT'), (None, 'EQUALS'), (None, 'RPAREN'), (None, 'DIVIDE'), (None, 'MINUS')])]}
_lexstateignore = {'INITIAL': ' \t\n'}
_lexstateerrorf = {'INITIAL': 't_error'}
