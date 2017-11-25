%from api import echolist
<div class="top-bar">
<div class="top-bar-left">
<ul class="dropdown menu" data-dropdown-menu>
<li class="menu-text">{{title}}</li>

        <li><a href="/user/me" title="{{u.uname}}"><i class="fa fa-fw fa-{{'user-circle-o' if u.uname else 'key'}}"></i></a></li>
%if ea:
        <li><a href="/new/{{now}}/{{ea}}/-/-" title="Написать новое сообщение в эту коференцию/форум">
                <i class="fa fa-plus-circle"></i> Новое</a>
            </li>
%end

            <li><a href="/start"><i class="fa fa-home"></i></a></li>
%if ea:
            <li><a href="/blog/{{ea}}">Блог</a></li>
%if now != 'echo':
            <li><a href="/echo/{{ea}}">Эха</a></li>
%end
%if now != 'forum':
            <li><a href="/forum/{{ea}}">Форум</a></li>
%end
<!--            <li><a href="/lenta">Лента</a></li> -->
%end


</ul>
</div>
<div class="top-bar-right">
<ul class="menu">
%for n in echolist():
%if n == ea:
<li><b><a href="/{{now}}/{{n}}">{{n}}</a></b></li>
%else:
<li><a href="/{{now}}/{{n}}">{{n}}</a></li>
%end
%end
</ul>
</div>
</div>
</div>
