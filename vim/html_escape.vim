" This script binds <C-E>,<C-U> in Visual-Mode to do html escape/unescape
" for selected text block.

function! EscapeHtml()
python << EOF
import vim, cgi, traceback
encoding = vim.eval("&encoding")
escape = cgi.escape(vim.eval('@"').decode(encoding)).encode('ascii', 'xmlcharrefreplace')
vim.command("let @\" = '%s'" % escape.replace("'","''"))
EOF
    let s = @"
    let @" = ""
    return s
endfunction


function! UnEscapeHtml()
python << EOF
import vim, HTMLParser
encoding = vim.eval("&encoding")
unescape = HTMLParser.HTMLParser().unescape(vim.eval('@"').encode(encoding))
vim.command("let @\" = '%s'" % unescape.encode(encoding).replace("'","''"))
EOF
    let s = @"
    let @" = ""
    return s
endfunction

vmap <C-E> c<C-R>=EscapeHtml()<ESC><ESC>
vmap <C-U> c<C-R>=UnEscapeHtml()<ESC><ESC>
