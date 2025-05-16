// X Build Tool


lexer grammar XbtLexer;

tokens {BUILD_FILES, OUT_FILES}

RULE     : 'rule';
COMMAND  : 'cmd' ;

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
BANG   : '!'   ;


// Keywords
BUILD_FILES  : 'build_files'  -> type(BUILD_FILES);
OUT_FILES    : 'output_files' -> type(OUT_FILES);
HELPER_FILES : 'helper_files' ;
DOLLAR_AT    : '$@' -> type(OUT_FILES);
DOLLAR_CARROT: '$^' -> type(BUILD_FILES);

DOT    : '.';

ML_COMMENT : '/*' .*? '*/' ;
SHELL      : '$' WS+ .+? '\n' ;
VARIABLE   : '$'[a-zA-Z_\-]+ [a-zA-Z_\-]*;
IDENT   : [a-zA-Z_\-]+ [/a-zA-Z_\-]*;
PATH       : [a-zA-Z_\-/.]+ [/a-zA-Z_\-!?.]*;


WS         : [ \t\r] -> skip ;
NEW_LINE   : '\n' -> skip;
