// occupied is an array of all allocated areas on the canvas
var occupied = new Array();

// Region is the data structure used to specify areas on the
// canvas.
// (x1,y1): the top left corner of data
// (x2,y2): the bottom right corner of data
// margin: the amount extra around the area to specify
function Region(x1, y1, x2, y2, margin)
{
  margin = margin || 0;
  return  {
           'x1': x1 - margin,
           'y1': y1 - margin,
           'x2': x2 + margin,
           'y2': y2 + margin
          };
}

// returns whether rega and regb share any space on the canvas
// rega: one region to check for collision in
// rebg: the other region to check for collision in
function do_regions_collide(rega, regb)
{
  return (rega.x1 < regb.x2 &&
     rega.x2 > regb.x1 &&
     rega.y1 < regb.y2 &&
     rega.y2 > regb.y1);
}

// claim a region as being occupied i.e. add the region to the occupied array
function occupy(region)
{
  occupied.push(region);
}


function is_available(region)
{
  var collision = occupied.some(function (self) {
    return do_regions_collide(region, self);
  });
  return !collision;
}

function printNode(context, node, x, y)
{

  var r;
  if (!node)
    console.log(51,'null node cant print');
  var arr = parseString(node.text);
  var pre = arr[0];
  var mid = arr[1];
  var post = arr[2];
  switch (node['type'])
  {
    case 'operator':
      r = createText(context, pre, mid, post, x, y, undefined, true, STCOLOR.ORIENT);
      break;
    case 'alias':
      r = createText(context, pre, mid, post, x, y, 'transparent', true);
      context.globalCompositeOperation =  'destination-over';
      createCircle(context, (r.x2+r.x1)/2, (r.y2+r.y1)/2, (r.x2-r.x1)/2+MARGIN, true);
      context.globalCompositeOperation = 'source-over';
      break;
    case 'table':
      r = createText(context, pre, mid, post, x, y, STCOLOR.ORIENT, true);
      // measure size of text
      //draw a rectangle
      // draw text on the rectangle
      break;
    default:
      console.log('error: invalid type');
  }
  //console.log(node.text);
  return r;
}

// takes a string of the format _{pre}mid_{post} and returns 
// strings pre, mid, post in an array
function parseString(str)
{
  var pre = '';
  var mid = str;
  var post = '';
  if (str.indexOf('_') == 0)
  {
    // has a prefix _{prefix}
    console.log(str, 'has a prefix');
    var first_brace_index = str.indexOf('\{');
    var last_brace_index = str.indexOf('\}');
    pre = str.slice(first_brace_index+1, last_brace_index);
    mid = mid.slice(last_brace_index + 1);
  }
  if (str.indexOf('}') == str.length - 1)
  {
    // has a suffix _{suffix}
    var first_brace_index = str.lastIndexOf('\{');
    var last_brace_index = str.lastIndexOf('\}');
    post = str.substring(first_brace_index+1, last_brace_index);
    mid = mid.substring(0, first_brace_index - 1);
  }

  return [pre, mid, post];
}

function convertLatexToUnicode(str)
{
  var dict = {

  }
}