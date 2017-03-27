/* The following code was adapted from that released by Bill Mill under 
   the WTFPL. It contains algorithms by Christoph Buchheim that enable
   printing n-ary trees evenly.
*/
function left(self)
{
  return self.thread || 
         self.children.length && self.children[0];
}

function right(self)
{
  return self.thread || 
         self.children.length && self.children[self.children.length - 1];
}

function left_brother(self)
{
  var n = false;
  if (self.hasOwnProperty('parent'))
  {
    for (var i = 0; i < self.parent.children.length; i++)
    {
      if (self.parent.children[i] == self) return n;
      else n = self.parent.children[i];
    }
  }
  return n;
}

function get_lmost_sibling(self)
{
  if (!self.hasOwnProperty('lmost_sibling') &&
      self.hasOwnProperty('parent') &&
      self != self.parent.children[0])
  {
    self.lmost_sibling = self.parent.children[0];
  }
  return self.lmost_sibling;
}

function buchheim(tree)
{
  var intermediate = firstwalk(tree);
  second_walk(intermediate);
  return intermediate;
}

function firstwalk(v, distance)
{
  distance = distance || 1;
  if (v.children.length == 0)
  {
      if (get_lmost_sibling(v))
        v.x = left_brother(v).x + distance;
      else
        v.x = 0;
  }
  else
  {
      var default_ancestor = v.children[0];
      v.children.forEach(function (self) {
        firstwalk(self);
        default_ancestor = apportion(self, default_ancestor, distance);
      });
      execute_shifts(v);
      var midpoint = (v.children[0].x + v.children[v.children.length - 1].x) / 2;

      var ell = v.children[0];
      var arr = v.children[v.children.length - 1];

      var w = left_brother(v);
      if (w)
      {
        v.x = w.x + distance;
        v.mod = v.x - midpoint;
      }    
      else
      {
        v.x = midpoint;
      }
    }
  return v;
}

function apportion(v, default_ancestor, distance)
{
  var w = left_brother(v);
  if (w)
  {
    var vir = v;
    var vor = v;
    var vil = w;
    var vol = get_lmost_sibling(v);
    var sir = v.mod;
    var sor = v.mod;
    var sil = vil.mod;
    var sol = vol.mod;

    while (right(vil) && left(vir))
    {
      vil = right(vil);
      vir = left(vir);
      vol = left(vol);
      vor = right(vor);
      vor.ancestor = v;

      var shift = (vil.x + sil) - (vir.x + sir) + distance;
      if (shift > 0)
      {
        var a = ancestor(vil, v, default_ancestor);
        move_subtree(a, v, shift);
        sir = sir + shift;
        sor = sor + shift;
      }
      sil += vil.mod;
      sir += vir.mod;
      sol += vol.mod;
      sor += vor.mod;
    }

    if (right(vil) && !right(vor))
    {
      vor.thread = right(vil);
      vor.mod += sil - sor;
    }
    else
    {
      if (left(vir) && !left(vol))
      {
        vol.thread = left(vir);
        vol.mod += sir - sol;
      }
      default_ancestor = v;
    }
  }
  return default_ancestor;
}

function move_subtree(wl, wr, shift)
{
  console.log(152, wl.x, wl.change, wr.x, wr.change);
  var subtrees = wr.number - wl.number;
  wr.change -= shift/subtrees;
  wr.shift += shift;
  wl.change += shift/subtrees;
  wr.x += shift;
  wr.mod += shift;
  console.log(159, wl.x, wl.change, wr.x, wr.change);
}

function execute_shifts(v)
{
  var shift = 0;
  var change = 0;
  for (var i = v.children.length - 1; i >= 0; i--)
  {
    var w = v.children[i];
    w.x += shift;
    w.mod += shift;
    change += w.change;
    shift += w.shift + change;
  }
}

function ancestor(vil, v, default_ancestor)
{
  if (v.parent.children.indexOf(vil.ancestor) != -1)
    return vil.ancestor;
  else
    return default_ancestor;
}

function secondwalk(v, m, depth)
{
  m = m || 0;
  depth = depth || 0;

  v.x += m;
  v.y = depth;

  v.children.forEach(function (self) {
    second_walk(self, m+v.mod, depth + 1);
  })
}