#!/usr/bin/python
from jinja2 import Environment, FileSystemLoader, Template
import os.path
import glob
import subprocess
from itertools import groupby

base = os.path.dirname(__file__)
template_dir = os.path.join(base, "templates")
mkd_dir = os.path.join(base, "sections")
env = Environment(loader=FileSystemLoader(template_dir))

def main():
    tmp = env.get_template("index.html")
    print tmp.render({
        "sections" : sections(),
        "style" : "neon",
        "transition" : "horizontal-slide"
        })

def sections():
    paths = glob.glob("%s/*.mkd" % mkd_dir)

    markdowns = []
    for path in paths:
        # remove postfix
        basename = os.path.basename(path)
        toks = basename.replace(".mkd", "").split("_")
        name = toks[0]
        sub = "".join(toks[1:])
        content = open(path).read()
        p = subprocess.Popen("markdown", shell=True,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE)
        html, _ = p.communicate(content)
        markdowns.append((name, sub, content, html))

    markdowns.sort(key=lambda x: x[0])
    
    sections = []
    for k, g in groupby(markdowns, lambda x:x[0]):
        l = list(g)
        assert len(filter(lambda x: x[1].isdigit(), l)) == 1

        index = None
        main = None
        nested = {}

        for name, sub, _, html in l:
            if sub.isdigit():
                index = sub
                main = html
            else:
                nested[sub] = html

        section = { "id": name }
        if nested:
            tmp = env.from_string(main)
            section["content"] = tmp.render(nested)
        else:
            section["content"] = main

        sections.append((index, section))
       
    if sections:
        # Sort by lexical order, make inserting new slice easier.
        sections.sort(key=lambda x:x[0])
        return [s[1] for s in sections]

if __name__ == '__main__':
    main()
