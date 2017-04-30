var tree_num = 0;
var tree;

// import PhantomJS modules
var page = require('webpage').create(),
    system = require('system'),
    fs = require('fs');

var tree_string = '',
    num;

var DATA_FILE_URL = 'data.json';
var LOG_FILE_URL = 'log.txt';

/* program should be run only as 'phantomjs.exe github.js "filename"' */
if ( system.args.length != 2 )
{
  console.error('Error: \'github.js\' was run with invalid number of args');
  phantom.exit(1);
}
else
{
  name = system.args[1];
}

/* viewportSize is the size of the headless browser/screenshot */
page.viewportSize = { width: 2000, height: 1000 };

/* clipRect is the size of the picture we clip from the browser */
page.clipRect = { top: 0, left: 0, width: 2000, height: 1000 };

/* determine whether or not the json data file we need exists. */
if ( !fs.exists(DATA_FILE_URL) )
{
  /* if not, exit */
  console.log('\'' + DATA_FILE_URL + '\' does not exist');
  phantom.exit(1); // end the program
}
else
{
  /* otherwise, obtain the json data */
  tree_string = fs.read(DATA_FILE_URL);
}

/* Parse JSON string into object */
tree = JSON.parse(tree_string);






function log_stuff ( msg )
{
  if ( !fs.exists(LOG_FILE_URL) )
  {
    fs.touch(LOG_FILE_URL);
  }
  fs.write(LOG_FILE_URL, fs.read(LOG_FILE_URL) + '' + msg + '\n', 'w')
}

page.onConsoleMessage = function ( msg, lineNum, sourceId )
{
  log_stuff('__CONSOLE__: ' + msg);
}

page.onError = function ( msg, trace )
{

  var msgStack = ['ERROR: ' + msg];

  if ( trace && trace.length )
  {
    msgStack.push('TRACE:');
    trace.forEach(function ( t ) {
      msgStack.push(' -> ' + t.file + ': ' + t.line + (t.function ? ' (in function "' + t.function +'")' : ''));
    });
  }

  console.error(msgStack.join('\n'));
};

page.onAlert = function (msg) {
  if (msg === "MathJax Done") {
    //console.log(page.content);
  } else if (msg === "MathJax Timeout") {
    console.log("Timed out waiting for MathJax");
  } else {console.log(msg)}
  page.render(name + '.png');
  page.close();
  phantom.exit(0);
}

page.open('trees2.html', function ( ) {
  page.evaluate(function (t) {
    t = processTree(t)
    PrintTree(cxt,t);
    var equation = document.getElementById('eq');
    var a = treeToLatex(t);
    equation.innerHTML += '$$' + a + '$$';
    equation.innerHTML += '\n\n' + a;
    MathJax.Hub.Queue(
      ["Typeset",MathJax.Hub],
      [alert,'MathJax Done']
    );
    setTimeout(function ( ) {alert("MathJax Timeout")},10000);
  }, tree);
});