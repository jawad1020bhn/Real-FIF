window.__hfRafNoop = window.__hfRafNoop || function(){return 0;};
window.mojs = (function(){
  var NS = 'http://www.w3.org/2000/svg';
  function make(parent, tag, attrs){
    var el = document.createElementNS(NS, tag);
    for (var k in attrs) el.setAttribute(k, attrs[k]);
    return el;
  }
  function canvas(parent, w, h){
    var c = document.createElementNS(NS, 'svg');
    c.setAttribute('width', w); c.setAttribute('height', h);
    c.style.position='absolute'; c.style.inset='0'; c.style.width='100%'; c.style.height='100%';
    parent.appendChild(c); return c;
  }
  function Shape(opts){
    opts = opts || {}; this.parent = opts.parent || document.body;
    this.canvas = canvas(this.parent, 840, 520);
    this.el = make(this.canvas, 'circle', {cx:420, cy:260, r:10, fill:'transparent', stroke:'#F3D489', 'stroke-width':3});
    this.canvas.appendChild(this.el); this.setProgress(0);
  }
  Shape.prototype.setProgress = function(p){
    var r = 24 + 120 * p, a = 1 - 0.35 * p;
    this.el.setAttribute('r', r);
    this.el.setAttribute('stroke', p > 0.5 ? '#D9A84E' : '#F3D489');
    this.el.setAttribute('opacity', a);
  };
  function Burst(opts){
    opts = opts || {}; this.parent = opts.parent || document.body;
    var count = opts.count || 8; this.dots = [];
    this.canvas = canvas(this.parent, 840, 520);
    for (var i=0;i<count;i++){
      var el = make(this.canvas, 'circle', {cx:420, cy:260, r:12, fill:'#D9A84E', opacity:0.9});
      this.canvas.appendChild(el); this.dots.push(el);
    }
    this.setProgress(0);
  }
  Burst.prototype.setProgress = function(p){
    for (var i=0;i<this.dots.length;i++){
      var ang = 2 * Math.PI * i / this.dots.length;
      var rad = 20 + 170 * p;
      var el = this.dots[i];
      el.setAttribute('cx', 420 + Math.cos(ang) * rad);
      el.setAttribute('cy', 260 + Math.sin(ang) * rad);
      el.setAttribute('r', 6 + 10 * (1 - p));
      el.setAttribute('opacity', 0.35 + 0.65 * Math.sin(Math.PI * p));
      el.setAttribute('fill', i % 2 ? '#F3D489' : '#F5F5F7');
    }
  };
  return {Shape:Shape, Burst:Burst};
})();
