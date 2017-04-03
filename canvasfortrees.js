
// Missouri S&T's branding pallete of colors
var STCOLOR = {
  LIMA:           '#78be20',
  APPLE:          '#509e2f',
  MINERGREEN:     '#007a33',
  CANDLELIGHT:    '#fdda24',
  ORIENT:         '#005f83',
  PESTO:          '#7d622e',
  TANGO:          '#e87722',
  LIGHTTURQUOISE: '#b1e4e3',
  SCOOTER:        '#2dccd3',
  CYPRUS:         '#003b49',
  SHUTTLEGRAY:    '#63666a',
  GOLD:           '#daaa00',
  SILVER:         '#dce3e4',
  BLACK:          '#000000',
  WHITE:          '#ffffff'
};

// unicode dictionary for greek and special symbols required for trees
var GREEK = {
  UPPER_PI:   '\u03a0',
  LOWER_PI:   '\u03c0',
  LOWER_RHO:  '\u03C1',
  LOWER_SIGMA:'\u03C3',
  BOWTIE:     '\u22c8',
}

// canvas is the canvas object in the HTML page that we will be drawing on
var canvas = document.getElementById('main_canvas');

// the context makes it so we can perform operations on the canvas
var cxt = canvas.getContext('2d');

// obtain the origin of the canvas (useful for centering operations)
canvas.width = window.innerWidth //* 2;
canvas.height = window.innerHeight //* 2;
var CENTER_X = canvas.width / 2;
var CENTER_Y = canvas.height / 2;

var MARGIN = 10; //min pixels between objects

var TEXT_COLOR = STCOLOR.WHITE;
var CIRCLE_COLOR = STCOLOR.CYPRUS;
var LEAF_COLOR = STCOLOR.TANGO;
var CXN_COLOR = STCOLOR.SHUTTLEGRAY;


var FONT = 'Orgon Slab';
var FONT_SIZE = '20px';
var SUB_SIZE = '10px';
var BOX_HEIGHT = 30;

// draw a circle on the canvas
// (x, y): center of the circle
// r:      circle radius
// override: allow to occupy an allocated area
function createCircle(context, x, y, r, override)
{
  // the region that will be allocated on canvas for the object
  var reg = Region(x-r, y-r, x+r, y+r, MARGIN);

  // check if the region on the canvas collides with previously
  // allocated areas
  if (!override && !is_available(reg)) 
  {
    console.error('Circle to draw collided with allocated area');
    return false;
  }

  // if not, draw the circle
  context.beginPath();
  context.arc(x, y, r, 0, 2*Math.PI, false);
  context.fillStyle = CIRCLE_COLOR;
  context.fill();
  context.closePath();
  
  // mark the area as allocated
  occupy(reg);
  return true;
};

// draw a line to connect two points
// (startx,starty): starting point on canvas
// (endx, endy):    ending point on canvas
function draw_cxn (context, startx, starty, endx, endy)
{
  // ensure we are drawing under objects not over them
  // for cleanliness
  context.globalCompositeOperation = 'destination-over';

  //draw the line
  context.beginPath();
  context.strokeStyle = CXN_COLOR;
  context.moveTo(startx, starty);
  context.lineTo(endx, endy);
  context.stroke();
  context.closePath();

  //return the globalCompositeOperation to default
  context.globalCompositeOperation = 'source-over';
}


// draw text on the canvas with or without a background
// pre: subscript preceding the normal text
// mid: normal text centered betwee pre and post
// post: subscript succeeding the normal text
// (x,y): the bounding center of the text (not necessarily where mid is placed)
// background: the color of the box drawn behind the text
// override: allow to occupy an allocated area
// text_color: the color of the text (if not default text color)
function createText(context, pre, mid, post, x, y, background, override, text_color)
{
  // calculate the pixel width of the subscript parts of the text
  context.font = SUB_SIZE + ' ' + FONT;
  var prewidth = context.measureText(pre).width;
  var postwidth = context.measureText(post).width;

  // calculate the pixel width of the normal part of the text
  context.font = FONT_SIZE + ' ' + FONT;
  var midwidth = context.measureText(mid).width;

  // find the total width of the text
  var totalwidth = prewidth + midwidth + postwidth;

  // find bounds of box in which text will reside on the canvas
  var leftbound = x - totalwidth/2;
  var rightbound = x + totalwidth/2;

  // the region that will be allocated on canvas for the object
  var region = Region (leftbound, y-BOX_HEIGHT/2, rightbound, y+BOX_HEIGHT/2, MARGIN);
  
  // check if the region on the canvas collides with previously
  // allocated areas
  if (!override && !is_available(region))
  {
    console.error('Text to draw collided with allocated area');
    return false;
  }

  // add a box around and behind the text or clear any 
  // lines to/from it in its box
  background = background || STCOLOR.WHITE;
  context.beginPath();
  context.fillStyle = background;
  context.fillRect(leftbound-MARGIN, y - BOX_HEIGHT / 2 - MARGIN, totalwidth + 2 * MARGIN, BOX_HEIGHT + 2 * MARGIN)
  context.closePath();

  // draw the subscript part of the text
  context.beginPath();
  context.fillStyle = text_color || TEXT_COLOR;
  context.font = SUB_SIZE + ' ' + FONT;
  context.textBaseline = 'hanging';
  context.textAlign = 'left';
  context.fillText(pre, leftbound, y);
  context.textAlign = 'right';
  context.fillText(post, rightbound, y);

  // draw the normal part of the text
  context.font = FONT_SIZE + ' ' + FONT;
  context.textAlign = 'left';
  context.textBaseline ='middle';
  context.fillText(mid, leftbound + prewidth, y);
  context.closePath();

  // mark the area as allocated
  occupy(region);

  // return the region in which the text was allocated
  return region;
}

function countNodes(node)
{
  var count = 1;
  node.children.forEach(function(self) {
    count += countNodes(self);
  });
  return count;
}

// returns the integer node depth of the tree
// node: tree of which to find the height
function treeDepth (node)
{
  var depth = 0;
  node.children.forEach(function (self) {
    depth = Math.max(depth, treeDepth(self));
  });
  return depth + 1;
}

// returns an array with canvas-coordinates from the coordinates
// created during the buchheim process for each node of the tree
function coordsToCanvas(x,y,num)
{
  console.log('________________________________190__________________________', x, y);
  var PADDING_X = 10 * MARGIN;
  var canvasX = (canvas.width - PADDING_X * 2) * (1.5*x/num) + PADDING_X;
  var canvasY = (y + 1) * 60;
  return [canvasX, canvasY];
}


// perform operations necessary to determine proper spatial relations
// between each node in the tree. The process used here can be attributed
// partially to Bill Mill and Christoph Buchheim whose algorithms produce
// aesthetically pleasing tree layouts built upon the groundwork laid by Knuth.
function processTree(tree)
{
  var queue = new Array();
  queue.push(tree);

  while (queue.length > 0)
  {
    // visit each node in level order
    var v = queue.shift();

    // set properties necessary for printing and processing the tree
    v['x'] = -1;
    v['thread'] = undefined;
    v['mod'] = 0;
    v['change'] = 0;
    v['shift'] = 0;
    v['ancestor'] = v;
    v['children'].forEach(function (self, i, arr) {
      // add properties related to parent
      self['parent'] = v;
      v['number'] = i + 1;
      
      // add each child of the node to be processed
      queue.push(self);
    });
  }

  return buchheim(tree);
}


function PrintTree(context, tree)
{
  var queue = new Array();
  size = countNodes(tree);
  queue.push(tree);
  while (queue.length > 0)
  {
    // visit each node in level order
    var v = queue.shift();

    // convert the processed (x,y) coordinates into canvas coordinates
    var canvasCoords = coordsToCanvas(v.x,v.y, size);
    v.x = canvasCoords[0];
    v.y = canvasCoords[1];

    // print the node
    var r = printNode(context, v, v.x, v.y);
    
    // print a connecting line to parent if possible
    if (tree != v)
    {
      draw_cxn(context, v.x, v.y, v.parent.x, v.parent.y);
    }

    //add each child of the node to be processed
    v.children.forEach(function (self) {
      queue.push(self);
    })
  }
  context.globalCompositeOperation = 'destination-over';
  context.beginPath();
  context.fillStyle = STCOLOR.WHITE;
  context.fillRect(0,0,CENTER_X * 2, CENTER_Y * 2);
  context.closePath();
  context.globalCompositeOperation = 'source-over';

}

function treeToLatex(tree) {

  var optext  = '';
  var return_text = '';
  if (tree.children.length == 0)
  {
    console.log(272);
    console.log(tree.text);
    return_text =  tree.text;
  }
  else if (tree.children.length == 1)
  {
    if (tree.type == 'alias')
    {
      console.log(279);
      console.log(tree.text);
      return_text = '\\rho_{' + tree['text'] + '}(' + treeToLatex(tree['children'][0]) + ')';
    }
    else
    {
      console.log(284);
      console.log(tree.text);
      optext = tree.text;
      optext = replacer(optext, 'SELECT_{', '\\sigma_{');
      optext = replacer(optext, 'PROJECT_{', '\\pi_{');
      optext = replacer(optext, 'RENAME_{', '\\rho_{');

      console.log(297);
      console.log(optext);

      return_text =  optext + '(' + treeToLatex(tree['children'][0]) + ')';
    }
  }
  else
  {
    optext = tree.text;
    optext = replacer(optext, 'CROSS', '\\times');
    optext = replacer(optext, 'NATURALJOIN', '\\bowtie');
    optext = replacer(optext, 'MINUS', '\\setdifference');
    optext = replacer(optext, 'DIVIDE', '\\division');
    optext = replacer(optext, 'INTERSECT', '\\cap');
    optext = replacer(optext, 'UNION', '\\cup');
      
    return_text =  '(' + treeToLatex(tree['children'][0]) + ') ' + optext + ' (' + treeToLatex(tree['children'][1]) + ')';
  }
  console.log('return text: ' + return_text);
  return return_text;
}

function replacer (str, to_rep, replacement) {
  var new_str = '';
  var match = str.indexOf(to_rep);
  if (match < 0)
  {
    //console.log(331, 'no match in ' + str + ' for ' + to_rep);
    new_str = str;
  }
  else
  {
    //console.log(336, 'found ' + to_rep + ' in ' + str);
    new_str = str.slice(0, match);
    new_str += replacement;
    new_str += str.slice(match + to_rep.length)
  }
  console.log(341, 'now ' + new_str);
  return new_str;
}