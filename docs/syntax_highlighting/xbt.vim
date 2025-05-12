"mkdir -p ~/.config/nvim/syntax && cp [this-file] [there]
"Open a *.lox file and run `:set syntax=lox"`


" syntax match Shell /\<\$\>/
syntax match XbtRule /\<[A-Z][a-z]*\>/
syntax match XbtString /".*"/
syntax region XbtComment start="/\*" end="\*/" contains=NONE
" \< means "start of a word"
" \ze means to match up to this point, but do not highlight
syntax keyword XbtKeyword rule build_files output_files watch_files

highlight link XbtRule Structure
highlight link XbtKeyword Keyword
highlight link XbtString String
highlight link XbtComment Comment
highlight link XbtMember @method
" highlight link Shell Keyword


" couldn't get these to work
syntax match XbtGlobalVar /[$][A-Z]+/

syntax match LoxFun /\<\w\+\>\ze\s*(/

