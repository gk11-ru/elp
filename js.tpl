%from api import sx

document.write('<div class="{{rq.lstclass or 'elp elp-panel'}}">')
%for o in mo:
document.write('<div class="{{rq.itemclass or 'elp elp-msg'}}"><p>{{!sx.rend(o.txt.decode('utf-8'))}}</p></div>')
%end
document.write('</div>')
