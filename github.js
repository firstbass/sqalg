var tree_num = 0;
var tree;
var page = require('webpage').create(),
    system = require('system'),
    fs = require('fs'),
    tree_string, name;

if (system.args.length != 2)
{
  console.log('__LENGTH__' + system.args.length);
  console.log('MUST HAVE ONLY NAME ARGUMENT');
  console.log(system.args);
  phantom.exit(1);
}
else
{
  name = system.args[1];
}
// page information
page.viewportSize = { width: 800, height: 700 };
page.clipRect = { top: 0, left: 0, width: 800, height: 700 };

tree_string = '';
file = 'data.json';
if (fs.exists(file))
{
  console.log('"'+file+'" exists.');
  tree_string = fs.read(file);
}
else
{
  console.log('"'+file+'" doesn\'t exist.');
  console.log('error');
  phantom.exit(1);
}

// Parse JSON string into object
tree = JSON.parse(tree_string);

page.onConsoleMessage = function(msg, lineNum, sourceId) {
  console.log('__CONSOLE__: ' + msg);
}

page.onError = function(msg, trace) {

  var msgStack = ['ERROR: ' + msg];

  if (trace && trace.length) {
    msgStack.push('TRACE:');
    trace.forEach(function(t) {
      msgStack.push(' -> ' + t.file + ': ' + t.line + (t.function ? ' (in function "' + t.function +'")' : ''));
    });
  }

  console.error(msgStack.join('\n'));

};


page.open('trees2.html', function ( ) {
  page.evaluate(function (t) {
    processTree(t);
    PrintTree(cxt,t);
  }, tree);
  page.render(name + '.png');
  page.close();
  phantom.exit(0);
});