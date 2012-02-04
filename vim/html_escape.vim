" This script binds <C-E>,<C-U> in Visual-Mode to do html escape/unescape
" for selected text block.

function! EscapeHtml()
python << EOF
import vim, cgi
escape = cgi.escape(vim.eval('@"'))
vim.command('let @" = "%s"' % escape)
EOF
    let s = @"
    let @" = ""
    return s
endfunction


function! UnEscapeHtml()
python << EOF
import vim, HTMLParser
unescape = HTMLParser.HTMLParser().unescape(vim.eval('@"'))
vim.command('let @" = "%s"' % unescape)
EOF
    let s = @"
    let @" = ""
    return s
endfunction

vmap <C-E> c<C-R>=EscapeHtml()<ESC><ESC>
vmap <C-U> c<C-R>=UnEscapeHtml()<ESC><ESC>
