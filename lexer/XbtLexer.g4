// X Build Tool


lexer grammar XbtLexer;

RULE : 'rule';

STRING : '"' .*? '"' ;

LBRACE : '{';
RBRACE : '}';
LPAR   : '(';
RPAR   : ')';
EQUAL  : '=';
SEMI   : ';';
COMMA  : ',';
COLON  : ':';
DCOLON : '::' ;

// Keywords
BUILD_FILES : 'build_files' ;
OUT_FILES   : 'output_files';
WATCH_FILES : 'watch_files' ;

DOT    : '.';
BANG_CARROT: '$^';

ML_COMMENT : '/*' .*? '*/' ;
SHELL      : '$' WS+ .+? '\n' ;
VARIABLE   : '$'[a-zA-Z_\-]+ [a-zA-Z_\-]*;
IDENT   : [a-zA-Z_\-]+ [/a-zA-Z_\-]*;
PATH       : [a-zA-Z_\-/.]+ [/a-zA-Z_\-!?.]*;

WS         : [ \t\r] -> skip ;
NEW_LINE   : '\n' -> skip;
