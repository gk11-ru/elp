#!/bin/sh

#asciidoc --theme=flask -b docbook45 -a newline='\n' obsde_$1.adoc
#asciidoc --theme=flask -b html -a newline='\n' -a toc obsde_$1.adoc
#dblatex -b xetex -t pdf -P latex.output.revhistory=0 -p "/etc/asciidoc/dblatex/asciidoc-dblatex.xsl" -s "/etc/asciidoc/dblatex/asciidoc-dblatex.sty" obsde_$1.xml

asciidoc --theme=flask -b html -a newline='\n' -a disable-javascript doc.adoc
