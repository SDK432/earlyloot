// Live countdowns. Targets local midnight of the given YYYY-MM-DD in the visitor's time zone.
(function(){
  function target(s){var p=s.split('-');return new Date(+p[0],p[1]-1,+p[2]).getTime();}
  function parts(ms){var s=Math.floor(ms/1000);return [Math.floor(s/86400),Math.floor(s%86400/3600),Math.floor(s%3600/60),s%60];}
  function pad(n){return n<10?'0'+n:''+n;}
  var els=[].slice.call(document.querySelectorAll('[data-countdown]'));
  function tick(){
    var now=Date.now();
    els.forEach(function(el){
      var t=target(el.getAttribute('data-countdown')), diff=t-now, live=diff<=0&&diff>-86400000;
      if(el.hasAttribute('data-clock')){
        var b=el.querySelectorAll('b');
        if(diff<=0){el.classList.add('out');el.innerHTML='<div class="outnow">'+(live?'Out today!':'Out now')+'</div>';return;}
        var p=parts(diff);b[0].textContent=p[0];b[1].textContent=pad(p[1]);b[2].textContent=pad(p[2]);b[3].textContent=pad(p[3]);
      } else {
        var p2=parts(Math.max(diff,0));
        el.textContent = diff<=0 ? (live?'Out today':'Out now') : (p2[0]>0 ? 'in '+p2[0]+'d '+p2[1]+'h' : 'in '+p2[1]+'h '+p2[2]+'m');
        el.classList.toggle('done',diff<=0);
      }
    });
    var next=null;
    document.querySelectorAll('.cal li').forEach(function(li){
      var t=target(li.getAttribute('data-date'));li.classList.remove('now');
      li.classList.toggle('past',t+86400000<now);
      if(!next&&t+86400000>=now) next=li;
    });
    if(next) next.classList.add('now');
  }
  tick(); setInterval(tick,1000);
})();
